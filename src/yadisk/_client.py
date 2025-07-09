# -*- coding: utf-8 -*-
# Copyright © 2025 Ivan Konovalov

# This file is part of a Python library yadisk.

# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, see <http://www.gnu.org/licenses/>.

from pathlib import PurePosixPath
import posixpath
import time
from urllib.parse import urlencode

from ._api import *

from .exceptions import (
    AsyncOperationFailedError, AsyncOperationPollingTimeoutError, ParentNotFoundError,
    PathNotFoundError, RetriableYaDiskError, UnauthorizedError,
    OperationNotFoundError, InvalidResponseError, WrongResourceTypeError
)

from .utils import auto_retry, CaseInsensitiveDict
from .objects import (
    SyncResourceLinkObject, SyncPublicResourceLinkObject,
    SyncTrashResourceObject, SyncFilesResourceListObject, SyncResourceObject,
    SyncLastUploadedResourceListObject, SyncOperationLinkObject,
    SyncPublicResourceObject, SyncPublicResourcesListObject, DiskInfoObject,
    TokenObject, TokenRevokeStatusObject, DeviceCodeObject, ResourceUploadLinkObject,
    PublicSettingsObject, PublicAvailableSettingsObject
)

from ._session import Session
from ._import_session import import_session

from . import settings

from typing import Any, Optional, Union, Literal
from ._typing_compat import Callable, Generator, Dict, List, Type
from .types import (
    OpenFileCallback, FileOrPath, FileOrPathDestination, OperationStatus, PublicSettings,
    SessionFactory, SessionName
)

from ._client_common import (
    _add_spoof_user_agent_header, _apply_default_args, _filter_request_kwargs,
    _read_file_as_generator, _set_authorization_header,
    _add_authorization_header, _validate_listdir_response,
    _validate_link_response, _validate_get_type_response
)

from ._common import remove_path_schema

__all__ = ["Client"]

ResourceType = Union[
    "SyncResourceObject",
    "SyncPublicResourceObject",
    "SyncTrashResourceObject"
]


def _exists(
    get_meta_function: Callable[..., ResourceType],
    /,
    *args,
    **kwargs
) -> bool:
    try:
        # We want to query the bare minimum number of fields, that's what
        # the fields parameter is for
        get_meta_function(*args, fields=["type"], **kwargs)

        return True
    except PathNotFoundError:
        return False


def _get_type(
    get_meta_function: Callable[..., ResourceType],
    /,
    *args,
    **kwargs
) -> str:
    return get_meta_function(
        *args,
        _then=_validate_get_type_response,
        fields=["type"],
        **kwargs
    ).type  # type: ignore[return-value]


def _listdir(
    get_meta_function: Callable[..., ResourceType],
    path: str,
    /,
    *,
    max_items: Optional[int] = None,
    **kwargs
) -> Generator[Any, None, None]:
    if kwargs.get("limit") is None:
        kwargs["limit"] = 500

    if kwargs.get("fields") is None:
        kwargs["fields"] = []

    kwargs["fields"] = ["embedded.items.%s" % (k,) for k in kwargs["fields"]]

    # Fields that are absolutely necessary
    NECESSARY_FIELDS = ["type",
                        "embedded",
                        "embedded.offset",
                        "embedded.limit",
                        "embedded.total",
                        "embedded.items"]

    kwargs["fields"].extend(NECESSARY_FIELDS)

    remaining_items = max_items

    if remaining_items is not None:
        # Do not query more items than necessary
        kwargs["limit"] = min(remaining_items, kwargs["limit"])

    result = get_meta_function(path, _then=_validate_listdir_response, **kwargs)

    if result.type == "file":
        raise WrongResourceTypeError("%r is a file" % (path,))

    yield from result.embedded.items[:remaining_items]  # type: ignore[union-attr,index]

    limit: int = result.embedded.limit  # type: ignore[assignment,union-attr]
    offset: int = result.embedded.offset  # type: ignore[assignment,union-attr]
    total: int = result.embedded.total  # type: ignore[assignment,union-attr]

    while offset + limit < total:
        if remaining_items is not None:
            remaining_items -= len(result.embedded.items)  # type: ignore[union-attr,arg-type]

            if remaining_items <= 0:
                break

            # Do not query more items than necessary
            kwargs["limit"] = min(remaining_items, kwargs["limit"])
        else:
            remaining_items = None

        offset += limit
        kwargs["offset"] = offset
        result = get_meta_function(path, _then=_validate_listdir_response, **kwargs)

        if result.type == "file":
            raise WrongResourceTypeError("%r is a file" % (path,))

        yield from result.embedded.items[:remaining_items]  # type: ignore[union-attr,index]

        limit = result.embedded.limit  # type: ignore[assignment,union-attr]
        total = result.embedded.total  # type: ignore[assignment,union-attr]


class Client:
    """
        Implements access to Yandex.Disk REST API (provides synchronous API).

        HTTP client implementation can be specified using the :code:`session`
        parameter. :any:`RequestsSession` is used by default. For other options,
        see :doc:`/api_reference/sessions`.

        Almost all methods of :any:`Client` (the ones that accept `**kwargs`)
        accept some additional arguments:

        * **n_retries** - `int`, maximum number of retries for a request
        * **retry_interval** - `float`, delay between retries (in seconds)
        * **headers** - `dict` or `None`, additional request headers
        * **timeout** - `tuple` (:code:`(<connect timeout>, <read timeout>)`) or
          `float` (specifies both connect and read timeout), request timeout
          (in seconds)

        Additional parameters, specific to a given HTTP client library can also
        be passed, see documentation for specific :any:`Session` subclasses
        (:doc:`/api_reference/sessions`).

        :param id: application ID
        :param secret: application secret password
        :param token: application token
        :param default_args: `dict` or `None`, default arguments for methods.
                             Can be used to set the default timeout, headers, etc.
        :param session: `None`, `str` or an instance of :any:`Session`.
                        If :code:`session` is a string, the appropriate session
                        class will be imported, it must be one of the
                        following values:

                          * :code:`"httpx"` - :any:`HTTPXSession`
                          * :code:`"pycurl"` - :any:`PycURLSession`
                          * :code:`"requests"` - :any:`RequestsSession`

        :param open_file: `None` or a function that opens a file for reading or
                          writing (:code:`open()` by default)
        :param session_factory: kept for compatibility, callable that returns an
                                instance of :any:`Session`

        :ivar id: `str`, application ID
        :ivar secret: `str`, application secret password
        :ivar token: `str`, application token
        :ivar default_args: `dict`, default arguments for methods. Can be used to
                            set the default timeout, headers, etc.
        :ivar session: current session (:any:`Session` instance)
        :ivar open_file: function that opens a file for reading or writing
                         (:code:`open()` by default)

        The following exceptions may be raised by most API requests:

        :raises RequestError: HTTP client raised an exception while making a request
        :raises BadRequestError: server returned HTTP code 400
        :raises FieldValidationError: request contains fields with invalid data
        :raises UnauthorizedError: server returned HTTP code 401
        :raises ForbiddenError: server returned HTTP code 403
        :raises NotAcceptableError: server returned HTTP code 406
        :raises ConflictError: server returned HTTP code 409
        :raises PayloadTooLargeError: server returned code 413
        :raises UnsupportedMediaError: server returned HTTP code 415
        :raises LockedError: server returned HTTP code 423
        :raises TooManyRequestsError: server returned HTTP code 429
        :raises InternalServerError: server returned HTTP code 500
        :raises BadGatewayError: server returned HTTP code 502
        :raises UnavailableError: server returned HTTP code 503
        :raises GatewayTimeoutError: server returned HTTP code 504
        :raises InsufficientStorageError: server returned HTTP code 509
        :raises UnknownYaDiskError: other unknown error
    """

    id: str
    secret: str
    token: str
    default_args: Dict[str, Any]
    session: Session
    open_file: OpenFileCallback

    synchronous = True

    def __init__(self,
                 id:     str = "",
                 secret: str = "",
                 token:  str = "",
                 *,
                 default_args:    Optional[Dict[str, Any]] = None,
                 session:         Optional[Union[Session, SessionName]] = None,
                 open_file:       Optional[OpenFileCallback] = None,
                 session_factory: Optional[SessionFactory] = None) -> None:
        self.id = id
        self.secret = secret
        self.token = ""

        self.default_args = {} if default_args is None else default_args

        if open_file is None:
            open_file = open

        self.open_file = open_file

        if session is None:
            if session_factory is not None:
                session = session_factory()
            else:
                try:
                    session = import_session("requests")()
                except ModuleNotFoundError as e:
                    if e.name == "requests":
                        raise ModuleNotFoundError(
                            "requests is not installed. Either install requests or provide a custom session",
                            name=e.name,
                            path=e.path) from e
                    else:
                        raise
        elif isinstance(session, str):
            session = import_session(session)()

        self.session = session
        self.token = token

    def __enter__(self):
        return self

    def __exit__(self, *args, **kwargs) -> None:
        self.close()

    def close(self) -> None:
        """
            Closes the session.
            Do not call this method while there are other active threads using this object.

            This method can also be called implicitly by using the `with`
            statement.
        """

        self.session.close()

    def _maybe_wait(
        self,
        request_class: Type[APIRequest],
        /,
        *args,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        **kwargs
    ) -> Any:
        request = request_class(self.session, *args, **kwargs)

        if wait:
            args_to_filter = (
                "permanently", "md5", "overwrite", "force_async", "fields"
            )

            for arg in args_to_filter:
                kwargs.pop(arg, None)

            def then(response: Optional[SyncOperationLinkObject]) -> Optional[SyncOperationLinkObject]:
                if not isinstance(response, SyncOperationLinkObject):
                    return response

                try:
                    response.wait(
                        poll_interval=poll_interval,
                        poll_timeout=poll_timeout,
                        **kwargs
                    )
                except RetriableYaDiskError as e:
                    # We want to trigger a full retry (including the operation iteslf)
                    # only if the asynchronous operation failed
                    if not isinstance(e, AsyncOperationFailedError):
                        e.disable_retry = True
                    else:
                        settings.logger.info("asynchronous operation failed, attempting to restart it")

                    raise e from None

                return response

            return request.send(yadisk=self, then=then)
        else:
            return request.send(yadisk=self)

    def get_auth_url(
        self,
        type:                  Union[Literal["code"], Literal["token"]],
        device_id:             Optional[str] = None,
        device_name:           Optional[str] = None,
        redirect_uri:          Optional[str] = None,
        login_hint:            Optional[str] = None,
        scope:                 Optional[str] = None,
        optional_scope:        Optional[str] = None,
        force_confirm:         bool = True,
        state:                 Optional[str] = None,
        code_challenge:        Optional[str] = None,
        code_challenge_method: Optional[Union[Literal["plain"], Literal["S256"]]] = None,
        display:               None = None
    ) -> str:
        """
            Get authentication URL for the user to go to.
            This method doesn't send any HTTP requests and merely constructs the URL.

            :param type: response type ("code" to get the confirmation code or "token" to get the token automatically)
            :param device_id: unique device ID, must be between 6 and 50 characters
            :param device_name: device name, should not be longer than 100 characters
            :param redirect_uri: the URL to redirect the user to after they allow access to the app,
                                 by default, the first redirect URI specified in the app settings
                                 is used
            :param display: doesn't do anything, kept for compatibility
            :param login_hint: username or email for the account the token is being requested for
            :param scope: `str`, list of permissions for the application
            :param optional_scope: `str`, list of optional permissions for the application
            :param force_confirm: if True, user will be required to confirm access to the account
                                  even if the user has already granted access for the application
            :param state: The state string, which Yandex.OAuth returns without any changes (<= 1024 characters)
            :param code_challenge: string derived from the generated :code:`code_verifier` value
                                   using one of the two possible transformations (plain or S256)
            :param code_challenge_method: specifies what function was used to transform
                                          the :code:`code_verifier` value to :code:`code_challenge`,
                                          allowed values are :code:`"plain"` and :code:`"S256"` (recommended).
                                          If :code:`"S256"` is used, :code:`code_challenge` must be produced
                                          by hashing the :code:`code_verifier` value and encoding it to base64

            :raises ValueError: invalid arguments were passed

            :returns: authentication URL
        """

        if type not in ("code", "token"):
            raise ValueError("type must be either 'code' or 'token'")

        if code_challenge_method not in (None, "plain", "S256"):
            raise ValueError("code_challenge_method must be either 'plain' or 'S256'")

        params = {"response_type": type,
                  "client_id":     self.id,
                  "force_confirm": "yes" if force_confirm else "no"}

        if device_id is not None:
            params["device_id"] = device_id

        if device_name is not None:
            params["device_name"] = device_name

        if redirect_uri is not None:
            params["redirect_uri"] = redirect_uri

        if login_hint is not None:
            params["login_hint"] = login_hint

        if scope is not None:
            params["scope"] = " ".join(scope)

        if optional_scope is not None:
            params["optional_scope"] = " ".join(optional_scope)

        if state is not None:
            params["state"] = state

        if code_challenge is not None:
            params["code_challenge"] = code_challenge

        if code_challenge_method is not None:
            params["code_challenge_method"] = code_challenge_method

        return "https://oauth.yandex.ru/authorize?" + urlencode(params)

    def get_code_url(
        self,
        device_id:             Optional[str] = None,
        device_name:           Optional[str] = None,
        redirect_uri:          Optional[str] = None,
        login_hint:            Optional[str] = None,
        scope:                 Optional[str] = None,
        optional_scope:        Optional[str] = None,
        force_confirm:         bool = True,
        state:                 Optional[str] = None,
        code_challenge:        Optional[str] = None,
        code_challenge_method: Optional[Union[Literal["plain"], Literal["S256"]]] = None,
        display:               None = None
    ) -> str:
        """
            Get the URL for the user to get the confirmation code.
            The confirmation code can later be used to get the token.
            This method doesn't send any HTTP requests and merely constructs the URL.

            :param device_id: unique device ID, must be between 6 and 50 characters
            :param device_name: device name, should not be longer than 100 characters
            :param redirect_uri: the URL to redirect the user to after they allow access to the app,
                                 by default, the first redirect URI specified in the app settings
                                 is used
            :param display: doesn't do anything, kept for compatibility
            :param login_hint: username or email for the account the token is being requested for
            :param scope: `str`, list of permissions for the application
            :param optional_scope: `str`, list of optional permissions for the application
            :param force_confirm: if True, user will be required to confirm access to the account
                                  even if the user has already granted access for the application
            :param state: The state string, which Yandex.OAuth returns without any changes (<= 1024 characters)
            :param code_challenge: string derived from the generated :code:`code_verifier` value
                                   using one of the two possible transformations (plain or S256)
            :param code_challenge_method: specifies what function was used to transform
                                          the :code:`code_verifier` value to :code:`code_challenge`,
                                          allowed values are :code:`"plain"` and :code:`"S256"` (recommended).
                                          If :code:`"S256"` is used, :code:`code_challenge` must be produced
                                          by hashing the :code:`code_verifier` value and encoding it to base64

            :raises ValueError: invalid arguments were passed

            :returns: authentication URL
        """

        return self.get_auth_url(
            "code",
            device_id=device_id,
            device_name=device_name,
            redirect_uri=redirect_uri,
            display=display,
            login_hint=login_hint,
            scope=scope,
            optional_scope=optional_scope,
            force_confirm=force_confirm,
            state=state,
            code_challenge=code_challenge,
            code_challenge_method=code_challenge_method
        )

    def get_device_code(self, **kwargs) -> "DeviceCodeObject":
        """
            This request is used for authorization using the Yandex OAuth page.
            In this case the user must enter the verification code (:code:`user_code`)
            in the browser on the Yandex OAuth page.
            After the user has entered the code on the OAuth page, the application
            can exchange the :code:`device_code` for the token using the :any:`Client.get_token_from_device_code()`.

            :param device_id: unique device ID (between 6 and 50 characters)
            :param device_name: device name, should not be longer than 100 characters
            :param scope: `str`, list of permissions for the application
            :param optional_scope: `str`, list of optional permissions for the application
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises InvalidClientError: invalid client ID
            :raises BadRequestError: invalid request parameters

            :returns: :any:`DeviceCodeObject` containing :code:`user_code` and :code:`device_code`
        """

        _apply_default_args(kwargs, self.default_args)
        _set_authorization_header(kwargs, "")

        return GetDeviceCodeRequest(self.session, self.id, **kwargs).send(yadisk=self)

    def get_token(self, code: str, /, **kwargs) -> "TokenObject":
        """
            Get a new token.

            :param code: confirmation code
            :param device_id: unique device ID (between 6 and 50 characters)
            :param device_name: device name, should not be longer than 100 characters
            :param code_verifier: `str`, verifier code, used with the PKCE authorization flow
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises BadVerificationCodeError: confirmation code has invalid format
            :raises InvalidGrantError: invalid or expired confirmation code
            :raises InvalidClientError: invalid client ID or client secret
            :raises BadRequestError: invalid request parameters

            :returns: :any:`TokenObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _set_authorization_header(kwargs, "")

        return GetTokenRequest(
            self.session,
            "authorization_code",
            client_id=self.id,
            code=code,
            client_secret=self.secret,
            **kwargs
        ).send(yadisk=self)

    def get_token_from_device_code(self, device_code: str, /, **kwargs) -> "TokenObject":
        """
            Get a new token from a device code, previously obtained with :any:`Client.get_device_code()`.

            :param device_code: device code, obtained from :any:`Client.get_device_code()`
            :param device_id: unique device ID (between 6 and 50 characters)
            :param device_name: device name, should not be longer than 100 characters
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises AuthorizationPendingError: user has not authorized the application yet
            :raises BadVerificationCodeError: :code:`device_code` has invalid format
            :raises InvalidGrantError: invalid or expired :code:`device_code`
            :raises InvalidClientError: invalid client ID or client secret
            :raises BadRequestError: invalid request parameters

            :returns: :any:`TokenObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _set_authorization_header(kwargs, "")

        return GetTokenRequest(
            self.session,
            "device_code",
            client_id=self.id,
            code=device_code,
            client_secret=self.secret,
            **kwargs
        ).send(yadisk=self)

    def refresh_token(self, refresh_token: str, /, **kwargs) -> "TokenObject":
        """
            Refresh an existing token.

            :param refresh_token: the refresh token that was received with the token
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises InvalidGrantError: invalid or expired refresh token or it
                                       doesn't belong to this application
            :raises InvalidClientError: invalid client ID or client secret
            :raises BadRequestError: invalid request parameters

            :returns: :any:`TokenObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _set_authorization_header(kwargs, "")

        return RefreshTokenRequest(
            self.session,
            refresh_token,
            self.id,
            self.secret,
            **kwargs
        ).send(yadisk=self)

    def revoke_token(
        self,
        token: Optional[str] = None,
        /,
        **kwargs
    ) -> "TokenRevokeStatusObject":
        """
            Revoke the token.

            :param token: token to revoke
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises InvalidGrantError: specified token doesn't belong to this application
            :raises InvalidClientError: invalid client ID or client secret
            :raises UnsupportedTokenTypeError: token could not be revoked because
                                               it doesn't have a :code:`device_id`
            :raises BadRequestError: invalid request parameters

            :returns: :any:`TokenRevokeStatusObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _set_authorization_header(kwargs, "")

        if token is None:
            token = self.token

        return RevokeTokenRequest(
            self.session, token, self.id, self.secret, **kwargs
        ).send(yadisk=self)

    def check_token(self, token: Optional[str] = None, /, **kwargs) -> bool:
        """
            Check whether the token is valid.

            :param token: token to check, equivalent to `self.token` if `None`
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :returns: `bool`
        """

        # Any ID will do, doesn't matter whether it exists or not
        fake_operation_id = "0000"

        if token is None:
            token = self.token

        if not token:
            return False

        _set_authorization_header(kwargs, token)

        try:
            # get_operation_status() doesn't require any permissions, unlike most other requests
            self.get_operation_status(fake_operation_id, **kwargs)
            return True
        except OperationNotFoundError:
            return True
        except UnauthorizedError:
            return False

    def get_disk_info(self, **kwargs) -> "DiskInfoObject":
        """
            Get disk information.

            :param extra_fields: list of additional keys to be included in the response
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/capacity>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk/GetDisk>`__

            :returns: :any:`DiskInfoObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return DiskInfoRequest(self.session, **kwargs).send(yadisk=self)

    def get_meta(self, path: str, /, **kwargs) -> "SyncResourceObject":
        """
            Get meta information about a file/directory.

            :param path: path to the resource
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param sort: `str`, field to be used as a key to sort children resources
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/meta>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/GetResource>`__

            :returns: :any:`SyncResourceObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        # This is for internal error handling
        _then = kwargs.pop("_then", None)

        return GetMetaRequest(self.session, path, **kwargs).send(yadisk=self, then=_then)

    def exists(self, path: str, /, **kwargs) -> bool:
        """
            Check whether `path` exists.

            :param path: path to the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `bool`
        """

        return _exists(self.get_meta, path, **kwargs)

    def get_type(self, path: str, /, **kwargs) -> str:
        """
            Get resource type.

            :param path: path to the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: "file" or "dir"
        """

        return _get_type(self.get_meta, path, **kwargs)

    def is_file(self, path: str, /, **kwargs) -> bool:
        """
            Check whether `path` is a file.

            :param path: path to the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a file, `False` otherwise (even if it doesn't exist)
        """

        try:
            return self.get_type(path, **kwargs) == "file"
        except PathNotFoundError:
            return False

    def is_dir(self, path: str, /, **kwargs) -> bool:
        """
            Check whether `path` is a directory.

            :param path: path to the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
        """

        try:
            return self.get_type(path, **kwargs) == "dir"
        except PathNotFoundError:
            return False

    def listdir(self, path: str, /, **kwargs) -> Generator["SyncResourceObject", None, None]:
        """
            Get contents of `path`.

            :param path: path to the directory
            :param max_items: `int` or `None`, maximum number of returned items (`None` means unlimited)
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises WrongResourceTypeError: resource is not a directory

            :returns: generator of :any:`ResourceObject`
        """

        return _listdir(self.get_meta, path, **kwargs)

    def get_upload_link(
        self,
        path: str,
        /,
        spoof_user_agent: bool = True,
        **kwargs
    ) -> str:
        """
            Get a link to upload the file using the PUT request.

            :param path: destination path
            :param overwrite: `bool`, determines whether to overwrite the destination
            :param spoof_user_agent: `bool`, if `True` (default), the `User-Agent` header
                will be set to a special value, which should allow bypassing of
                Yandex.Disk's upload speed limit
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises InsufficientStorageError: cannot upload file due to lack of storage space
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/upload>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/GetResourceUploadLink>`__

            :returns: `str`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        # This is used to bypass Yandex.Disk's upload speed limit for some file types
        if spoof_user_agent:
            _add_spoof_user_agent_header(kwargs)

        return GetUploadLinkRequest(
            self.session, path, fields=["href"], **kwargs
        ).send(yadisk=self, then=_validate_link_response).href

    def get_upload_link_object(
        self,
        path: str,
        /,
        spoof_user_agent: bool = True,
        **kwargs
    ) -> ResourceUploadLinkObject:
        """
            Get a link to upload the file using the PUT request.
            This is similar to :any:`Client.get_upload_link()`, except it returns
            an instance of :any:`ResourceUploadLinkObject` which also contains
            an asynchronous operation ID.

            :param path: destination path
            :param overwrite: `bool`, determines whether to overwrite the destination
            :param fields: list of keys to be included in the response
            :param spoof_user_agent: `bool`, if `True` (default), the `User-Agent` header
                will be set to a special value, which should allow bypassing of
                Yandex.Disk's upload speed limit
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises InsufficientStorageError: cannot upload file due to lack of storage space
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded

            :returns: :any:`ResourceUploadLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        # This is used to bypass Yandex.Disk's upload speed limit for some file types
        if spoof_user_agent:
            _add_spoof_user_agent_header(kwargs)

        return GetUploadLinkRequest(
            self.session, path, **kwargs
        ).send(yadisk=self)

    def _upload(self,
                get_upload_link_function: Callable,
                file_or_path: FileOrPath,
                dst_path: str, /, **kwargs) -> None:
        timeout = kwargs.get("timeout", ...)

        if timeout is ...:
            timeout = settings.DEFAULT_UPLOAD_TIMEOUT

        retry_interval = kwargs.get("retry_interval")

        if retry_interval is None:
            retry_interval = settings.DEFAULT_UPLOAD_RETRY_INTERVAL

        n_retries = kwargs.get("n_retries")

        if n_retries is None:
            n_retries = settings.DEFAULT_N_RETRIES

        # Number of retries for getting the upload link.
        # It is set to 0, unless the file is not seekable, in which case
        # we have to use a different retry scheme
        n_retries_for_upload_link = 0

        kwargs["timeout"] = timeout

        # Make sure we don't get any inconsistent behavior with header names
        kwargs["headers"] = CaseInsensitiveDict(kwargs.get("headers") or {})

        file: Any = None
        close_file = False
        file_position = 0
        iterator_factory = None

        session = self.session

        try:
            if isinstance(file_or_path, (str, bytes)):
                close_file = True
                file = self.open_file(file_or_path, "rb")
            elif callable(file_or_path):
                close_file = False
                iterator_factory = file_or_path
            else:
                close_file = False
                file = file_or_path

            if file is not None and file.seekable():
                file_position = file.tell()
            elif iterator_factory is None:
                n_retries, n_retries_for_upload_link = 0, n_retries

            def attempt() -> None:
                temp_kwargs = dict(kwargs)
                temp_kwargs["n_retries"] = n_retries_for_upload_link
                temp_kwargs["retry_interval"] = 0.0

                link = get_upload_link_function(dst_path, **temp_kwargs)

                # session.put() doesn't accept some of the passed parameters
                _filter_request_kwargs(temp_kwargs)

                temp_kwargs.setdefault("stream", True)

                # Disable keep-alive by default, since the upload server is random
                temp_kwargs["headers"].setdefault("Connection", "close")

                # This is generally not necessary, libraries like aiohttp
                # will generally always set this header while others might not
                # We're setting content-type here just to fix this inconsistency,
                # this makes testing easier
                temp_kwargs["headers"].setdefault("Content-Type", "application/octet-stream")

                if iterator_factory is not None:
                    payload = iterator_factory()
                elif file.seekable():
                    file.seek(file_position)
                    payload = file
                else:
                    # requests will try to seek the file to determine the payload size
                    # regardless of whether it is seekable() or not.
                    # To bypass this problem we pass the file as a generator instead.
                    payload = _read_file_as_generator(file)

                settings.logger.info(f"uploading file to {dst_path} at {link}")

                with session.send_request("PUT", link, data=payload, **temp_kwargs) as response:
                    if response.status != 201:
                        raise response.get_exception()

            auto_retry(attempt, n_retries, retry_interval)
        finally:
            if close_file and file is not None:
                file.close()

    def upload(
        self,
        file_or_path: FileOrPath,
        dst_path: str,
        /,
        **kwargs
    ) -> SyncResourceLinkObject:
        """
            Upload a file to disk.

            :param file_or_path: path, file-like object to be uploaded or
                                 a function that returns an iterator (or generator)
            :param dst_path: destination path
            :param overwrite: if `True`, the resource will be overwritten if it already exists,
                              an error will be raised otherwise
            :param spoof_user_agent: `bool`, if `True` (default), the `User-Agent` header
                will be set to a special value, which should allow bypassing of
                Yandex.Disk's upload speed limit
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises PathExistsError: destination path already exists
            :raises InsufficientStorageError: cannot upload file due to lack of storage space
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded

            :returns: :any:`SyncResourceLinkObject`, link to the destination resource
        """

        _apply_default_args(kwargs, self.default_args)

        self._upload(self.get_upload_link, file_or_path, dst_path, **kwargs)

        return SyncResourceLinkObject.from_path(dst_path, yadisk=self)

    def upload_by_link(self,
                       file_or_path: FileOrPath,
                       link: str, /, **kwargs) -> None:
        """
            Upload a file to disk using an upload link.

            :param file_or_path: path, file-like object to be uploaded or
                                 a function that returns an iterator (or generator)
            :param link: upload link
            :param overwrite: if `True`, the resource will be overwritten if it already exists,
                              an error will be raised otherwise
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises InsufficientStorageError: cannot upload file due to lack of storage space
        """

        _apply_default_args(kwargs, self.default_args)

        self._upload(lambda *args, **kwargs: link, file_or_path, "", **kwargs)

    def get_download_link(self, path: str, /, **kwargs) -> str:
        """
            Get a download link for a file (or a directory).

            :param path: path to the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/content>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/GetResourceDownloadLink>`__

            :returns: `str`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return GetDownloadLinkRequest(
            self.session, path, fields=["href"], **kwargs
        ).send(yadisk=self, then=_validate_link_response).href

    def _download(
        self,
        get_download_link_function: Callable,
        src_path: str,
        file_or_path: FileOrPathDestination,
        /,
        **kwargs
    ) -> None:
        n_retries = kwargs.get("n_retries")

        if n_retries is None:
            n_retries = settings.DEFAULT_N_RETRIES

        # Number of retries for getting the download link.
        # It is set to 0, unless the file is not seekable, in which case
        # we have to use a different retry scheme
        n_retries_for_download_link = 0

        retry_interval = kwargs.get("retry_interval")

        if retry_interval is None:
            retry_interval = settings.DEFAULT_RETRY_INTERVAL

        timeout = kwargs.get("timeout", ...)

        if timeout is ...:
            timeout = settings.DEFAULT_TIMEOUT

        kwargs["timeout"] = timeout

        file: Any = None
        close_file = False
        file_position = 0

        session = self.session

        try:
            if isinstance(file_or_path, (str, bytes)):
                close_file = True
                file = self.open_file(file_or_path, "wb")
            else:
                close_file = False
                file = file_or_path

            if file.seekable():
                file_position = file.tell()
            else:
                n_retries, n_retries_for_download_link = 0, n_retries

            def attempt() -> None:
                temp_kwargs = dict(kwargs)
                temp_kwargs["n_retries"] = n_retries_for_download_link
                temp_kwargs["retry_interval"] = 0.0
                link = get_download_link_function(src_path, **temp_kwargs)

                # session.get() doesn't accept some of the passed parameters
                _filter_request_kwargs(temp_kwargs)

                temp_kwargs.setdefault("stream", True)

                if file.seekable():
                    file.seek(file_position)

                settings.logger.info(f"downloading file {src_path} from {link}")

                with session.send_request("GET", link, **temp_kwargs) as response:
                    # pycurl can't get status until the response is actually read
                    # in that case, status will be set to 0
                    if response.status == 0:
                        def consume(chunk: bytes) -> None:
                            if response.status not in (0, 200):
                                return

                            file.write(chunk)

                        response.download(consume)

                        if response.status != 200:
                            raise response.get_exception()
                    else:
                        if response.status != 200:
                            raise response.get_exception()

                        response.download(file.write)

            auto_retry(attempt, n_retries, retry_interval)
        finally:
            if close_file and file is not None:
                file.close()

    def download(
        self,
        src_path: str,
        file_or_path: FileOrPathDestination,
        /,
        **kwargs
    ) -> SyncResourceLinkObject:
        """
            Download the file.

            :param src_path: source path
            :param file_or_path: destination path or file-like object
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`SyncResourceLinkObject`, link to the source resource
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        self._download(self.get_download_link, src_path, file_or_path, **kwargs)

        return SyncResourceLinkObject.from_path(src_path, yadisk=self)

    def download_by_link(
        self,
        link: str,
        file_or_path: FileOrPathDestination,
        /,
        **kwargs
    ) -> None:
        """
            Download the file from the link.

            :param link: download link
            :param file_or_path: destination path or file-like object
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`
        """

        _apply_default_args(kwargs, self.default_args)

        self._download(lambda *args, **kwargs: link, "", file_or_path, **kwargs)

    def remove(self, path: str, /, **kwargs) -> Optional["SyncOperationLinkObject"]:
        """
            Remove the resource.

            :param path: path to the resource to be removed
            :param permanently: if `True`, the resource will be removed permanently,
                                otherwise, it will be just moved to the trash
            :param md5: `str`, MD5 hash of the file to remove
            :param force_async: forces the operation to be executed asynchronously
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises BadRequestError: MD5 check is only available for files
            :raises ResourceIsLockedError: resource is locked by another request
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/delete>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/DeleteResource>`__

            :returns: :any:`SyncOperationLinkObject` if the operation is performed asynchronously, `None` otherwise
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return self._maybe_wait(DeleteRequest, path, **kwargs)

    def mkdir(self, path: str, /, **kwargs) -> SyncResourceLinkObject:
        """
            Create a new directory.

            :param path: path to the directory to be created
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises DirectoryExistsError: destination path already exists
            :raises InsufficientStorageError: cannot create directory due to lack of storage space
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/create-folder>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/CreateResource>`__

            :returns: :any:`SyncResourceLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return MkdirRequest(self.session, path, **kwargs).send(yadisk=self)

    def makedirs(self, path: str, /, **kwargs) -> SyncResourceLinkObject:
        """
            Create a new directory at `path`. If its parent directory doesn't
            exist it will also be created recursively.

            :param path: path to the directory to be created
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises DirectoryExistsError: destination path already exists
            :raises InsufficientStorageError: cannot create directory due to lack of storage space
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`SyncResourceLinkObject`
        """

        while True:
            try:
                return self.mkdir(path, **kwargs)
            except ParentNotFoundError as e:
                # We first have to remove the schema, otherwise posixpath.split()
                # may treat it as part of the path
                schema, path_without_schema = remove_path_schema(path)

                # Extract the parent directory
                head, tail = posixpath.split(path_without_schema)
                head = head.strip("/")

                if head == "":
                    # We should never find ourselves in this situation
                    raise e from None

                # Restore the schema
                if schema:
                    head = f"{schema}:/{head}"

                self.makedirs(head, **kwargs)

    def get_trash_meta(self, path: str, /, **kwargs) -> "SyncTrashResourceObject":
        """
            Get meta information about a trash resource.

            :param path: path to the trash resource
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param sort: `str`, field to be used as a key to sort children resources
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/meta>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47trash47resources/GetTrashResource>`__

            :returns: :any:`SyncTrashResourceObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        # This is for internal error handling
        _then = kwargs.pop("_then", None)

        return GetTrashRequest(self.session, path, **kwargs).send(yadisk=self, then=_then)

    def trash_exists(self, path: str, /, **kwargs) -> bool:
        """
            Check whether the trash resource at `path` exists.

            :param path: path to the trash resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `bool`
        """

        return _exists(self.get_trash_meta, path, **kwargs)

    def copy(
        self,
        src_path: str,
        dst_path: str,
        /,
        **kwargs
    ) -> Union[SyncResourceLinkObject, "SyncOperationLinkObject"]:
        """
            Copy `src_path` to `dst_path`.
            If the operation is performed asynchronously, returns the link to the operation,
            otherwise, returns the link to the newly created resource.

            :param src_path: source path
            :param dst_path: destination path
            :param overwrite: if `True` the destination path can be overwritten,
                              otherwise, an error will be raised
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises InsufficientStorageError: cannot complete request due to lack of storage space
            :raises ResourceIsLockedError: resource is locked by another request
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/copy>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/CopyResource>`__

            :returns: :any:`SyncResourceLinkObject` or :any:`SyncOperationLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return self._maybe_wait(CopyRequest, src_path, dst_path, **kwargs)

    def restore_trash(
        self,
        path: str,
        /,
        dst_path: Optional[str] = None,
        **kwargs
    ) -> Union[SyncResourceLinkObject, "SyncOperationLinkObject"]:
        """
            Restore a trash resource.
            Returns a link to the newly created resource or a link to the asynchronous operation.

            :param path: path to the trash resource to be restored
            :param dst_path: destination path
            :param overwrite: `bool`, determines whether the destination can be overwritten
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/trash-restore>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47trash47resources/RestoreFromTrash>`__

            :returns: :any:`SyncResourceLinkObject` or :any:`SyncOperationLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return self._maybe_wait(RestoreTrashRequest, path, dst_path=dst_path, **kwargs)

    def move(
        self,
        src_path: str,
        dst_path: str,
        /,
        **kwargs
    ) -> Union[SyncResourceLinkObject, "SyncOperationLinkObject"]:
        """
            Move `src_path` to `dst_path`.

            :param src_path: source path to be moved
            :param dst_path: destination path
            :param overwrite: `bool`, determines whether to overwrite the destination
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/move>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/MoveResource>`__

            :returns: :any:`SyncResourceLinkObject` or :any:`SyncOperationLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return self._maybe_wait(MoveRequest, src_path, dst_path, **kwargs)

    def rename(
        self,
        src_path: str,
        new_name: str,
        /,
        **kwargs
    ) -> Union[SyncResourceLinkObject, "SyncOperationLinkObject"]:
        """
            Rename `src_path` to have filename `new_name`.
            Does the same as `move()` but changes only the filename.

            :param src_path: source path to be moved
            :param new_name: target filename to rename to
            :param overwrite: `bool`, determines whether to overwrite the destination
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises ValueError: `new_name` is not a valid filename or `src_path` is root
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            :returns: :any:`SyncResourceLinkObject` or :any:`SyncOperationLinkObject`
        """

        new_name = new_name.rstrip("/")

        if "/" in new_name or new_name in (".", "..", ""):
            raise ValueError(f"Invalid filename: {new_name}")

        # Remove schema first, otherwise PurePosixPath will treat it as part of the path
        schema, src_path_without_schema = remove_path_schema(src_path)
        sanitized_src_path = PurePosixPath(src_path_without_schema.strip("/"))

        if len(sanitized_src_path.parts) == 0:
            raise ValueError("Cannot rename root")

        dst_path = str(sanitized_src_path.parent / new_name)

        # Restore schema back
        if schema:
            dst_path = f"{schema}:/{dst_path}"

        return self.move(src_path, dst_path, **kwargs)

    def remove_trash(
        self,
        path: str,
        /,
        **kwargs
    ) -> Optional["SyncOperationLinkObject"]:
        """
            Remove a trash resource.

            :param path: path to the trash resource to be deleted
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/trash-delete>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47trash47resources/ClearTrash>`__

            :returns: :any:`SyncOperationLinkObject` if the operation is performed asynchronously, `None` otherwise
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return self._maybe_wait(DeleteTrashRequest, path, **kwargs)

    def publish(self, path: str, /, **kwargs) -> SyncResourceLinkObject:
        """
            Make a resource public.

            :param path: path to the resource to be published
            :param allow_address_access: `bool`, specifies the request format, i.e.
                with personal access settings (when set to `True`) or without
            :param public_settings: :any:`PublicSettings` or `None`, public access settings for the resource
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/publish>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/PublishResource>`__

            :returns: :any:`SyncResourceLinkObject`, link to the resource
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return PublishRequest(self.session, path, **kwargs).send(yadisk=self)

    def unpublish(self, path: str, /, **kwargs) -> SyncResourceLinkObject:
        """
            Make a public resource private.

            :param path: path to the resource to be unpublished
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/publish#unpublish-q>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/UnpublishResource>`__

            :returns: :any:`SyncResourceLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return UnpublishRequest(self.session, path, **kwargs).send(yadisk=self)

    def get_public_settings(self, path: str, /, **kwargs) -> PublicSettingsObject:
        """
            Get public settings of a resource.

            :param path: path to the resource
            :param allow_address_access: `bool`, specifies the request format, i.e.
                with personal access settings (when set to `True`) or without
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            More info about this request:

            * `Official docs <https://yandex.ru/dev/disk-api/doc/ru/reference/public-settings-get>`__

            :returns: :any:`PublicSettingsObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return GetPublicSettingsRequest(self.session, path, **kwargs).send(yadisk=self)

    def get_public_available_settings(self, path: str, /, **kwargs) -> PublicAvailableSettingsObject:
        """
            Get public settings of a shared resource for the current OAuth token owner.

            :param path: path to the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            More info about this request:

            * `Official docs <https://yandex.ru/dev/disk-api/doc/ru/reference/public-settings-get-available>`__

            :returns: :any:`PublicAvailableSettingsObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return GetPublicAvailableSettingsRequest(self.session, path, **kwargs).send(yadisk=self)

    def update_public_settings(self, path: str, public_settings: PublicSettings, /, **kwargs) -> None:
        """
            Update public settings of a shared resource.

            :param path: path to the resource
            :param public_settings: :any:`PublicSettings`, public access settings for the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            More info about this request:

            * `Official docs <https://yandex.ru/dev/disk-api/doc/ru/reference/public-settings-change>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47public47resources/UpdatePublicSettings>`__

            :returns: `None`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return UpdatePublicSettingsRequest(self.session, path, public_settings, **kwargs).send(yadisk=self)

    def save_to_disk(
        self,
        public_key: str,
        /,
        **kwargs
    ) -> Union[SyncResourceLinkObject, "SyncOperationLinkObject"]:
        """
            Saves a public resource to the disk.
            Returns the link to the operation if it's performed asynchronously,
            or a link to the resource otherwise.

            :param public_key: public key or public URL of the public resource
            :param name: filename of the saved resource
            :param path: path to the copied resource in the public folder
            :param save_path: path to the destination directory (downloads directory by default)
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises InsufficientStorageError: cannot upload file due to lack of storage space
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/public#save>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47public47resources/SaveToDiskPublicResource>`__

            :returns: :any:`SyncResourceLinkObject` or :any:`SyncOperationLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return self._maybe_wait(SaveToDiskRequest, public_key, **kwargs)

    def get_public_meta(
        self,
        public_key: str,
        /,
        **kwargs
    ) -> "SyncPublicResourceObject":
        """
            Get meta-information about a public resource.

            :param public_key: public key or public URL of the public resource
            :param path: relative path to a resource in a public folder.
                         By specifying the key of the published folder in `public_key`,
                         you can request metainformation for any resource in the folder.
            :param offset: offset from the beginning of the list of nested resources
            :param limit: maximum number of nested elements to be included in the list
            :param sort: `str`, field to be used as a key to sort children resources
            :param preview_size: file preview size
            :param preview_crop: `bool`, allow preview crop
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/public>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47public47resources/GetPublicResource>`__

            :returns: :any:`SyncPublicResourceObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        # This is for internal error handling
        _then = kwargs.pop("_then", None)

        return GetPublicMetaRequest(self.session, public_key, **kwargs).send(yadisk=self, then=_then)

    def public_exists(self, public_key: str, /, **kwargs) -> bool:
        """
            Check whether the public resource exists.

            :param public_key: public key or public URL of the public resource
            :param path: relative path to the resource within the public folder
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `bool`
        """

        return _exists(self.get_public_meta, public_key, **kwargs)

    def public_listdir(
        self,
        public_key: str,
        /,
        **kwargs
    ) -> Generator["SyncPublicResourceObject", None, None]:
        """
            Get contents of a public directory.

            :param public_key: public key or public URL of the public resource
            :param path: relative path to the resource in the public folder.
                         By specifying the key of the published folder in `public_key`,
                         you can request contents of any nested folder.
            :param max_items: `int` or `None`, maximum number of returned items (`None` means unlimited)
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises WrongResourceTypeError: resource is not a directory

            :returns: generator of :any:`SyncPublicResourceObject`
        """

        return _listdir(self.get_public_meta, public_key, **kwargs)

    def get_public_type(self, public_key: str, /, **kwargs) -> str:
        """
            Get public resource type.

            :param public_key: public key or public URL of the public resource
            :param path: relative path to the resource within the public folder
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: "file" or "dir"
        """

        return _get_type(self.get_public_meta, public_key, **kwargs)

    def is_public_dir(self, public_key: str, /, **kwargs) -> bool:
        """
            Check whether the public resource is a public directory.

            :param public_key: public key or public URL of the public resource
            :param path: relative path to the resource within the public folder
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `public_key` is a directory, `False` otherwise (even if it doesn't exist)
        """

        try:
            return self.get_public_type(public_key, **kwargs) == "dir"
        except PathNotFoundError:
            return False

    def is_public_file(self, public_key: str, /, **kwargs) -> bool:
        """
            Check whether the public resource is a public file.

            :param public_key: public key or public URL of the public resource
            :param path: relative path to the resource within the public folder
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `public_key` is a file, `False` otherwise (even if it doesn't exist)
        """

        try:
            return self.get_public_type(public_key, **kwargs) == "file"
        except PathNotFoundError:
            return False

    def trash_listdir(
        self,
        path: str,
        /,
        **kwargs
    ) -> Generator["SyncTrashResourceObject", None, None]:
        """
            Get contents of a trash resource.

            :param path: path to the directory in the trash bin
            :param max_items: `int` or `None`, maximum number of returned items (`None` means unlimited)
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises WrongResourceTypeError: resource is not a directory

            :returns: generator of :any:`SyncTrashResourceObject`
        """

        return _listdir(self.get_trash_meta, path, **kwargs)

    def get_trash_type(self, path: str, /, **kwargs) -> str:
        """
            Get trash resource type.

            :param path: path to the trash resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: "file" or "dir"
        """

        return _get_type(self.get_trash_meta, path, **kwargs)

    def is_trash_dir(self, path: str, /, **kwargs) -> bool:
        """
            Check whether `path` is a trash directory.

            :param path: path to the trash resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
        """

        try:
            return self.get_trash_type(path, **kwargs) == "dir"
        except PathNotFoundError:
            return False

    def is_trash_file(self, path: str, /, **kwargs) -> bool:
        """
            Check whether `path` is a trash file.

            :param path: path to the trash resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a file, `False` otherwise (even if it doesn't exist)
        """

        try:
            return self.get_trash_type(path, **kwargs) == "file"
        except PathNotFoundError:
            return False

    def get_public_resources(self, **kwargs) -> "SyncPublicResourcesListObject":
        """
            Get a list of public resources.

            :param offset: offset from the beginning of the list
            :param limit: maximum number of elements in the list
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param type: filter based on type of resources ("file" or "dir")
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/recent-public>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/ListPublicResources>`__

            :returns: :any:`SyncPublicResourcesListObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return GetPublicResourcesRequest(self.session, **kwargs).send(yadisk=self)

    def get_all_public_resources(
        self,
        *,
        max_items: Optional[int] = None,
        **kwargs
    ) -> Generator[SyncPublicResourceObject, None, None]:
        """
            Get a list of all public resources.

            :param max_items: `int` or `None`, maximum number of returned items (`None` means unlimited)
            :param offset: offset from the beginning of the list
            :param limit: maximum number of elements in the list
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param type: filter based on type of resources ("file" or "dir")
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/recent-public>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/ListPublicResources>`__

            :returns: generator of :any:`SyncPublicResourceObject`
        """

        if kwargs.get("offset") is None:
            kwargs["offset"] = 0

        if kwargs.get("limit") is None:
            kwargs["limit"] = 100

        remaining_items = max_items

        while True:
            # Do not query more items than necessary
            if remaining_items is not None:
                kwargs["limit"] = min(remaining_items, kwargs["limit"])

            files = self.get_public_resources(**kwargs).items or []
            file_count = len(files)

            yield from files[:remaining_items]

            if remaining_items is not None:
                remaining_items -= file_count

                if remaining_items <= 0:
                    break

            if file_count < kwargs["limit"]:
                break

            kwargs["offset"] += kwargs["limit"]

    def patch(self, path: str, properties: dict, /, **kwargs) -> "SyncResourceObject":
        """
            Update custom properties of a resource.

            :param path: path to the resource
            :param properties: `dict`, custom properties to update
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/meta-add>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/UpdateResource>`__

            :returns: :any:`ResourceObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return PatchRequest(self.session, path, properties, **kwargs).send(yadisk=self)

    def _get_files_some(self, **kwargs) -> List["SyncResourceObject"]:
        response: "SyncFilesResourceListObject" = FilesRequest(
            self.session, **kwargs).send(yadisk=self)

        if response.items is None:
            raise InvalidResponseError("Response did not contain key field")

        return response.items

    def get_files(
        self,
        *,
        max_items: Optional[int] = None,
        **kwargs
    ) -> Generator["SyncResourceObject", None, None]:
        """
            Get a flat list of all files (that doesn't include directories).

            :param offset: offset from the beginning of the list
            :param max_items: `int` or `None`, maximum number of returned items (`None` means unlimited)
            :param limit: number of list elements to be included in each response
            :param media_type: type of files to include in the list
            :param sort: `str`, field to be used as a key to sort children resources
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/all-files>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/GetFlatFilesList>`__

            :returns: generator of :any:`ResourceObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        if kwargs.get("offset") is None:
            kwargs["offset"] = 0

        if kwargs.get("limit") is None:
            kwargs["limit"] = 200

        remaining_items = max_items

        while True:
            # Do not query more items than necessary
            if remaining_items is not None:
                kwargs["limit"] = min(remaining_items, kwargs["limit"])

            files = self._get_files_some(**kwargs)
            file_count = len(files)

            yield from files[:remaining_items]

            if remaining_items is not None:
                remaining_items -= file_count

                if remaining_items <= 0:
                    break

            if file_count < kwargs["limit"]:
                break

            kwargs["offset"] += kwargs["limit"]

    def get_last_uploaded(self, **kwargs) -> List["SyncResourceObject"]:
        """
            Get the list of latest uploaded files sorted by upload date.

            :param limit: maximum number of elements in the list
            :param media_type: type of files to include in the list
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/recent-upload>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/GetLastUploadedFilesList>`__

            :returns: generator of :any:`ResourceObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        response: "SyncLastUploadedResourceListObject" = LastUploadedRequest(
            self.session, **kwargs
        ).send(yadisk=self)

        if response.items is None:
            raise InvalidResponseError("Response did not contain key field")

        return response.items

    def upload_url(
        self,
        url: str,
        path: str,
        /,
        **kwargs
    ) -> "SyncOperationLinkObject":
        """
            Upload a file from URL.

            :param url: source URL
            :param path: destination path
            :param disable_redirects: `bool`, forbid redirects
            :param fields: list of keys to be included in the response
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises PathExistsError: destination path already exists
            :raises InsufficientStorageError: cannot upload file due to lack of storage space
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/upload-ext>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/UploadExternalResource>`__

            :returns: :any:`SyncOperationLinkObject`, link to the asynchronous operation
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return self._maybe_wait(UploadURLRequest, url, path, **kwargs)

    def get_public_download_link(self, public_key: str, /, **kwargs) -> str:
        """
            Get a download link for a public resource.

            :param public_key: public key or public URL of the public resource
            :param path: relative path to the resource within the public folder
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/public#download-request>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47public47resources/GetPublicResourceDownloadLink>`__

            :returns: `str`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return GetPublicDownloadLinkRequest(
            self.session, public_key, fields=["href"], **kwargs
        ).send(yadisk=self, then=_validate_link_response).href

    def download_public(
        self,
        public_key: str,
        file_or_path: FileOrPathDestination,
        /,
        **kwargs
    ) -> SyncPublicResourceLinkObject:
        """
            Download the public resource.

            :param public_key: public key or public URL of the public resource
            :param file_or_path: destination path or file-like object
            :param path: relative path to the resource within the public folder
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`SyncPublicResourceLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)

        self._download(
            lambda public_key, **kwargs: self.get_public_download_link(public_key, **kwargs),
            public_key, file_or_path, **kwargs)

        return SyncPublicResourceLinkObject.from_public_key(public_key, yadisk=self)

    def get_operation_status(self, operation_id: str, /, **kwargs) -> OperationStatus:
        """
            Get operation status.

            :param operation_id: ID of the operation or a link
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises OperationNotFoundError: requested operation was not found

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/operations>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47operations47123operation95id125/GetOperationStatus/>`__

            :returns: `str`, :code:`"in-progress"` indicates that the operation
                      is currently running, :code:`"success"` indicates that
                      the operation was successful, :code:`"failed"` means that
                      the operation failed
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return GetOperationStatusRequest(
            self.session, operation_id, fields=["status"], **kwargs
        ).send(yadisk=self).status

    def wait_for_operation(
        self,
        operation_id: str,
        /,
        *,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        **kwargs
    ) -> None:
        """
            Wait until an operation is completed. If the operation fails, an
            exception is raised. Waiting is performed by calling :any:`time.sleep`.

            :param operation_id: ID of the operation or a link
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)
        """

        poll_start_time = time.monotonic()

        while (status := self.get_operation_status(operation_id, **kwargs)) == "in-progress":
            if poll_timeout is not None:
                total_poll_duration = time.monotonic() - poll_start_time

                if total_poll_duration >= poll_timeout:
                    raise AsyncOperationPollingTimeoutError("Asynchronous operation did not complete in specified time")

            time.sleep(poll_interval)

        if status != "success":
            raise AsyncOperationFailedError("Asynchronous operation failed")
