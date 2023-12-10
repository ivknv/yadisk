# -*- coding: utf-8 -*-

import asyncio
import inspect
from pathlib import PurePosixPath

from urllib.parse import urlencode

from .types import (
    AsyncFileOrPath, AsyncFileOrPathDestination, AsyncSessionFactory,
    AsyncOpenFileCallback, FileOpenMode, BinaryAsyncFileLike
)

from . import settings
from .api import *
from .exceptions import (
    InvalidResponseError, UnauthorizedError, OperationNotFoundError,
    PathNotFoundError, WrongResourceTypeError)
from .utils import auto_retry
from .objects import AsyncResourceLinkObject, AsyncPublicResourceLinkObject

from typing import Any, Optional, Union, IO, TYPE_CHECKING, BinaryIO
from .compat import Callable, AsyncGenerator, Awaitable, Dict

from .async_session import AsyncSession

try:
    from .sessions.aiohttp_session import AIOHTTPSession
except ImportError:
    # aiohttp is not available
    AIOHTTPSession = None

try:
    import aiofiles

    async def _open_file_with_aiofiles(path: Union[str, bytes], mode: FileOpenMode) -> BinaryAsyncFileLike:
        return await aiofiles.open(path, mode)

    _default_open_file = _open_file_with_aiofiles
except ImportError:
    async def _open_file(path: Union[str, bytes], mode: FileOpenMode) -> BinaryIO:
        return open(path, mode)

    _default_open_file = _open_file

if TYPE_CHECKING:
    from .objects import (
        TokenObject, TokenRevokeStatusObject, DiskInfoObject,
        AsyncResourceObject, AsyncOperationLinkObject,
        AsyncTrashResourceObject, AsyncPublicResourceObject,
        AsyncPublicResourcesListObject
    )

__all__ = ["AsyncClient"]

async def _exists(get_meta_function: Callable[..., Awaitable], /, *args, **kwargs) -> bool:
    kwargs["limit"] = 0

    try:
        await get_meta_function(*args, **kwargs)

        return True
    except PathNotFoundError:
        return False

ResourceType = Union["AsyncResourceObject", "AsyncPublicResourceObject", "AsyncTrashResourceObject"]

async def _get_type(get_meta_function: Callable[..., Awaitable[ResourceType]],
                    /, *args, **kwargs) -> str:
    kwargs["limit"] = 0
    kwargs["fields"] = ["type"]

    type = (await get_meta_function(*args, **kwargs)).type

    if type is None:
        raise InvalidResponseError("Response did not contain the type field")

    return type

async def _listdir(get_meta_function: Callable[..., Awaitable[ResourceType]],
                   path: str, /, **kwargs) -> AsyncGenerator:
    kwargs.setdefault("limit", 10000)

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

    result = await get_meta_function(path, **kwargs)

    if result.type == "file":
        raise WrongResourceTypeError("%r is a file" % (path,))

    if result.embedded is None:
        raise InvalidResponseError("Response did not contain _embedded field")

    if (result.type is None or result.embedded.items is None or
        result.embedded.offset is None or result.embedded.limit is None or
        result.embedded.total is None):
        raise InvalidResponseError("Response did not contain key field")

    for child in result.embedded.items:
        yield child

    limit: int = result.embedded.limit
    offset: int = result.embedded.offset
    total: int = result.embedded.total

    while offset + limit < total:
        offset += limit
        kwargs["offset"] = offset
        result = await get_meta_function(path, **kwargs)

        if result.embedded is None:
            raise InvalidResponseError("Response did not contain _embedded field")

        if (result.type is None or result.embedded.items is None or
            result.embedded.offset is None or result.embedded.limit is None or
            result.embedded.total is None):
            raise InvalidResponseError("Response did not contain key field")

        for child in result.embedded.items:
            yield child

        limit: int = result.embedded.limit
        total: int = result.embedded.total

def _filter_request_kwargs(kwargs: Dict[str, Any]) -> None:
    # Remove some of the yadisk-specific arguments from kwargs
    keys_to_remove = ("n_retries", "retry_interval", "fields", "overwrite", "path")

    for key in keys_to_remove:
        kwargs.pop(key, None)

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

def is_async_file(file: Any) -> bool:
    read_method = getattr(file, "read", None)

    return is_async_func(read_method)

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

    return file.seekable();

def _apply_default_args(args: Dict[str, Any], default_args: Dict[str, Any]) -> None:
    new_args = dict(default_args)
    new_args.update(args)
    args.clear()
    args.update(new_args)

class AsyncClient:
    """
        Implements access to Yandex.Disk REST API.

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
        :param session_factory: `None` or a function that returns a new instance of :any:`AsyncSession`
        :param open_file: `None` or an async function that opens a file for reading or writing (`aiofiles.open()` by default)

        :ivar id: `str`, application ID
        :ivar secret: `str`, application secret password
        :ivar token: `str`, application token
        :ivar default_args: `dict`, default arguments for methods. Can be used to
                            set the default timeout, headers, etc.
        :ivar session_factory: function that returns a new instance of :any:`AsyncSession`
        :ivar open_file: async function that opens a file for reading or writing (`aiofiles.open()` by default)

        The following exceptions may be raised by most API requests:

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
    default_args: Dict[str, Any]
    session_factory: AsyncSessionFactory
    session: AsyncSession
    open_file: AsyncOpenFileCallback

    synchronous = False

    def __init__(self,
                 id: str = "",
                 secret: str = "",
                 token: str = "",
                 default_args: Optional[Dict[str, Any]] = None,
                 session_factory: Optional[AsyncSessionFactory] = None,
                 open_file: Optional[AsyncOpenFileCallback] = None):
        self.id = id
        self.secret = secret

        self._token = ""

        self.default_args = {} if default_args is None else default_args

        if session_factory is None:
            if AIOHTTPSession is None:
                raise RuntimeError("aiohttp is not installed. Either install aiohttp or provide a custom session_factory.")

            self.session_factory = AIOHTTPSession
        else:
            self.session_factory = session_factory

        self.session = self.make_session()

        if open_file is None:
            open_file = _default_open_file

        self.open_file = open_file

        self.token = token

    @property
    def token(self) -> str:
        return self._token

    @token.setter
    def token(self, value: str) -> None:
        self._token = value
        self.session.set_token(self._token)

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

    def make_session(self, token: Optional[str] = None) -> AsyncSession:
        """
            Prepares a new :any:`AsyncSession` object with headers needed for API.

            :param token: application token, equivalent to `self.token` if `None`
            :returns: `AsyncSession`
        """

        if token is None:
            token = self.token

        session = self.session_factory()

        if token:
            session.set_token(token)

        return session

    def get_auth_url(self, **kwargs) -> str:
        """
            Get authentication URL for the user to go to.

            :param type: response type ("code" to get the confirmation code or "token" to get the token automatically)
            :param device_id: unique device ID, must be between 6 and 50 characters
            :param device_name: device name, should not be longer than 100 characters
            :param display: indicates whether to use lightweight layout, values other than "popup" are ignored
            :param login_hint: username or email for the account the token is being requested for
            :param scope: list of permissions for the application
            :param optional_scope: list of optional permissions for the application
            :param force_confirm: if True, user will be required to confirm access to the account
                                  even if the user has already granted access for the application
            :param state: The state string, which Yandex.OAuth returns without any changes (<= 1024 characters)

            :returns: authentication URL
        """

        type           = kwargs.get("type")
        device_id      = kwargs.get("device_id")
        device_name    = kwargs.get("device_name")
        display        = kwargs.get("display", "popup")
        login_hint     = kwargs.get("login_hint")
        scope          = kwargs.get("scope")
        optional_scope = kwargs.get("optional_scope")
        force_confirm  = kwargs.get("force_confirm", True)
        state          = kwargs.get("state")

        if type not in {"code", "token"}:
            raise ValueError("type must be either 'code' or 'token'")

        params = {"response_type": type,
                  "client_id":     self.id,
                  "display":       display,
                  "force_confirm": "yes" if force_confirm else "no"}

        if device_id is not None:
            params["device_id"] = device_id

        if device_name is not None:
            params["device_name"] = device_name

        if login_hint is not None:
            params["login_hint"] = login_hint

        if scope is not None:
            params["scope"] = " ".join(scope)

        if optional_scope is not None:
            params["optional_scope"] = " ".join(optional_scope)

        if state is not None:
            params["state"] = state

        return "https://oauth.yandex.ru/authorize?" + urlencode(params)

    def get_code_url(self, **kwargs) -> str:
        """
            Get the URL for the user to get the confirmation code.
            The confirmation code can later be used to get the token.

            :param device_id: unique device ID, must be between 6 and 50 characters
            :param device_name: device name, should not be longer than 100 characters
            :param display: indicates whether to use lightweight layout, values other than "popup" are ignored
            :param login_hint: username or email for the account the token is being requested for
            :param scope: list of permissions for the application
            :param optional_scope: list of optional permissions for the application
            :param force_confirm: if True, user will be required to confirm access to the account
                                  even if the user has already granted access for the application
            :param state: The state string, which Yandex.OAuth returns without any changes (<= 1024 characters)

            :returns: authentication URL
        """

        kwargs["type"] = "code"

        return self.get_auth_url(**kwargs)

    async def get_token(self, code: str, /, **kwargs) -> "TokenObject":
        """
            Get a new token.

            :param code: confirmation code
            :param device_id: unique device ID (between 6 and 50 characters)
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises BadRequestError: invalid or expired code, application ID or secret

            :returns: :any:`TokenObject`
        """

        _apply_default_args(kwargs, self.default_args)

        async with self.session_factory() as session:
            request = GetTokenRequest(session, code, self.id, self.secret, **kwargs)
            await request.asend()

            return await request.aprocess()

    async def refresh_token(self, refresh_token: str, /, **kwargs) -> "TokenObject":
        """
            Refresh an existing token.

            :param refresh_token: the refresh token that was received with the token
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises BadRequestError: invalid or expired refresh token, application ID or secret

            :returns: :any:`TokenObject`
        """

        _apply_default_args(kwargs, self.default_args)

        async with self.session_factory() as session:
            request = RefreshTokenRequest(
                session, refresh_token, self.id, self.secret, **kwargs)
            await request.asend()

            return await request.aprocess()

    async def revoke_token(self, token: Optional[str] = None, /, **kwargs) -> "TokenRevokeStatusObject":
        """
            Revoke the token.

            :param token: token to revoke, equivalent to `self.token` if `None`
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises BadRequestError: token cannot be revoked (not bound to this application, etc.)

            :returns: :any:`TokenRevokeStatusObject`
        """

        _apply_default_args(kwargs, self.default_args)

        if token is None:
            token = self.token

        async with self.session_factory() as session:
            request = RevokeTokenRequest(
                session, token, self.id, self.secret, **kwargs)
            await request.asend()

            return await request.aprocess()

    async def get_disk_info(self, **kwargs) -> "DiskInfoObject":
        """
            Get disk information.

            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: :any:`DiskInfoObject`
        """

        _apply_default_args(kwargs, self.default_args)

        request = DiskInfoRequest(self.session, **kwargs)
        await request.asend()

        return await request.aprocess()

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

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: :any:`AsyncResourceObject`
        """

        _apply_default_args(kwargs, self.default_args)

        request = GetMetaRequest(self.session, path, **kwargs)
        await request.asend()

        return await request.aprocess(yadisk=self)

    async def exists(self, path: str, /, **kwargs) -> bool:
        """
            Check whether `path` exists.

            :param path: path to the resource
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `bool`
        """

        _apply_default_args(kwargs, self.default_args)

        return await _exists(self.get_meta, path, **kwargs)

    async def get_type(self, path: str, /, **kwargs) -> str:
        """
            Get resource type.

            :param path: path to the resource
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: "file" or "dir"
        """

        _apply_default_args(kwargs, self.default_args)

        return await _get_type(self.get_meta, path, **kwargs)

    async def is_file(self, path: str, /, **kwargs) -> bool:
        """
            Check whether `path` is a file.

            :param path: path to the resource
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a file, `False` otherwise (even if it doesn't exist)
        """

        _apply_default_args(kwargs, self.default_args)

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

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
        """

        _apply_default_args(kwargs, self.default_args)

        try:
            return (await self.get_type(path, **kwargs)) == "dir"
        except PathNotFoundError:
            return False

    async def listdir(self, path: str, /, **kwargs) -> AsyncGenerator["AsyncResourceObject", None]:
        """
            Get contents of `path`.

            :param path: path to the directory
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises WrongResourceTypeError: resource is not a directory

            :returns: async generator of :any:`AsyncResourceObject`
        """

        _apply_default_args(kwargs, self.default_args)

        return _listdir(self.get_meta, path, **kwargs)

    async def get_upload_link(self, path: str, /, **kwargs) -> str:
        """
            Get a link to upload the file using the PUT request.

            :param path: destination path
            :param overwrite: `bool`, determines whether to overwrite the destination
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises InsufficientStorageError: cannot upload file due to lack of storage space
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded

            :returns: `str`
        """

        _apply_default_args(kwargs, self.default_args)

        request = GetUploadLinkRequest(self.session, path, **kwargs)
        await request.asend()

        return (await request.aprocess(yadisk=self)).href

    async def _upload(self,
                      get_upload_link_function: Callable[..., Awaitable[str]],
                      file_or_path: AsyncFileOrPath,
                      dst_path: str, /, **kwargs) -> None:
        try:
            timeout = kwargs["timeout"]
        except KeyError:
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

            async def attempt():
                temp_kwargs = dict(kwargs)
                temp_kwargs["n_retries"] = n_retries_for_upload_link
                temp_kwargs["retry_interval"] = 0.0

                link = await get_upload_link_function(dst_path, **temp_kwargs)

                # session.get() doesn't accept some of the passed parameters
                _filter_request_kwargs(temp_kwargs)

                # Disable keep-alive by default, since the upload server is random
                try:
                    temp_kwargs["headers"].setdefault("Connection", "close")
                except KeyError:
                    temp_kwargs["headers"] = {"Connection": "close"}

                data = None

                if generator_factory is None:
                    if await _is_file_seekable(file):
                        await _file_seek(file, file_position)

                    if is_async_func(file.read):
                        data = read_in_chunks(file)
                    else:
                        data = read_in_chunks_sync(file)
                else:
                    data = generator_factory()

                async with await session.send_request("PUT", link, data=data, **temp_kwargs) as response:
                    if response.status != 201:
                        raise await response.get_exception()

            await auto_retry(attempt, n_retries, retry_interval)
        finally:
            if close_file and file is not None:
                await file.close()

    async def upload(self,
                     path_or_file: AsyncFileOrPath,
                     dst_path: str, /, **kwargs) -> AsyncResourceLinkObject:
        """
            Upload a file to disk.

            :param path_or_file: path, file-like object or an async generator function to be uploaded
            :param dst_path: destination path
            :param overwrite: if `True`, the resource will be overwritten if it already exists,
                              an error will be raised otherwise
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

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
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: `str`
        """

        _apply_default_args(kwargs, self.default_args)

        request = GetDownloadLinkRequest(self.session, path, **kwargs)
        await request.asend()

        return (await request.aprocess(yadisk=self)).href

    async def _download(self,
                        get_download_link_function: Callable[..., Awaitable[str]],
                        src_path: str,
                        file_or_path: AsyncFileOrPathDestination, /, **kwargs) -> None:
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

        try:
            timeout = kwargs["timeout"]
        except KeyError:
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

                # Disable keep-alive by default, since the download server is random
                try:
                    temp_kwargs["headers"].setdefault("Connection", "close")
                except KeyError:
                    temp_kwargs["headers"] = {"Connection": "close"}

                if await _is_file_seekable(file):
                    await _file_seek(file, file_position)

                async with await session.send_request("GET", link, **temp_kwargs) as response:
                    await response.download(file.write)

                    if response.status != 200:
                        raise await response.get_exception()

            return await auto_retry(attempt, n_retries, retry_interval)
        finally:
            if close_file and file is not None:
                await file.close()

    async def download(self,
                       src_path: str,
                       path_or_file: AsyncFileOrPathDestination, /, **kwargs) -> AsyncResourceLinkObject:
        """
            Download the file.

            :param src_path: source path
            :param path_or_file: destination path or file-like object
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`AsyncResourceLinkObject`, link to the source resource
        """

        _apply_default_args(kwargs, self.default_args)

        await self._download(self.get_download_link, src_path, path_or_file, **kwargs)
        return AsyncResourceLinkObject.from_path(src_path, yadisk=self)

    async def download_by_link(self,
                               link: str,
                               file_or_path: AsyncFileOrPathDestination, /, **kwargs) -> None:
        """
            Download the file from the link.

            :param link: download link
            :param file_or_path: destination path or file-like object
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
        """

        _apply_default_args(kwargs, self.default_args)

        async def get_link(*args, **kwargs) -> str:
            return link

        await self._download(get_link, "", file_or_path, **kwargs)

    async def remove(self, path: str, /, **kwargs) -> Optional["AsyncOperationLinkObject"]:
        """
            Remove the resource.

            :param path: path to the resource to be removed
            :param permanently: if `True`, the resource will be removed permanently,
                                otherwise, it will be just moved to the trash
            :param md5: `str`, MD5 hash of the file to remove
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises BadRequestError: MD5 check is only available for files
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`AsyncOperationLinkObject` if the operation is performed asynchronously, `None` otherwise
        """

        _apply_default_args(kwargs, self.default_args)

        request = DeleteRequest(self.session, path, **kwargs)
        await request.asend()

        return await request.aprocess(yadisk=self)

    async def mkdir(self, path: str, /, **kwargs) -> AsyncResourceLinkObject:
        """
            Create a new directory.

            :param path: path to the directory to be created
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises DirectoryExistsError: destination path already exists
            :raises InsufficientStorageError: cannot create directory due to lack of storage space
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`AsyncResourceLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)

        request = MkdirRequest(self.session, path, **kwargs)
        await request.asend()

        return await request.aprocess(yadisk=self)

    async def check_token(self, token: Optional[str] = None, /, **kwargs) -> bool:
        """
            Check whether the token is valid.

            :param token: token to check, equivalent to `self.token` if `None`
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: `bool`
        """

        _apply_default_args(kwargs, self.default_args)

        # Any ID will do, doesn't matter whether it exists or not
        fake_operation_id = "0000"

        if token is None:
            token = self.token

        if token == self.token:
            session = self.session
        else:
            session = self.make_session(token)

        try:
            # get_operation_status() doesn't require any permissions, unlike most other requests
            await self._get_operation_status(session, fake_operation_id, **kwargs)
            return True
        except UnauthorizedError:
            return False
        except OperationNotFoundError:
            return True
        finally:
            if session is not self.session:
                await session.close()

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

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: :any:`AsyncTrashResourceObject`
        """

        _apply_default_args(kwargs, self.default_args)

        request = GetTrashRequest(self.session, path, **kwargs)
        await request.asend()

        return await request.aprocess(yadisk=self)

    async def trash_exists(self, path: str, /, **kwargs) -> bool:
        """
            Check whether the trash resource at `path` exists.

            :param path: path to the trash resource
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `bool`
        """

        _apply_default_args(kwargs, self.default_args)

        return await _exists(self.get_trash_meta, path, **kwargs)

    async def copy(self,
                   src_path: str,
                   dst_path: str, /, **kwargs) -> Union[AsyncResourceLinkObject, "AsyncOperationLinkObject"]:
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
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises InsufficientStorageError: cannot complete request due to lack of storage space
            :raises ResourceIsLockedError: resource is locked by another request
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded

            :returns: :any:`AsyncResourceLinkObject` or :any:`AsyncOperationLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)

        request = CopyRequest(self.session, src_path, dst_path, **kwargs)
        await request.asend()

        return await request.aprocess(yadisk=self)

    async def restore_trash(self,
                            path: str,
                            dst_path: Optional[str] = None, /, **kwargs) -> Union[AsyncResourceLinkObject, "AsyncOperationLinkObject"]:
        """
            Restore a trash resource.
            Returns a link to the newly created resource or a link to the asynchronous operation.

            :param path: path to the trash resource to restore
            :param dst_path: destination path
            :param overwrite: `bool`, determines whether the destination can be overwritten
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`AsyncResourceLinkObject` or :any:`AsyncOperationLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)

        kwargs["dst_path"] = dst_path

        request = RestoreTrashRequest(self.session, path, **kwargs)
        await request.asend()

        return await request.aprocess(yadisk=self)

    async def move(self,
                   src_path: str,
                   dst_path: str, /, **kwargs) -> Union["AsyncOperationLinkObject", AsyncResourceLinkObject]:
        """
            Move `src_path` to `dst_path`.

            :param src_path: source path to be moved
            :param dst_path: destination path
            :param overwrite: `bool`, determines whether to overwrite the destination
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`AsyncResourceLinkObject` or :any:`AsyncOperationLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)

        request = MoveRequest(self.session, src_path, dst_path, **kwargs)
        await request.asend()

        return await request.aprocess(yadisk=self)

    async def rename(self,
                     src_path: str,
                     new_name: str, /, **kwargs) -> Union[AsyncResourceLinkObject, "AsyncOperationLinkObject"]:
        """
            Rename `src_path` to have filename `new_name`.
            Does the same as `move()` but changes only the filename.

            :param src_path: source path to be moved
            :param new_name: target filename to rename to
            :param overwrite: `bool`, determines whether to overwrite the destination
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises ValueError: `new_name` is not a valid filename

            :returns: :any:`AsyncResourceLinkObject` or :any:`AsyncOperationLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)

        new_name = new_name.rstrip("/")

        if "/" in new_name or new_name in (".", ".."):
            raise ValueError(f"Invalid filename: {new_name}")

        dst_path = str(PurePosixPath(src_path).parent / new_name)

        return await self.move(src_path, dst_path, **kwargs)

    async def remove_trash(self, path: str, /, **kwargs) -> Optional["AsyncOperationLinkObject"]:
        """
            Remove a trash resource.

            :param path: path to the trash resource to be deleted
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`AsyncOperationLinkObject` if the operation is performed asynchronously, `None` otherwise
        """

        _apply_default_args(kwargs, self.default_args)

        request = DeleteTrashRequest(self.session, path, **kwargs)
        await request.asend()

        return await request.aprocess(yadisk=self)

    async def publish(self, path: str, /, **kwargs) -> AsyncResourceLinkObject:
        """
            Make a resource public.

            :param path: path to the resource to be published
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`AsyncResourceLinkObject`, link to the resource
        """

        _apply_default_args(kwargs, self.default_args)

        request = PublishRequest(self.session, path, **kwargs)
        await request.asend()

        return await request.aprocess(yadisk=self)

    async def unpublish(self, path: str, /, **kwargs) -> AsyncResourceLinkObject:
        """
            Make a public resource private.

            :param path: path to the resource to be unpublished
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`AsyncResourceLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)

        request = UnpublishRequest(self.session, path, **kwargs)
        await request.asend()

        return await request.aprocess(yadisk=self)

    async def save_to_disk(self, public_key: str, /, **kwargs) -> Union[AsyncResourceLinkObject, "AsyncOperationLinkObject"]:
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
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises InsufficientStorageError: cannot upload file due to lack of storage space
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded

            :returns: :any:`AsyncResourceLinkObject` or :any:`AsyncOperationLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)

        request = SaveToDiskRequest(self.session, public_key, **kwargs)
        await request.asend()

        return await request.aprocess(yadisk=self)

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

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: :any:`AsyncPublicResourceObject`
        """

        _apply_default_args(kwargs, self.default_args)

        request = GetPublicMetaRequest(self.session, public_key, **kwargs)
        await request.asend()

        return await request.aprocess(yadisk=self)

    async def public_exists(self, public_key: str, /, **kwargs) -> bool:
        """
            Check whether the public resource exists.

            :param public_key: public key or public URL of the resource
            :param path: relative path to the resource within the public folder
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `bool`
        """

        _apply_default_args(kwargs, self.default_args)

        return await _exists(self.get_public_meta, public_key, **kwargs)

    async def public_listdir(self, public_key: str, /, **kwargs) -> AsyncGenerator["AsyncPublicResourceObject", None]:
        """
            Get contents of a public directory.

            :param public_key: public key or public URL of the resource
            :param path: relative path to the resource in the public folder.
                         By specifying the key of the published folder in `public_key`,
                         you can request contents of any nested folder.
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises WrongResourceTypeError: resource is not a directory

            :returns: async generator of :any:`AsyncPublicResourceObject`
        """

        _apply_default_args(kwargs, self.default_args)

        return _listdir(self.get_public_meta, public_key, **kwargs)

    async def get_public_type(self, public_key: str, /, **kwargs) -> str:
        """
            Get public resource type.

            :param public_key: public key or public URL of the resource
            :param path: relative path to the resource within the public folder
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: "file" or "dir"
        """

        _apply_default_args(kwargs, self.default_args)

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

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `public_key` is a directory, `False` otherwise (even if it doesn't exist)
        """

        _apply_default_args(kwargs, self.default_args)

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

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `public_key` is a file, `False` otherwise (even if it doesn't exist)
        """

        _apply_default_args(kwargs, self.default_args)

        try:
            return (await self.get_public_type(public_key, **kwargs)) == "file"
        except PathNotFoundError:
            return False

    async def trash_listdir(self, path: str, /, **kwargs) -> AsyncGenerator["AsyncTrashResourceObject", None]:
        """
            Get contents of a trash resource.

            :param path: path to the directory in the trash bin
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises WrongResourceTypeError: resource is not a directory

            :returns: async generator of :any:`AsyncTrashResourceObject`
        """

        _apply_default_args(kwargs, self.default_args)

        return _listdir(self.get_trash_meta, path, **kwargs)

    async def get_trash_type(self, path: str, /, **kwargs) -> str:
        """
            Get trash resource type.

            :param path: path to the trash resource
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: "file" or "dir"
        """

        _apply_default_args(kwargs, self.default_args)

        return await _get_type(self.get_trash_meta, path, **kwargs)

    async def is_trash_dir(self, path: str, /, **kwargs) -> bool:
        """
            Check whether `path` is a trash directory.

            :param path: path to the trash resource
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
        """

        _apply_default_args(kwargs, self.default_args)

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

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
        """

        _apply_default_args(kwargs, self.default_args)

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

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: :any:`AsyncPublicResourcesListObject`
        """

        _apply_default_args(kwargs, self.default_args)

        request = GetPublicResourcesRequest(self.session, **kwargs)
        await request.asend()

        return await request.aprocess(yadisk=self)

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

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`AsyncResourceObject`
        """

        _apply_default_args(kwargs, self.default_args)

        request = PatchRequest(self.session, path, properties, **kwargs)
        await request.asend()

        return await request.aprocess(yadisk=self)

    async def get_files(self, **kwargs) -> AsyncGenerator["AsyncResourceObject", None]:
        """
            Get a flat list of all files (that doesn't include directories).

            :param offset: offset from the beginning of the list
            :param limit: number of list elements to be included
            :param media_type: type of files to include in the list
            :param sort: `str`, field to be used as a key to sort children resources
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: async generator of :any:`AsyncResourceObject`
        """

        _apply_default_args(kwargs, self.default_args)

        if kwargs.get("limit") is not None:
            request = FilesRequest(self.session, **kwargs)
            await request.asend()

            for i in (await request.aprocess(yadisk=self)).items:
                yield i

            return

        kwargs.setdefault("offset", 0)
        kwargs["limit"] = 1000

        while True:
            counter = 0
            async for i in self.get_files(**kwargs):
                counter += 1
                yield i

            if counter < kwargs["limit"]:
                break

            kwargs["offset"] += kwargs["limit"]

    async def get_last_uploaded(self, **kwargs) -> AsyncGenerator["AsyncResourceObject", None]:
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

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: async generator of :any:`AsyncResourceObject`
        """

        _apply_default_args(kwargs, self.default_args)

        request = LastUploadedRequest(self.session, **kwargs)
        await request.asend()

        for i in (await request.aprocess(yadisk=self)).items:
            yield i

    async def upload_url(self, url: str, path: str, /, **kwargs) -> "AsyncOperationLinkObject":
        """
            Upload a file from URL.

            :param url: source URL
            :param path: destination path
            :param disable_redirects: `bool`, forbid redirects
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises PathExistsError: destination path already exists
            :raises InsufficientStorageError: cannot upload file due to lack of storage space
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded

            :returns: :any:`AsyncOperationLinkObject`, link to the asynchronous operation
        """

        _apply_default_args(kwargs, self.default_args)

        request = UploadURLRequest(self.session, url, path, **kwargs)
        await request.asend()

        return await request.aprocess(yadisk=self)

    async def get_public_download_link(self, public_key: str, /, **kwargs) -> str:
        """
            Get a download link for a public resource.

            :param public_key: public key or public URL of the resource
            :param path: relative path to the resource within the public folder
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: `str`
        """

        _apply_default_args(kwargs, self.default_args)

        request = GetPublicDownloadLinkRequest(self.session, public_key, **kwargs)
        await request.asend()

        return (await request.aprocess(yadisk=self)).href

    async def download_public(self,
                              public_key: str,
                              file_or_path: AsyncFileOrPathDestination, /, **kwargs) -> AsyncPublicResourceLinkObject:
        """
            Download the public resource.

            :param public_key: public key or public URL of the resource
            :param file_or_path: destination path or file-like object
            :param path: relative path to the resource within the public folder
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`AsyncPublicResourceLinkObject`
        """

        _apply_default_args(kwargs, self.default_args)

        await self._download(
            lambda *args, **kwargs: self.get_public_download_link(public_key, **kwargs),
            "", file_or_path, **kwargs)
        return AsyncPublicResourceLinkObject.from_public_key(public_key, yadisk=self)

    async def get_operation_status(self, operation_id, **kwargs):
        """
            Get operation status.

            :param operation_id: ID of the operation or a link
            :param fields: list of keys to be included in the response
            :param timeout: `float`, `tuple` or `None`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises OperationNotFoundError: requested operation was not found

            :returns: `str`
        """

        _apply_default_args(kwargs, self.default_args)

        return await self._get_operation_status(self.session, operation_id, **kwargs)

    async def _get_operation_status(self, session: AsyncSession, operation_id: str, **kwargs) -> str:
        request = GetOperationStatusRequest(session, operation_id, **kwargs)
        await request.asend()

        return (await request.aprocess()).status
