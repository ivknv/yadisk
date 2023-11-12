# -*- coding: utf-8 -*-

from typing import Any, Optional, Union, TYPE_CHECKING, Protocol, BinaryIO
from .compat import (
    Dict, List, Tuple, Generator, AsyncGenerator, Callable, Awaitable,
    AsyncIterable
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
    "AsyncFileOrPath", "AsyncFileOrPathDestination", "SessionFactory", "AsyncSessionFactory"
]

JSON = Union[Dict, List, str, int, float, None]
TimeoutParameter = Optional[Union[float, Tuple[Optional[float], Optional[float]]]]
Headers = Dict[str, str]

Payload = Union[bytes, Generator[bytes, None, None]]
ConsumeCallback = Callable[[bytes], None]

AsyncPayload = Union[bytes, Generator[bytes, None, None], AsyncGenerator[bytes, None]]
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
    Callable[[], AsyncIterable[bytes]]
]

AsyncFileOrPathDestination = Union[
    str,
    bytes,
    BinaryIO,
    BinaryAsyncFileLike
]

SessionFactory = Callable[[], "Session"]
AsyncSessionFactory = Callable[[], "AsyncSession"]
