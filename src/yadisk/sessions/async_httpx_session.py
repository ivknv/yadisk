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

from typing import Any

from .._async_session import AsyncSession, AsyncResponse
from ..types import JSON, AsyncConsumeCallback, HTTPMethod
from .._common import is_async_func

from ._httpx_common import *

import httpx

__all__ = ["AsyncHTTPXSession"]


class AsyncHTTPXResponse(AsyncResponse):
    def __init__(self, response: httpx.Response):
        super().__init__()

        self._response = response
        self.status = response.status_code

    async def json(self) -> JSON:
        try:
            await self._response.aread()
        except httpx.HTTPError as e:
            raise convert_httpx_exception(e) from e
        except httpx.StreamConsumed as e:
            raise ValueError(f"Could not parse JSON: {e}") from e

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
            raise convert_httpx_exception(e) from e

    async def close(self) -> None:
        await self._response.aclose()


class AsyncHTTPXSession(AsyncSession):
    """
        .. _httpx: https://pypi.org/project/httpx

        :any:`AsyncSession` implementation using the `httpx`_ library.

        .. _httpx.AsyncClient: https://www.python-httpx.org/api/#asyncclient

        All arguments passed in the constructor are directly forwared to `httpx.AsyncClient`_.

        :ivar httpx_client: underlying instance of `httpx.AsyncClient`_

        To pass `httpx`-specific arguments from :any:`AsyncClient` use :code:`httpx_args` keyword argument.

        Usage example:

        .. code:: python

           import yadisk

           async def main():
               async with yadisk.AsyncClient(..., session="httpx") as client:
                   await client.get_meta(
                       "/my_file.txt",
                       n_retries=5,
                       httpx_args={
                           "proxy": "http://localhost:11234",
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

    async def send_request(self, method: HTTPMethod, url: str, **kwargs) -> AsyncResponse:
        request_kwargs, send_kwargs = convert_args_for_httpx(self._session, kwargs)

        try:
            request = self._session.build_request(method, url, **request_kwargs)
            return AsyncHTTPXResponse(await self._session.send(request, **send_kwargs))
        except httpx.HTTPError as e:
            raise convert_httpx_exception(e) from e

    async def close(self) -> None:
        await self._session.aclose()
