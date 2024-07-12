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

from typing import Optional, Any, Union

from ..exceptions import (
    RequestError, TooManyRedirectsError,
    RequestTimeoutError, YaDiskConnectionError
)

from .._async_session import AsyncSession, AsyncResponse
from .._common import is_async_func
from ..utils import CaseInsensitiveDict
from .._typing_compat import Dict
from ..types import (
    JSON, AsyncConsumeCallback, Headers, TimeoutParameter, HTTPMethod, AsyncPayload
)

from .. import settings

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
        super().__init__()

        self._response = response
        self.status = response.status

    async def json(self) -> JSON:
        try:
            return await self._response.json()
        except aiohttp.ContentTypeError as e:
            raise ValueError("Expected Content-Type: application/json, got something else") from e
        except aiohttp.ClientError as e:
            raise convert_aiohttp_exception(e) from e

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
            raise convert_aiohttp_exception(e) from e

    async def close(self) -> None:
        await self._response.release()


def convert_timeout(timeout: TimeoutParameter) -> Optional[aiohttp.ClientTimeout]:
    if timeout is ...:
        return convert_timeout(settings.DEFAULT_TIMEOUT)
    elif timeout is None:
        return None
    elif isinstance(timeout, (int, float)):
        return aiohttp.ClientTimeout(sock_connect=timeout, sock_read=timeout)

    connect, read = timeout

    return aiohttp.ClientTimeout(sock_connect=connect, sock_read=read)


DEFAULT_USER_AGENT = "Python/%s.%s aiohttp/%s" % (sys.version_info.major,
                                                  sys.version_info.minor,
                                                  aiohttp.__version__)


class AIOHTTPSession(AsyncSession):
    """
        .. _aiohttp: https://pypi.org/project/aiohttp

        :any:`AsyncSession` implementation using the `aiohttp`_ library.

        All arguments passed in the constructor are directly forwared to :any:`aiohttp.ClientSession`.

        :ivar aiohttp_session: underlying instance of :any:`aiohttp.ClientSession`

        To pass `aiohttp`-specific arguments from :any:`AsyncClient` use :code:`aiohttp_args` keyword argument.

        Usage example:

        .. code:: python

           import yadisk

           async def main():
               async with yadisk.AsyncClient(..., session="aiohttp") as client:
                   await client.get_meta(
                       "/my_file.txt",
                       n_retries=5,
                       aiohttp_args={
                           "proxies": {"https": "http://example.com:1234"},
                           "verify": False
                       }
                    )
    """
    def __init__(self, *args, **kwargs) -> None:
        headers = CaseInsensitiveDict({
            "User-Agent": DEFAULT_USER_AGENT,
            "Accept-Encoding": "gzip, deflate",
            "Accept": "*/*",
            "Connection": "keep-alive"
        })

        headers.update(kwargs.get("headers") or {})

        kwargs["headers"] = headers

        self._session = aiohttp.ClientSession(*args, **kwargs)

    @property
    def aiohttp_session(self) -> aiohttp.ClientSession:
        return self._session

    async def send_request(
        self,
        method: HTTPMethod,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[AsyncPayload] = None,
        headers: Optional[Headers] = None,
        **kwargs
    ) -> AsyncResponse:
        converted_kwargs: Dict[str, Any] = {
            "params": params,
            "data": data,
            "headers": headers
        }

        if "timeout" in kwargs:
            converted_kwargs["timeout"] = convert_timeout(kwargs["timeout"])

        if "aiohttp_args" in kwargs:
            converted_kwargs.update(kwargs["aiohttp_args"] or {})

        try:
            return AIOHTTPResponse(await self._session.request(method, url, **converted_kwargs))
        except aiohttp.ClientError as e:
            raise convert_aiohttp_exception(e) from e

    async def close(self) -> None:
        await self._session.close()
