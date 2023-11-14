# -*- coding: utf-8 -*-

from typing import Optional, Any, Union

from ..common import CaseInsensitiveDict

from ..exceptions import (
    RequestError, TooManyRedirectsError,
    RequestTimeoutError, YaDiskConnectionError
)

from ..async_session import AsyncSession, AsyncResponse
from ..compat import Iterable
from ..common import is_async_func
from ..types import JSON, AsyncConsumeCallback, Headers, TimeoutParameter, HTTPMethod

import aiohttp
import sys

__all__ = ["AIOHTTPSession"]

def convert_aiohttp_exception(exc: aiohttp.ClientError) -> Union[RequestError, aiohttp.ClientError]:
    if isinstance(exc, aiohttp.TooManyRedirects):
        return TooManyRedirectsError(str(exc))
    elif isinstance(exc, aiohttp.ServerTimeoutError):
        return RequestTimeoutError(str(exc))
    elif isinstance(exc, aiohttp.ClientConnectionError):
        return YaDiskConnectionError(str(exc))
    elif isinstance(exc, aiohttp.ClientError):
        return RequestError(str(exc))
    else:
        return exc

class AIOHTTPResponse(AsyncResponse):
    def __init__(self, response: aiohttp.ClientResponse):
        self._response = response
        self.status = response.status

    async def json(self) -> JSON:
        return await self._response.json()

    async def download(self, consume_callback: AsyncConsumeCallback) -> None:
        callback: Any = consume_callback

        try:
            if is_async_func(consume_callback):
                async for chunk in self._response.content.iter_chunked(8192):
                    await callback(chunk)
            else:
                async for chunk in self._response.content.iter_chunked(8192):
                    callback(chunk)
        except aiohttp.ClientError as e:
            raise convert_aiohttp_exception(e)

    async def close(self) -> None:
        await self._response.release()

def convert_timeout(timeout: TimeoutParameter) -> Optional[aiohttp.ClientTimeout]:
    if timeout is None:
        return None

    if isinstance(timeout, (int, float)):
        return aiohttp.ClientTimeout(sock_connect=timeout, sock_read=timeout)

    connect, read = timeout

    return aiohttp.ClientTimeout(sock_connect=connect, sock_read=read)

DEFAULT_USER_AGENT = "Python/%s.%s aiohttp/%s" % (sys.version_info.major,
                                                  sys.version_info.minor,
                                                  aiohttp.__version__)

class AIOHTTPSession(AsyncSession):
    def __init__(self, *args, **kwargs):
        headers = CaseInsensitiveDict({
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept-Encoding": "gzip, deflate",
            "Accept": "*/*",
            "Connection": "keep-alive"
        })

        headers.update(kwargs.get("headers", {}))

        kwargs["headers"] = headers

        self._session = aiohttp.ClientSession(*args, **kwargs)

    @property
    def aiohttp_session(self) -> aiohttp.ClientSession:
        return self._session

    def set_headers(self, headers: Headers) -> None:
        self._session.headers.update(headers)

    def remove_headers(self, headers: Iterable[str]) -> None:
        for h in headers:
            self._session.headers.pop(h, None)

    async def send_request(self, method: HTTPMethod, url: str, **kwargs) -> AsyncResponse:
        if "timeout" in kwargs:
            kwargs["timeout"] = convert_timeout(kwargs["timeout"])

        kwargs.pop("stream", None)

        if "aiohttp_args" in kwargs:
            kwargs.update(kwargs.pop("aiohttp_args"))

        try:
            return AIOHTTPResponse(await self._session.request(method, url, **kwargs))
        except aiohttp.ClientError as e:
            raise convert_aiohttp_exception(e)

    async def close(self) -> None:
        await self._session.close()
