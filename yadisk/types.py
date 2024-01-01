# -*- coding: utf-8 -*-

from typing import Any, Optional, Union, TYPE_CHECKING, Protocol, BinaryIO, Literal
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
    "SessionName", "AsyncSessionName"
]

JSON = Union[Dict, List, str, int, float, None]
TimeoutParameter = Optional[Union[float, Tuple[Optional[float], Optional[float]]]]
Headers = Dict[str, str]

Payload = Union[bytes, Iterator[bytes]]
ConsumeCallback = Callable[[bytes], None]

AsyncPayload = Union[bytes, Iterator[bytes], AsyncIterator[bytes]]
AsyncConsumeCallback = Union[Callable[[bytes], None], Callable[[bytes], Awaitable[None]]]

AnyResponse = Union["Response", "AsyncResponse"]
AnySession = Union["Session", "AsyncSession"]
AnyClient = Union["Client", "AsyncClient"]

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

FileOrPath = Union[
    str,
    bytes,
    BinaryIO,
    Callable[[], Iterator[bytes]]
]

FileOrPathDestination = Union[
    str,
    bytes,
    BinaryIO,
]

AsyncFileOrPath = Union[
    str,
    bytes,
    BinaryIO,
    AsyncFileLike,
    Callable[[], AsyncIterator[bytes]]
]

AsyncFileOrPathDestination = Union[
    str,
    bytes,
    BinaryIO,
    BinaryAsyncFileLike
]

SessionFactory = Callable[[], "Session"]
AsyncSessionFactory = Callable[[], "AsyncSession"]

FileOpenMode = Union[Literal["rb"], Literal["wb"]]
OpenFileCallback = Callable[[Union[str, bytes], FileOpenMode], BinaryIO]
AsyncOpenFileCallback = Union[
    Callable[[Union[str, bytes], FileOpenMode], Awaitable[BinaryAsyncFileLike]],
    Callable[[Union[str, bytes], FileOpenMode], Awaitable[BinaryIO]],
]

HTTPMethod = Union[
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

SessionName = Union[Literal["httpx"], Literal["pycurl"], Literal["requests"]]
AsyncSessionName = Union[Literal["aiohttp"], Literal["httpx"]]
