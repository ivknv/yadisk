# -*- coding: utf-8 -*-

from typing import Any

from ..async_session import AsyncSession, AsyncResponse
from ..compat import Iterable
from ..types import JSON, AsyncConsumeCallback, Headers, HTTPMethod
from ..common import is_async_func

from .httpx_common import *

import httpx

__all__ = ["AsyncHTTPXSession"]

class AsyncHTTPXResponse(AsyncResponse):
    def __init__(self, response: httpx.Response):
        self._response = response
        self.status = response.status_code

    async def json(self) -> JSON:
        await self._response.aread()
        return self._response.json()

    async def download(self, consume_callback: AsyncConsumeCallback) -> None:
        callback: Any = consume_callback

        try:
            if is_async_func(consume_callback):
                async for chunk in self._response.aiter_bytes(8192):
                    await callback(chunk)
            else:
                async for chunk in self._response.aiter_bytes(8192):
                    callback(chunk)
        except httpx.HTTPError as e:
            raise convert_httpx_exception(e)

    async def close(self) -> None:
        await self._response.aclose()

class AsyncHTTPXSession(AsyncSession):
    """
        :any:`AsyncSession` implementation using the :code:`httpx` library.

        .. _httpx.AsyncClient: https://www.python-httpx.org/api/#asyncclient

        All arguments passed in the constructor are directly forwared to `httpx.AsyncClient`_.

        :ivar httpx_client: underlying instance of `httpx.AsyncClient`_

        To pass `httpx`-specific arguments from :any:`AsyncClient` use :code:`httpx_args` keyword argument.

        Usage example:

        .. code:: python

           import yadisk
           from yadisk.sessions.async_httpx_session import AsyncHTTPXSession

           async def main():
               async with yadisk.AsyncClient(..., session_factory=AsyncHTTPXSession) as client:
                   await client.get_meta(
                       "/my_file.txt",
                       n_retries=5,
                       httpx_args={
                           "proxies":"http://localhost:11234",
                           "verify": False,
                           "max_redirects": 10
                       }
                    )
    """

    def __init__(self, *args, **kwargs):
        self._session = httpx.AsyncClient(*args, **kwargs)
        self._session.follow_redirects = True

    @property
    def httpx_session(self) -> httpx.AsyncClient:
        return self._session

    def set_headers(self, headers: Headers) -> None:
        self._session.headers.update(headers)

    def remove_headers(self, headers: Iterable[str]) -> None:
        for h in headers:
            self._session.headers.pop(h, None)

    async def send_request(self, method: HTTPMethod, url: str, **kwargs) -> AsyncResponse:
        request_kwargs, send_kwargs = convert_args_for_httpx(self._session, kwargs)

        try:
            request = self._session.build_request(method, url, **request_kwargs)
            return AsyncHTTPXResponse(await self._session.send(request, **send_kwargs))
        except httpx.HTTPError as e:
            raise convert_httpx_exception(e)

    async def close(self) -> None:
        await self._session.aclose()
