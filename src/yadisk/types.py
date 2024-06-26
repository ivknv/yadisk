# -*- coding: utf-8 -*-

from typing import Any, Optional, Union, TYPE_CHECKING, Protocol, BinaryIO, Literal
from typing_extensions import TypeAlias
from .compat import (
    Dict, List, Tuple, Callable, Awaitable,
    Iterator, AsyncIterator
)

if TYPE_CHECKING:
    from .session import Session, Response
    from .async_session import AsyncSession, AsyncResponse
    from .client import Client
    from .async_client import AsyncClient

__all__ = [
    "JSON", "TimeoutParameter", "Headers", "Payload", "ConsumeCallback",
    "AsyncPayload", "AsyncConsumeCallback", "AnyResponse", "AnyClient",
    "AsyncFileLike", "BinaryAsyncFileLike", "FileOrPath", "FileOrPathDestination",
    "AsyncFileOrPath", "AsyncFileOrPathDestination", "SessionFactory", "AsyncSessionFactory",
    "FileOpenMode", "OpenFileCallback", "AsyncOpenFileCallback", "HTTPMethod",
    "SessionName", "AsyncSessionName", "OperationStatus"
]

JSON: TypeAlias = Union[Dict, List, str, int, float, None]
TimeoutParameter: TypeAlias = Optional[Union[float, Tuple[Optional[float], Optional[float]]]]
Headers: TypeAlias = Dict[str, str]

Payload: TypeAlias = Union[bytes, Iterator[bytes]]
ConsumeCallback: TypeAlias = Callable[[bytes], None]

AsyncPayload: TypeAlias = Union[bytes, Iterator[bytes], AsyncIterator[bytes]]
AsyncConsumeCallback: TypeAlias = Union[Callable[[bytes], None], Callable[[bytes], Awaitable[None]]]

AnyResponse: TypeAlias = Union["Response", "AsyncResponse"]
AnySession: TypeAlias = Union["Session", "AsyncSession"]
AnyClient: TypeAlias = Union["Client", "AsyncClient"]


class AsyncFileLike(Protocol):
    async def read(self, size: int = ..., /) -> Union[str, bytes]: ...
    async def write(self, buffer: Any, /) -> int: ...
    async def seek(self, pos: int, whence: int = ..., /) -> int: ...
    async def tell(self) -> int: ...


class BinaryAsyncFileLike(Protocol):
    async def read(self, size: int = ..., /) -> bytes: ...
    async def write(self, buffer: Any, /) -> int: ...
    async def seek(self, pos: int, whence: int = ..., /) -> int: ...
    async def tell(self) -> int: ...


FileOrPath: TypeAlias = Union[
    str,
    bytes,
    BinaryIO,
    Callable[[], Iterator[bytes]]
]

FileOrPathDestination: TypeAlias = Union[
    str,
    bytes,
    BinaryIO,
]

AsyncFileOrPath: TypeAlias = Union[
    str,
    bytes,
    BinaryIO,
    AsyncFileLike,
    Callable[[], AsyncIterator[bytes]]
]

AsyncFileOrPathDestination: TypeAlias = Union[
    str,
    bytes,
    BinaryIO,
    BinaryAsyncFileLike
]

SessionFactory: TypeAlias = Callable[[], "Session"]
AsyncSessionFactory: TypeAlias = Callable[[], "AsyncSession"]

FileOpenMode: TypeAlias = Union[Literal["rb"], Literal["wb"]]
OpenFileCallback: TypeAlias = Callable[[Union[str, bytes], FileOpenMode], BinaryIO]
AsyncOpenFileCallback: TypeAlias = Union[
    Callable[[Union[str, bytes], FileOpenMode], Awaitable[BinaryAsyncFileLike]],
    Callable[[Union[str, bytes], FileOpenMode], Awaitable[BinaryIO]],
]

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

SessionName: TypeAlias = Union[Literal["httpx"], Literal["pycurl"], Literal["requests"]]
AsyncSessionName: TypeAlias = Union[Literal["aiohttp"], Literal["httpx"]]

OperationStatus: TypeAlias = Union[Literal["in-progress"], Literal["success"], Literal["failed"]]
