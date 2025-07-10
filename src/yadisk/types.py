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

from typing import Any, Optional, TypedDict, Union, TYPE_CHECKING, Protocol, BinaryIO, Literal
from ._typing_compat import (
    Dict, List, Tuple, Callable, Awaitable,
    Iterator, AsyncIterator, Mapping, TypeAlias
)

if TYPE_CHECKING:  # pragma: no cover
    from ._session import Session, Response
    from ._async_session import AsyncSession, AsyncResponse
    from ._client import Client
    from ._async_client import AsyncClient

__all__ = [
    "JSON",
    "AnyClient",
    "AnyResponse",
    "AsyncConsumeCallback",
    "AsyncFileLike",
    "AsyncFileOrPath",
    "AsyncFileOrPathDestination",
    "AsyncOpenFileCallback",
    "AsyncPayload",
    "AsyncSessionFactory",
    "AsyncSessionName",
    "AvailableUntilVerbose",
    "BinaryAsyncFileLike",
    "ConsumeCallback",
    "ExternalOrganizationIdVerbose",
    "FileOpenMode",
    "FileOrPath",
    "FileOrPathDestination",
    "HTTPMethod",
    "Headers",
    "OpenFileCallback",
    "OperationStatus",
    "PasswordVerbose",
    "Payload",
    "PublicSettings",
    "PublicSettingsAccess",
    "SessionFactory",
    "SessionName",
    "TimeoutParameter",
]

#: JSON data (parsed)
JSON: TypeAlias = Union[Dict, List, str, int, float, None]

#: Request timeout (in seconds). Can be a single number, None or a tuple.
#: If the timeout is specified as a tuple, then the first value is the
#: connect timeout, and the second value is the read timeout.
#: Otherwise, both connect and read timeouts are set to the same value.
#: A value of None means no timeout.
#: If the timeout's value is :code:`...`, the default timeout is used
#: (either :any:`settings.DEFAULT_TIMEOUT` or :any:`settings.DEFAULT_UPLOAD_TIMEOUT`)
TimeoutParameter: TypeAlias = Optional[
    Union[
        float,
        Tuple[Optional[float], Optional[float]]
    ]
]

#: Type used for passing HTTP request headers
Headers: TypeAlias = Mapping[str, str]

#: Request payload - data to be uploaded
Payload: TypeAlias = Union[bytes, Iterator[bytes]]

#: Callback function that is invoked to consume the streamed HTTP response body
ConsumeCallback: TypeAlias = Callable[[bytes], None]

#: Request payload - data to be uploaded (async variant)
AsyncPayload: TypeAlias = Union[bytes, Iterator[bytes], AsyncIterator[bytes]]

#: Callback function (may be asynchronous) that is invoked to consume the
#: streamed HTTP response body
AsyncConsumeCallback: TypeAlias = Union[Callable[[bytes], None], Callable[[bytes], Awaitable[None]]]

#: :any:`Response` or :any:`AsyncResponse`
AnyResponse: TypeAlias = Union["Response", "AsyncResponse"]

#: :any:`Session` or :any:`AsyncSession`
AnySession: TypeAlias = Union["Session", "AsyncSession"]

#: :any:`Client` or :any:`AsyncClient`
AnyClient: TypeAlias = Union["Client", "AsyncClient"]


class AsyncFileLike(Protocol):
    """
        This protocol describes the bare minimum set of required methods for
        an async file-like object (open in either binary or unicode mode).
    """

    async def read(self, size: int = ..., /) -> Union[str, bytes]:
        """
            Reads `size` bytes or characters.

            :param size: `int`, number of bytes/characters to read from the file
            :returns: data that was read from the file
        """
        ...

    async def write(self, buffer: Any, /) -> int:
        """
            Writes data (contained in `buffer`).

            :param buffer: data to be written
            :returns: the number of written bytes/characters
        """
        ...

    async def seek(self, pos: int, whence: int = ..., /) -> int:
        """
            Performs a seek operation on a file.

            :param pos: `int`, position to seek to
            :param whence: `int`, 0 (seek absolute position), 1 (seek relative
                            to current position) or 2 (seek to file's end)

            :returns: `int`, absolute position within the file after the seek operation
        """
        ...

    async def tell(self) -> int:
        """
            Returns current position within the file.

            :returns: `int`, current position within the file
        """
        ...


class BinaryAsyncFileLike(Protocol):
    """
        This protocol describes the bare minimum set of required methods for
        an async file-like object open in binary mode.
    """

    async def read(self, size: int = ..., /) -> bytes:
        """
            Reads `size` bytes.

            :param size: `int`, number of bytes/characters to read from the file
            :returns: data that was read from the file
        """
        ...

    async def write(self, buffer: Any, /) -> int:
        """
            Writes data (contained in `buffer`).

            :param buffer: data to be written
            :returns: the number of written bytes
        """
        ...

    async def seek(self, pos: int, whence: int = ..., /) -> int:
        """
            Performs a seek operation on a file.

            :param pos: `int`, position to seek to
            :param whence: `int`, 0 (seek absolute position), 1 (seek relative
                            to current position) or 2 (seek to file's end)

            :returns: `int`, absolute position within the file after the seek operation
        """
        ...

    async def tell(self) -> int:
        """
            Returns current position within the file.

            :returns: `int`, current position within the file
        """
        ...


#: This is used to specify a source file to upload
FileOrPath: TypeAlias = Union[
    str,
    bytes,
    BinaryIO,
    Callable[[], Iterator[bytes]]
]

#: This is used to specify a destination file to download into
FileOrPathDestination: TypeAlias = Union[
    str,
    bytes,
    BinaryIO,
]

#: This is used to specify a source file to upload (async variant)
AsyncFileOrPath: TypeAlias = Union[
    str,
    bytes,
    BinaryIO,
    AsyncFileLike,
    Callable[[], AsyncIterator[bytes]]
]

#: This is used to specify a destination file to download into (async variant)
AsyncFileOrPathDestination: TypeAlias = Union[
    str,
    bytes,
    BinaryIO,
    BinaryAsyncFileLike
]

#: Function that returns an instance of :any:`Session`
SessionFactory: TypeAlias = Callable[[], "Session"]

#: Function that returns an instance of :any:`AsyncSession`
AsyncSessionFactory: TypeAlias = Callable[[], "AsyncSession"]

#: File mode for :any:`OpenFileCallback` and :any:`AsyncOpenFileCallback`
FileOpenMode: TypeAlias = Union[Literal["rb"], Literal["wb"]]

#: Function that is used for opening local files (like :any:`open`)
OpenFileCallback: TypeAlias = Callable[[Union[str, bytes], FileOpenMode], BinaryIO]

#: Function that is used for opening local files (async variant)
AsyncOpenFileCallback: TypeAlias = Union[
    Callable[[Union[str, bytes], FileOpenMode], Awaitable[BinaryAsyncFileLike]],
    Callable[[Union[str, bytes], FileOpenMode], Awaitable[BinaryIO]],
]

#: HTTP request method
HTTPMethod: TypeAlias = Union[
    Literal["GET"],
    Literal["POST"],
    Literal["PUT"],
    Literal["PATCH"],
    Literal["DELETE"],
    Literal["OPTIONS"],
    Literal["HEAD"],
    Literal["CONNECT"],
    Literal["TRACE"],
]

#: Valid session name (see :doc:`/api_reference/sessions`)
SessionName: TypeAlias = Union[Literal["httpx"], Literal["pycurl"], Literal["requests"]]

#: Valid asynchronous session name (see :doc:`/api_reference/sessions`)
AsyncSessionName: TypeAlias = Union[Literal["aiohttp"], Literal["httpx"]]

#: Yandex.Disk's asynchronous operation status
OperationStatus: TypeAlias = Union[Literal["in-progress"], Literal["success"], Literal["failed"]]


class PublicSettings(TypedDict, total=False):
    """
        Public settings of a shared resource. This type describes the input for
        requests that modify public settings. For the related response object,
        see :any:`PublicSettingsObject`.

        :ivar available_until: `int`, timestamp indicating the expiration date of the link
        :ivar read_only: `bool`, whether the resource is read-only
        :ivar available_until_verbose: :any:`AvailableUntilVerbose`, verbose information about the expiration date
        :ivar password: `str`, password to access the resource
        :ivar password_verbose: :any:`PasswordVerbose`, verbose information about the password
        :ivar external_organization_id: `str`, external organization ID
        :ivar external_organization_id_verbose: :any:`ExternalOrganizationIdVerbose`,
            verbose information about the external organization ID
        :ivar accesses: `List[PublicSettingsAccess]`, list of access settings

        .. note::

           It appears that passing :code:`available_until` as an empty string
           disables the expiration date. Similarly, password can be disabled
           by passing :code:`False` or :code:`0`. This is not officially
           documented, though.
    """

    available_until: Union[int, str]
    read_only: bool
    available_until_verbose: "AvailableUntilVerbose"
    password: Union[str, Literal[False, 0]]
    password_verbose: "PasswordVerbose"
    external_organization_id: str
    external_organization_id_verbose: "ExternalOrganizationIdVerbose"
    accesses: List["PublicSettingsAccess"]


class AvailableUntilVerbose(TypedDict):
    """
        Verbose information about the expiration date of a shared resource.

        :ivar enabled: `bool`, whether the expiration date is enabled
        :ivar value: `int`, timestamp indicating the expiration date
    """

    enabled: bool
    value: int


class PasswordVerbose(TypedDict):
    """
        Verbose information about the password of a shared resource.

        :ivar enabled: `bool`, whether the password is enabled
        :ivar value: `str`, password to access the resource
    """

    enabled: bool
    value: str


class ExternalOrganizationIdVerbose(TypedDict):
    """
        Verbose information about the external organization ID of a shared resource.

        :ivar enabled: `bool`, whether the external organization ID is enabled
        :ivar value: `str`, external organization ID
    """

    enabled: bool
    value: str


class PublicSettingsAccess(TypedDict, total=False):
    """
        Access settings of a shared resource.

        :ivar macros: `List[Union[Literal["employees"], Literal["all"]]],`,
            specifies who has access to the shared resource, must contain only
            one element
        :ivar org_id: `int`, organization ID
        :ivar user_ids: `List[str]`, list of user IDs
        :ivar group_ids: `List[int]`, list of group IDs
        :ivar department_ids: `List[int]`, list of department IDs
        :ivar rights: `list[str]`, list of access rights

        Valid access rights:

        - `write`: write access
        - `read`: read access
        - `read_without_download`: read access without download
        - `read_with_password`: read access with password
        - `read_with_password_without_download`: read access with password and without download
    """

    macros: List[Union[Literal["employees"], Literal["all"]]]
    org_id: int
    user_ids: List[str]
    group_ids: List[int]
    department_ids: List[int]
    rights: List[
        Union[
            Literal["write"],
            Literal["read"],
            Literal["read_without_download"],
            Literal["read_with_password"],
            Literal["read_with_password_without_download"]
        ]
    ]
