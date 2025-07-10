# -*- coding: utf-8 -*-
# Copyright © 2024 Ivan Konovalov

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

import asyncio
import inspect
from pathlib import PurePosixPath

import posixpath
from urllib.parse import urlencode

from .types import (
    AsyncFileOrPath, AsyncFileOrPathDestination, AsyncOpenFileCallback,
    AsyncSessionFactory, FileOpenMode, BinaryAsyncFileLike, AsyncSessionName,
    OperationStatus, PublicSettings
)

from . import settings
from ._api import *
from .exceptions import (
    AsyncOperationFailedError, AsyncOperationPollingTimeoutError,
    InvalidResponseError, ParentNotFoundError, RetriableYaDiskError, UnauthorizedError,
    OperationNotFoundError, PathNotFoundError, WrongResourceTypeError
)
from .utils import auto_retry, CaseInsensitiveDict
from .objects import (
    AsyncResourceLinkObject, AsyncPublicResourceLinkObject, TokenObject,
    TokenRevokeStatusObject, DiskInfoObject, AsyncResourceObject,
    AsyncOperationLinkObject, AsyncTrashResourceObject,
    AsyncPublicResourceObject, AsyncPublicResourcesListObject,
    AsyncFilesResourceListObject, AsyncLastUploadedResourceListObject,
    DeviceCodeObject, ResourceUploadLinkObject, PublicSettingsObject, PublicAvailableSettingsObject
)

from typing import Any, Optional, Union, IO, BinaryIO, Literal
from ._typing_compat import Callable, AsyncGenerator, Awaitable, Dict, List, Type

from ._async_session import AsyncSession
from ._import_session import import_async_session

from ._client_common import (
    _add_spoof_user_agent_header, _apply_default_args,
    _filter_request_kwargs, _set_authorization_header,
    _add_authorization_header, _validate_listdir_response,
    _validate_link_response, _validate_get_type_response
)

from ._common import remove_path_schema

_default_open_file: AsyncOpenFileCallback

try:
    import aiofiles


    async def _open_file_with_aiofiles(path: Union[str, bytes], mode: FileOpenMode) -> BinaryAsyncFileLike:
        return await aiofiles.open(path, mode)


    _default_open_file = _open_file_with_aiofiles
except ImportError:
    async def _open_file(path: Union[str, bytes], mode: FileOpenMode) -> BinaryIO:
        return open(path, mode)


    _default_open_file = _open_file

__all__ = ["AsyncClient"]


async def _exists(get_meta_function: Callable[..., Awaitable], /, *args, **kwargs) -> bool:
    try:
        # We want to query the bare minimum number of fields, that's what
        # the fields parameter is for
        await get_meta_function(*args, fields=["type"], **kwargs)

        return True
    except PathNotFoundError:
        return False


ResourceType = Union["AsyncResourceObject", "AsyncPublicResourceObject", "AsyncTrashResourceObject"]


async def _get_type(
    get_meta_function: Callable[..., Awaitable[ResourceType]],
    /,
    *args,
    **kwargs
) -> str:
    return (
        await get_meta_function(
            *args,
            _then=_validate_get_type_response,
            fields=["type"],
            **kwargs
        )
    ).type  # type: ignore[return-value]


async def _listdir(
    get_meta_function: Callable[..., Awaitable[ResourceType]],
    path: str,
    /,
    *,
    max_items: Optional[int] = None,
    **kwargs
) -> AsyncGenerator:
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

    result = await get_meta_function(path, _then=_validate_listdir_response, **kwargs)

    if result.type == "file":
        raise WrongResourceTypeError("%r is a file" % (path,))

    for child in result.embedded.items[:remaining_items]:  # type: ignore[union-attr,index]
        yield child

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
        result = await get_meta_function(path, _then=_validate_listdir_response, **kwargs)

        if result.type == "file":
            raise WrongResourceTypeError("%r is a file" % (path,))

        for child in result.embedded.items[:remaining_items]:  # type: ignore[union-attr,index]
            yield child

        limit = result.embedded.limit  # type: ignore[assignment,union-attr]
        total = result.embedded.total  # type: ignore[assignment,union-attr]


async def read_in_chunks(file: IO, chunk_size: int = 64 * 1024) -> Union[AsyncGenerator[str, None],
                                                                         AsyncGenerator[bytes, None]]:
    while chunk := await file.read(chunk_size):
        yield chunk


async def read_in_chunks_sync(file: IO, chunk_size: int = 64 * 1024) -> Union[AsyncGenerator[str, None],
                                                                              AsyncGenerator[bytes, None]]:
    while chunk := file.read(chunk_size):
        yield chunk


def is_async_func(func: Any) -> bool:
    return inspect.isgeneratorfunction(func) or asyncio.iscoroutinefunction(func)


async def _file_tell(file: Any) -> int:
    if is_async_func(file.tell):
        return await file.tell()
    else:
        return file.tell()


async def _file_seek(file: Any, offset: int, whence: int = 0) -> int:
    if is_async_func(file.seek):
        return await file.seek(offset, whence)
    else:
        return file.seek(offset, whence)


async def _is_file_seekable(file: Any) -> bool:
    if not hasattr(file, "seekable"):
        # Assume the file is seekable if there's no way to check
        return True

    if is_async_func(file.seekable):
        return await file.seekable()

    return file.seekable()


class AsyncClient:
    """
        Implements access to Yandex.Disk REST API (provides asynchronous API).

        HTTP client implementation can be specified using the :code:`session`
        parameter. :any:`AsyncHTTPXSession` is used by default. For other options,
        see :doc:`/api_reference/sessions`.

        Almost all methods of :any:`AsyncClient` (the ones that accept `**kwargs`)
        accept some additional arguments:

        * **n_retries** - `int`, maximum number of retries for a request
        * **retry_interval** - `float`, delay between retries (in seconds)
        * **headers** - `dict` or `None`, additional request headers
        * **timeout** - `tuple` (:code:`(<connect timeout>, <read timeout>)`) or
          `float` (specifies both connect and read timeout), request timeout
          (in seconds)

        Additional parameters, specific to a given HTTP client library can also
        be passed, see documentation for specific :any:`AsyncSession` subclasses
        (:doc:`/api_reference/sessions`).

        .. note::
           Do not forget to call :any:`AsyncClient.close` or use the `async with` statement
           to close all the connections. Otherwise, you may get a warning.

           In :any:`Client` this is handled in the destructor, but since
           :any:`AsyncClient.close` is a coroutine function the
           same cannot be done here, so you have to do it explicitly.

        :param id: application ID
        :param secret: application secret password
        :param token: application token
        :param default_args: `dict` or `None`, default arguments for methods.
                             Can be used to set the default timeout, headers, etc.
        :param session: `None`, `str` or an instance of :any:`AsyncSession`.
                        If :code:`session` is a string, the appropriate session
                        class will be imported, it must be one of the
                        following values:

                          * :code:`"aiohttp"` - :any:`AIOHTTPSession`
                          * :code:`"httpx"` - :any:`AsyncHTTPXSession`

        :param open_file: `None` or an async function that opens a file for
                           reading or writing (:code:`aiofiles.open()` by default)
        :param session_factory: kept for compatibility, callable that returns an
                                instance of :any:`AsyncSession`

        :ivar id: `str`, application ID
        :ivar secret: `str`, application secret password
        :ivar token: `str`, application token
        :ivar default_args: `dict`, default arguments for methods. Can be used to
                            set the default timeout, headers, etc.
        :ivar session: current session (:any:`AsyncSession` instance)
        :ivar open_file: async function that opens a file for reading or writing
                         (:code:`aiofiles.open()` by default)

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
    session: AsyncSession
    open_file: AsyncOpenFileCallback

    synchronous = False

    def __init__(
        self,
        id:     str = "",
        secret: str = "",
        token:  str = "",
        *,
        default_args:    Optional[Dict[str, Any]] = None,
        session:         Optional[Union[AsyncSession, AsyncSessionName]] = None,
        open_file:       Optional[AsyncOpenFileCallback] = None,
        session_factory: Optional[AsyncSessionFactory] = None
    ) -> None:
        self.id = id
        self.secret = secret

        self.token = ""

        self.default_args = {} if default_args is None else default_args

        if session is None:
            if session_factory is not None:
                session = session_factory()
            else:
                try:
                    session = import_async_session("httpx")()
                except ModuleNotFoundError as e:
                    if e.name == "httpx":
                        raise ModuleNotFoundError(
                            "httpx is not installed. Either install httpx or provide a custom session",
                            name=e.name,
                            path=e.path) from e
                    else:
                        raise
        elif isinstance(session, str):
            session = import_async_session(session)()

        self.session = session

        if open_file is None:
            open_file = _default_open_file

        self.open_file = open_file

        self.token = token

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        await self.close()

    async def close(self) -> None:
        """
            Closes the session.
            Do not call this method while there are other active threads using this object.

            This method can also be called implicitly by using the `async with`
            statement.
        """

        await self.session.close()

    async def _maybe_wait(
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

            async def then(response: Optional[AsyncOperationLinkObject]) -> Optional[AsyncOperationLinkObject]:
                if not isinstance(response, AsyncOperationLinkObject):
                    return response

                try:
                    await response.wait(
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

            return await request.asend(yadisk=self, then=then)
        else:
            return await request.asend(yadisk=self)

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
        display:               None = None,
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

    async def get_device_code(self, **kwargs) -> "DeviceCodeObject":
        """
            This request is used for authorization using the Yandex OAuth page.
            In this case the user must enter the verification code (:code:`user_code`)
            in the browser on the Yandex OAuth page.
            After the user has entered the code on the OAuth page, the application
            can exchange the :code:`device_code` for the token using the
            :any:`AsyncClient.get_token_from_device_code()`.

            :param device_id: unique device ID (between 6 and 50 characters)
            :param device_name: device name, should not be longer than 100 characters
            :param scope: `str`, list of permissions for the application
            :param optional_scope: `str`, list of optional permissions for the application
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises InvalidClientError: invalid client ID or client secret
            :raises BadRequestError: invalid request parameters

            :returns: :any:`DeviceCodeObject` containing :code:`user_code` and :code:`device_code`
        """

        _apply_default_args(kwargs, self.default_args)
        _set_authorization_header(kwargs, "")

        return await GetDeviceCodeRequest(self.session, self.id, **kwargs).asend(yadisk=self)

    async def get_token(self, code: str, /, **kwargs) -> "TokenObject":
        """
            Get a new token.

            :param code: confirmation code
            :param device_id: unique device ID (between 6 and 50 characters)
            :param code_verifier: `str`, verifier code, used with the PKCE authorization flow
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises BadVerificationCodeError: confirmation code has invalid format
            :raises InvalidGrantError: invalid or expired confirmation code
            :raises InvalidClientError: invalid client ID or client secret
            :raises BadRequestError: invalid request parameters

            :returns: :any:`TokenObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _set_authorization_header(kwargs, "")

        return await GetTokenRequest(
            self.session,
            "authorization_code",
            self.id,
            code=code,
            client_secret=self.secret,
            **kwargs
        ).asend(yadisk=self)

    async def get_token_from_device_code(self, device_code: str, /, **kwargs) -> "TokenObject":
        """
            Get a new token from a device code, previously obtained with :any:`AsyncClient.get_device_code()`.

            :param device_code: device code, obtained from :any:`AsyncClient.get_device_code()`
            :param device_id: unique device ID (between 6 and 50 characters)
            :param device_name: device name, should not be longer than 100 characters
            :param code_verifier: `str`, verifier code, used with the PKCE authorization flow
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
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

        return await GetTokenRequest(
            self.session,
            "device_code",
            client_id=self.id,
            code=device_code,
            client_secret=self.secret,
            **kwargs
        ).asend(yadisk=self)

    async def refresh_token(self, refresh_token: str, /, **kwargs) -> "TokenObject":
        """
            Refresh an existing token.

            :param refresh_token: the refresh token that was received with the token
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises InvalidGrantError: invalid or expired refresh token or it
                                       doesn't belong to this application
            :raises InvalidClientError: invalid client ID or client secret
            :raises BadRequestError: invalid request parameters

            :returns: :any:`TokenObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _set_authorization_header(kwargs, "")

        return await RefreshTokenRequest(
            self.session,
            refresh_token,
            self.id,
            self.secret,
            **kwargs
        ).asend(yadisk=self)

    async def revoke_token(
        self,
        token: Optional[str] = None,
        /,
        **kwargs
    ) -> "TokenRevokeStatusObject":
        """
            Revoke the token.

            :param token: token to revoke, equivalent to `self.token` if `None`
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
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

        return await RevokeTokenRequest(
            self.session,
            token,
            self.id,
            self.secret,
            **kwargs
        ).asend(yadisk=self)

    async def get_disk_info(self, **kwargs) -> "DiskInfoObject":
        """
            Get disk information.

            :param extra_fields: list of additional keys to be included in the response
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/capacity>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk/GetDisk>`__

            :returns: :any:`DiskInfoObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return await DiskInfoRequest(self.session, **kwargs).asend(yadisk=self)

    async def get_meta(self, path: str, /, **kwargs) -> "AsyncResourceObject":
        """
            Get meta information about a file/directory.

            :param path: path to the resource
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param sort: `str`, field to be used as a key to sort children resources
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/meta>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/GetResource>`__

            :returns: :any:`AsyncResourceObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        # This is for internal error handling
        _then = kwargs.pop("_then", None)

        return await GetMetaRequest(self.session, path, **kwargs).asend(yadisk=self, then=_then)

    async def exists(self, path: str, /, **kwargs) -> bool:
        """
            Check whether `path` exists.

            :param path: path to the resource
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `bool`
        """

        return await _exists(self.get_meta, path, **kwargs)

    async def get_type(self, path: str, /, **kwargs) -> str:
        """
            Get resource type.

            :param path: path to the resource
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: "file" or "dir"
        """

        return await _get_type(self.get_meta, path, **kwargs)

    async def is_file(self, path: str, /, **kwargs) -> bool:
        """
            Check whether `path` is a file.

            :param path: path to the resource
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a file, `False` otherwise (even if it doesn't exist)
        """

        try:
            return (await self.get_type(path, **kwargs)) == "file"
        except PathNotFoundError:
            return False

    async def is_dir(self, path: str, /, **kwargs) -> bool:
        """
            Check whether `path` is a directory.

            :param path: path to the resource
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
        """

        try:
            return (await self.get_type(path, **kwargs)) == "dir"
        except PathNotFoundError:
            return False

    async def listdir(
        self,
        path: str,
        /,
        **kwargs
    ) -> AsyncGenerator["AsyncResourceObject", None]:
        """
            Get contents of `path`.

            :param path: path to the directory
            :param max_items: `int` or `None`, maximum number of returned items (`None` means unlimited)
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises WrongResourceTypeError: resource is not a directory

            :returns: async generator of :any:`AsyncResourceObject`
        """

        async for file in _listdir(self.get_meta, path, **kwargs):
            yield file

    async def get_upload_link(
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
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
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

        return (
            await GetUploadLinkRequest(
                self.session, path, fields=["href"], **kwargs
            ).asend(yadisk=self, then=_validate_link_response)
        ).href

    async def get_upload_link_object(
        self,
        path: str,
        /,
        spoof_user_agent: bool = True,
        **kwargs
    ) -> ResourceUploadLinkObject:
        """
            Get a link to upload the file using the PUT request.
            This is similar to :any:`AsyncClient.get_upload_link()`, except it returns
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
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
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

        return await GetUploadLinkRequest(
            self.session, path, **kwargs
        ).asend(yadisk=self)

    async def _upload(self,
                      get_upload_link_function: Callable[..., Awaitable[str]],
                      file_or_path: AsyncFileOrPath,
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
        generator_factory: Optional[Callable[[], AsyncGenerator]] = None
        file_position = 0

        session = self.session

        try:
            if isinstance(file_or_path, (str, bytes)):
                close_file = True
                file = await self.open_file(file_or_path, "rb")
            elif inspect.isasyncgenfunction(file_or_path):
                generator_factory = file_or_path
            else:
                close_file = False
                file = file_or_path

            if generator_factory is None:
                if await _is_file_seekable(file):
                    file_position = await _file_tell(file)
                else:
                    n_retries, n_retries_for_upload_link = 0, n_retries

            async def attempt() -> None:
                temp_kwargs = dict(kwargs)
                temp_kwargs["n_retries"] = n_retries_for_upload_link
                temp_kwargs["retry_interval"] = 0.0

                link = await get_upload_link_function(dst_path, **temp_kwargs)

                # session.get() doesn't accept some of the passed parameters
                _filter_request_kwargs(temp_kwargs)

                # Disable keep-alive by default, since the upload server is random
                temp_kwargs["headers"].setdefault("Connection", "close")

                # This is generally not necessary, libraries like aiohttp
                # will generally always set this header while others might not
                # We're setting content-type here just to fix this inconsistency,
                # this makes testing easier
                temp_kwargs["headers"].setdefault("Content-Type", "application/octet-stream")

                data: Any = None

                if generator_factory is None:
                    if await _is_file_seekable(file):
                        await _file_seek(file, file_position)

                    if is_async_func(file.read):
                        data = read_in_chunks(file)
                    else:
                        data = read_in_chunks_sync(file)
                else:
                    data = generator_factory()

                settings.logger.info(f"uploading file to {dst_path} at {link}")

                async with await session.send_request("PUT", link, data=data, **temp_kwargs) as response:
                    if response.status != 201:
                        raise await response.get_exception()

            await auto_retry(attempt, n_retries, retry_interval)
        finally:
            if close_file and file is not None:
                await file.close()

    async def upload(
        self,
        path_or_file: AsyncFileOrPath,
        dst_path: str,
        /,
        **kwargs
    ) -> AsyncResourceLinkObject:
        """
            Upload a file to disk.

            :param path_or_file: path, file-like object or an async generator function to be uploaded
            :param dst_path: destination path
            :param overwrite: if `True`, the resource will be overwritten if it already exists,
                              an error will be raised otherwise
            :param spoof_user_agent: `bool`, if `True` (default), the `User-Agent` header
                will be set to a special value, which should allow bypassing of
                Yandex.Disk's upload speed limit
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises PathExistsError: destination path already exists
            :raises InsufficientStorageError: cannot upload file due to lack of storage space
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded

            :returns: :any:`AsyncResourceLinkObject`, link to the destination resource
        """

        _apply_default_args(kwargs, self.default_args)

        await self._upload(self.get_upload_link, path_or_file, dst_path, **kwargs)
        return AsyncResourceLinkObject.from_path(dst_path, yadisk=self)

    async def upload_by_link(self,
                             file_or_path: AsyncFileOrPath,
                             link: str, /, **kwargs) -> None:
        """
            Upload a file to disk using an upload link.

            :param file_or_path: path, file-like object or an async generator function to be uploaded
            :param link: upload link
            :param overwrite: if `True`, the resource will be overwritten if it already exists,
                              an error will be raised otherwise
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises InsufficientStorageError: cannot upload file due to lack of storage space
        """

        _apply_default_args(kwargs, self.default_args)

        async def get_link(*args, **kwargs) -> str:
            return link

        await self._upload(get_link, file_or_path, "", **kwargs)

    async def get_download_link(self, path: str, /, **kwargs) -> str:
        """
            Get a download link for a file (or a directory).

            :param path: path to the resource
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
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

        return (
            await GetDownloadLinkRequest(
                self.session, path, fields=["href"], **kwargs
            ).asend(yadisk=self, then=_validate_link_response)
        ).href

    async def _download(
        self,
        get_download_link_function: Callable[..., Awaitable[str]],
        src_path: str,
        file_or_path: AsyncFileOrPathDestination,
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
                file = await self.open_file(file_or_path, "wb")
            else:
                close_file = False
                file = file_or_path

            if await _is_file_seekable(file):
                file_position = await _file_tell(file)
            else:
                n_retries, n_retries_for_download_link = 0, n_retries

            async def attempt() -> None:
                temp_kwargs = dict(kwargs)
                temp_kwargs["n_retries"] = n_retries_for_download_link
                temp_kwargs["retry_interval"] = 0.0
                link = await get_download_link_function(src_path, **temp_kwargs)

                # session.get() doesn't accept some of the passed parameters
                _filter_request_kwargs(temp_kwargs)

                temp_kwargs.setdefault("stream", True)

                if await _is_file_seekable(file):
                    await _file_seek(file, file_position)

                settings.logger.info(f"downloading file {src_path} from {link}")

                async with await session.send_request("GET", link, **temp_kwargs) as response:
                    if response.status != 200:
                        raise await response.get_exception()

                    await response.download(file.write)

            return await auto_retry(attempt, n_retries, retry_interval)
        finally:
            if close_file and file is not None:
                await file.close()

    async def download(
        self,
        src_path: str,
        path_or_file: AsyncFileOrPathDestination,
        /,
        **kwargs
    ) -> AsyncResourceLinkObject:
        """
            Download the file.

            :param src_path: source path
            :param path_or_file: destination path or file-like object
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`AsyncResourceLinkObject`, link to the source resource
        """

        _apply_default_args(kwargs, self.default_args)

        await self._download(self.get_download_link, src_path, path_or_file, **kwargs)
        return AsyncResourceLinkObject.from_path(src_path, yadisk=self)

    async def download_by_link(
        self,
        link: str,
        file_or_path: AsyncFileOrPathDestination,
        /,
        **kwargs
    ) -> None:
        """
            Download the file from the link.

            :param link: download link
            :param file_or_path: destination path or file-like object
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`
        """

        _apply_default_args(kwargs, self.default_args)

        async def get_link(*args, **kwargs) -> str:
            return link

        await self._download(get_link, "", file_or_path, **kwargs)

    async def remove(
        self,
        path: str,
        /,
        **kwargs
    ) -> Optional[AsyncOperationLinkObject]:
        """
            Remove the resource.

            :param path: path to the resource to be removed
            :param permanently: if `True`, the resource will be removed permanently,
                                otherwise, it will be just moved to the trash
            :param md5: `str`, MD5 hash of the file to remove
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
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

            :returns: :any:`AsyncOperationLinkObject` if the operation is performed asynchronously, `None` otherwise
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return await self._maybe_wait(DeleteRequest, path, **kwargs)

    async def mkdir(self, path: str, /, **kwargs) -> AsyncResourceLinkObject:
        """
            Create a new directory.

            :param path: path to the directory to be created
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises DirectoryExistsError: destination path already exists
            :raises InsufficientStorageError: cannot create directory due to lack of storage space
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/create-folder>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/CreateResource>`__

            :returns: :any:`AsyncResourceLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return await MkdirRequest(self.session, path, **kwargs).asend(yadisk=self)

    async def makedirs(self, path: str, /, **kwargs) -> AsyncResourceLinkObject:
        """
            Create a new directory at `path`. If its parent directory doesn't
            exist it will also be created recursively.

            :param path: path to the directory to be created
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises DirectoryExistsError: destination path already exists
            :raises InsufficientStorageError: cannot create directory due to lack of storage space
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`AsyncResourceLinkObject`
        """

        while True:
            try:
                return await self.mkdir(path, **kwargs)
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

                await self.makedirs(head, **kwargs)

    async def check_token(self, token: Optional[str] = None, /, **kwargs) -> bool:
        """
            Check whether the token is valid.

            :param token: token to check, equivalent to `self.token` if `None`
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
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
            await self.get_operation_status(fake_operation_id, **kwargs)
            return True
        except OperationNotFoundError:
            return True
        except UnauthorizedError:
            return False

    async def get_trash_meta(self, path: str, /, **kwargs) -> "AsyncTrashResourceObject":
        """
            Get meta information about a trash resource.

            :param path: path to the trash resource
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param sort: `str`, field to be used as a key to sort children resources
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/meta>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47trash47resources/GetTrashResource>`__

            :returns: :any:`AsyncTrashResourceObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        # This is for internal error handling
        _then = kwargs.pop("_then", None)

        return await GetTrashRequest(
            self.session, path, **kwargs
        ).asend(yadisk=self, then=_then)

    async def trash_exists(self, path: str, /, **kwargs) -> bool:
        """
            Check whether the trash resource at `path` exists.

            :param path: path to the trash resource
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `bool`
        """

        return await _exists(self.get_trash_meta, path, **kwargs)

    async def copy(
        self,
        src_path: str,
        dst_path: str,
        /,
        **kwargs
    ) -> Union[AsyncResourceLinkObject, AsyncOperationLinkObject]:
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
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
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

            :returns: :any:`AsyncResourceLinkObject` or :any:`AsyncOperationLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return await self._maybe_wait(CopyRequest, src_path, dst_path, **kwargs)

    async def restore_trash(
        self,
        path: str,
        dst_path: Optional[str] = None,
        **kwargs
    ) -> Union[AsyncResourceLinkObject, AsyncOperationLinkObject]:
        """
            Restore a trash resource.
            Returns a link to the newly created resource or a link to the asynchronous operation.

            :param path: path to the trash resource to restore
            :param dst_path: destination path
            :param overwrite: `bool`, determines whether the destination can be overwritten
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
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

            :returns: :any:`AsyncResourceLinkObject` or :any:`AsyncOperationLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return await self._maybe_wait(
            RestoreTrashRequest, path, dst_path=dst_path, **kwargs
        )

    async def move(
        self,
        src_path: str,
        dst_path: str,
        /,
        **kwargs
    ) -> Union[AsyncOperationLinkObject, AsyncResourceLinkObject]:
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
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
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

            :returns: :any:`AsyncResourceLinkObject` or :any:`AsyncOperationLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return await self._maybe_wait(MoveRequest, src_path, dst_path, **kwargs)

    async def rename(
        self,
        src_path: str,
        new_name: str,
        /,
        **kwargs
    ) -> Union[AsyncResourceLinkObject, AsyncOperationLinkObject]:
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
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
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

            :returns: :any:`AsyncResourceLinkObject` or :any:`AsyncOperationLinkObject`
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

        return await self.move(src_path, dst_path, **kwargs)

    async def remove_trash(
        self,
        path: str,
        /,
        **kwargs
    ) -> Optional[AsyncOperationLinkObject]:
        """
            Remove a trash resource.

            :param path: path to the trash resource to be deleted
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
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

            :returns: :any:`AsyncOperationLinkObject` if the operation is performed asynchronously, `None` otherwise
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return await self._maybe_wait(DeleteTrashRequest, path, **kwargs)

    async def publish(self, path: str, /, **kwargs) -> AsyncResourceLinkObject:
        """
            Make a resource public.

            :param path: path to the resource to be published
            :param allow_address_access: `bool`, specifies the request format, i.e.
                with personal access settings (when set to `True`) or without
            :param public_settings: :any:`PublicSettings` or `None`, public access settings for the resource
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/publish>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/PublishResource>`__

            :returns: :any:`AsyncResourceLinkObject`, link to the resource
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return await PublishRequest(self.session, path, **kwargs).asend(yadisk=self)

    async def unpublish(self, path: str, /, **kwargs) -> AsyncResourceLinkObject:
        """
            Make a public resource private.

            :param path: path to the resource to be unpublished
            :param allow_address_access: `bool`, specifies the request format, i.e.
                with personal access settings (when set to `True`) or without
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/publish#unpublish-q>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/UnpublishResource>`__

            :returns: :any:`AsyncResourceLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return await UnpublishRequest(self.session, path, **kwargs).asend(yadisk=self)

    async def get_public_settings(self, path: str, /, **kwargs) -> PublicSettingsObject:
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
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
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

        return await GetPublicSettingsRequest(self.session, path, **kwargs).asend(yadisk=self)

    async def get_public_available_settings(self, path: str, /, **kwargs) -> PublicAvailableSettingsObject:
        """
            Get public settings of a shared resource for the current OAuth token owner.

            :param path: path to the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
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

        return await GetPublicAvailableSettingsRequest(self.session, path, **kwargs).asend(yadisk=self)

    async def update_public_settings(self, path: str, public_settings: PublicSettings, /, **kwargs) -> None:
        """
            Update public settings of a shared resource.

            :param path: path to the resource
            :param public_settings: :any:`PublicSettings`, public access settings for the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
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

        return await UpdatePublicSettingsRequest(self.session, path, public_settings, **kwargs).asend(yadisk=self)

    async def save_to_disk(
        self,
        public_key: str,
        /,
        **kwargs
    ) -> Union[AsyncResourceLinkObject, "AsyncOperationLinkObject"]:
        """
            Saves a public resource to the disk.
            Returns the link to the operation if it's performed asynchronously,
            or a link to the resource otherwise.

            :param public_key: public key or public URL of the resource
            :param name: filename of the saved resource
            :param path: path to the copied resource in the public folder
            :param save_path: path to the destination directory (downloads directory by default)
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
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

            :returns: :any:`AsyncResourceLinkObject` or :any:`AsyncOperationLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return await self._maybe_wait(SaveToDiskRequest, public_key, **kwargs)

    async def get_public_meta(self, public_key: str, /, **kwargs) -> "AsyncPublicResourceObject":
        """
            Get meta-information about a public resource.

            :param public_key: public key or public URL of the resource
            :param path: relative path to a resource in a public folder.
                         By specifying the key of the published folder in `public_key`,
                         you can request metainformation for any resource in the folder.
            :param offset: offset from the beginning of the list of nested resources
            :param limit: maximum number of nested elements to be included in the list
            :param sort: `str`, field to be used as a key to sort children resources
            :param preview_size: file preview size
            :param preview_crop: `bool`, allow preview crop
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/public>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47public47resources/GetPublicResource>`__

            :returns: :any:`AsyncPublicResourceObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        # This is for internal error handling
        _then = kwargs.pop("_then", None)

        return await GetPublicMetaRequest(
            self.session, public_key, **kwargs
        ).asend(yadisk=self, then=_then)

    async def public_exists(self, public_key: str, /, **kwargs) -> bool:
        """
            Check whether the public resource exists.

            :param public_key: public key or public URL of the resource
            :param path: relative path to the resource within the public folder
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `bool`
        """

        return await _exists(self.get_public_meta, public_key, **kwargs)

    async def public_listdir(
        self,
        public_key: str,
        /,
        **kwargs
    ) -> AsyncGenerator["AsyncPublicResourceObject", None]:
        """
            Get contents of a public directory.

            :param public_key: public key or public URL of the resource
            :param path: relative path to the resource in the public folder.
                         By specifying the key of the published folder in `public_key`,
                         you can request contents of any nested folder.
            :param max_items: `int` or `None`, maximum number of returned items (`None` means unlimited)
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises WrongResourceTypeError: resource is not a directory

            :returns: async generator of :any:`AsyncPublicResourceObject`
        """

        async for file in _listdir(self.get_public_meta, public_key, **kwargs):
            yield file

    async def get_public_type(self, public_key: str, /, **kwargs) -> str:
        """
            Get public resource type.

            :param public_key: public key or public URL of the resource
            :param path: relative path to the resource within the public folder
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: "file" or "dir"
        """

        return await _get_type(self.get_public_meta, public_key, **kwargs)

    async def is_public_dir(self, public_key: str, /, **kwargs) -> bool:
        """
            Check whether `public_key` is a public directory.

            :param public_key: public key or public URL of the resource
            :param path: relative path to the resource within the public folder
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `public_key` is a directory, `False` otherwise (even if it doesn't exist)
        """

        try:
            return (await self.get_public_type(public_key, **kwargs)) == "dir"
        except PathNotFoundError:
            return False

    async def is_public_file(self, public_key: str, /, **kwargs) -> bool:
        """
            Check whether `public_key` is a public file.

            :param public_key: public key or public URL of the resource
            :param path: relative path to the resource within the public folder
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `public_key` is a file, `False` otherwise (even if it doesn't exist)
        """

        try:
            return (await self.get_public_type(public_key, **kwargs)) == "file"
        except PathNotFoundError:
            return False

    async def trash_listdir(
        self,
        path: str,
        /,
        **kwargs
    ) -> AsyncGenerator["AsyncTrashResourceObject", None]:
        """
            Get contents of a trash resource.

            :param path: path to the directory in the trash bin
            :param max_items: `int` or `None`, maximum number of returned items (`None` means unlimited)
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises WrongResourceTypeError: resource is not a directory

            :returns: async generator of :any:`AsyncTrashResourceObject`
        """

        async for file in _listdir(self.get_trash_meta, path, **kwargs):
            yield file

    async def get_trash_type(self, path: str, /, **kwargs) -> str:
        """
            Get trash resource type.

            :param path: path to the trash resource
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: "file" or "dir"
        """

        return await _get_type(self.get_trash_meta, path, **kwargs)

    async def is_trash_dir(self, path: str, /, **kwargs) -> bool:
        """
            Check whether `path` is a trash directory.

            :param path: path to the trash resource
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
        """

        try:
            return (await self.get_trash_type(path, **kwargs)) == "dir"
        except PathNotFoundError:
            return False

    async def is_trash_file(self, path: str, /, **kwargs) -> bool:
        """
            Check whether `path` is a trash file.

            :param path: path to the trash resource
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
        """

        try:
            return (await self.get_trash_type(path, **kwargs)) == "file"
        except PathNotFoundError:
            return False

    async def get_public_resources(self, **kwargs) -> "AsyncPublicResourcesListObject":
        """
            Get a list of public resources.

            :param offset: offset from the beginning of the list
            :param limit: maximum number of elements in the list
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param type: filter based on type of resources ("file" or "dir")
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/recent-public>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/ListPublicResources>`__

            :returns: :any:`AsyncPublicResourcesListObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return await GetPublicResourcesRequest(self.session, **kwargs).asend(yadisk=self)

    async def get_all_public_resources(
        self,
        *,
        max_items: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator[AsyncPublicResourceObject, None]:
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

            :returns: async generator of :any:`AsyncPublicResourceObject`
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

            files = (await self.get_public_resources(**kwargs)).items or []
            file_count = len(files)

            for i in files[:remaining_items]:
                yield i

            if remaining_items is not None:
                remaining_items -= file_count

                if remaining_items <= 0:
                    break

            if file_count < kwargs["limit"]:
                break

            kwargs["offset"] += kwargs["limit"]

    async def patch(self, path: str, properties: dict, /, **kwargs) -> "AsyncResourceObject":
        """
            Update custom properties of a resource.

            :param path: path to the resource
            :param properties: `dict`, custom properties to update
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/meta-add>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/UpdateResource>`__

            :returns: :any:`AsyncResourceObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return await PatchRequest(self.session, path, properties, **kwargs).asend(yadisk=self)

    async def _get_files_some(self, **kwargs) -> List["AsyncResourceObject"]:
        def validate_response(response: "AsyncFilesResourceListObject") -> "AsyncFilesResourceListObject":
            if response.items is None:
                raise InvalidResponseError("Response did not contain key field")

            return response

        items: List["AsyncResourceObject"] = (
            await FilesRequest(
                self.session, **kwargs
            ).asend(yadisk=self, then=validate_response)
        ).items

        return items

    async def get_files(
        self,
        *,
        max_items: Optional[int] = None,
        **kwargs
    ) -> AsyncGenerator["AsyncResourceObject", None]:
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
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/all-files>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/GetFlatFilesList>`__

            :returns: async generator of :any:`AsyncResourceObject`
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

            files = await self._get_files_some(**kwargs)
            file_count = len(files)

            for file in files[:remaining_items]:
                yield file

            if remaining_items is not None:
                remaining_items -= file_count

                if remaining_items <= 0:
                    break

            if file_count < kwargs["limit"]:
                break

            kwargs["offset"] += kwargs["limit"]

    async def get_last_uploaded(self, **kwargs) -> List["AsyncResourceObject"]:
        """
            Get the list of latest uploaded files sorted by upload date.

            :param limit: maximum number of elements in the list
            :param media_type: type of files to include in the list
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            More info about this request:

            * `Official docs <https://yandex.com/dev/disk-api/doc/en/reference/recent-upload>`__
            * `Polygon <https://yandex.com/dev/disk/poligon#!/v147disk47resources/GetLastUploadedFilesList>`__

            :returns: async generator of :any:`AsyncResourceObject`
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        def validate_response(
            response: "AsyncLastUploadedResourceListObject"
        ) -> "AsyncLastUploadedResourceListObject":
            if response.items is None:
                raise InvalidResponseError("Response did not contain key field")

            return response

        items: List["AsyncResourceObject"] = (
            await LastUploadedRequest(
                self.session, **kwargs
            ).asend(yadisk=self, then=validate_response)
        ).items

        return items

    async def upload_url(
        self,
        url: str,
        path: str,
        /,
        **kwargs
    ) -> AsyncOperationLinkObject:
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
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
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

            :returns: :any:`AsyncOperationLinkObject`, link to the asynchronous operation
        """

        _apply_default_args(kwargs, self.default_args)
        _add_authorization_header(kwargs, self.token)

        return await self._maybe_wait(UploadURLRequest, url, path, **kwargs)

    async def get_public_download_link(self, public_key: str, /, **kwargs) -> str:
        """
            Get a download link for a public resource.

            :param public_key: public key or public URL of the resource
            :param path: relative path to the resource within the public folder
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
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

        return (
            await GetPublicDownloadLinkRequest(
                self.session, public_key, fields=["href"], **kwargs
            ).asend(yadisk=self, then=_validate_link_response)
        ).href

    async def download_public(
        self,
        public_key: str,
        file_or_path: AsyncFileOrPathDestination,
        /,
        **kwargs
    ) -> AsyncPublicResourceLinkObject:
        """
            Download the public resource.

            :param public_key: public key or public URL of the resource
            :param file_or_path: destination path or file-like object
            :param path: relative path to the resource within the public folder
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`AsyncPublicResourceLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)

        await self._download(
            lambda public_key, **kwargs: self.get_public_download_link(public_key, **kwargs),
            public_key, file_or_path, **kwargs)
        return AsyncPublicResourceLinkObject.from_public_key(public_key, yadisk=self)

    async def get_operation_status(self, operation_id: str, /, **kwargs) -> OperationStatus:
        """
            Get operation status.

            :param operation_id: ID of the operation or a link
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
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

        return (
            await GetOperationStatusRequest(
                self.session, operation_id, fields=["status"], **kwargs
            ).asend(yadisk=self)
        ).status

    async def wait_for_operation(
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
            exception is raised. Waiting is performed by calling :any:`asyncio.sleep`.

            :param operation_id: ID of the operation or a link
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)
        """

        async def poll() -> None:
            while (status := await self.get_operation_status(operation_id, **kwargs)) == "in-progress":
                await asyncio.sleep(poll_interval)

            if status != "success":
                raise AsyncOperationFailedError("Asynchronous operation failed")

        try:
            await asyncio.wait_for(poll(), timeout=poll_timeout)
        except asyncio.exceptions.TimeoutError as e:
            raise AsyncOperationPollingTimeoutError("Asynchronous operation did not complete in specified time") from e
