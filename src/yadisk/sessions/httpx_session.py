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

from .._session import Session, Response
from ..types import JSON, ConsumeCallback, HTTPMethod

from ._httpx_common import *

import httpx

__all__ = ["HTTPXSession"]


class HTTPXResponse(Response):
    def __init__(self, response: httpx.Response):
        super().__init__()

        self._response = response
        self.status = response.status_code

    def json(self) -> JSON:
        try:
            self._response.read()
        except httpx.HTTPError as e:
            raise convert_httpx_exception(e) from e
        except httpx.StreamConsumed as e:
            raise ValueError(f"Could not parse JSON: {e}") from e

        return self._response.json()

    def download(self, consume_callback: ConsumeCallback) -> None:
        try:
            for chunk in self._response.iter_bytes(8192):
                consume_callback(chunk)
        except httpx.HTTPError as e:
            raise convert_httpx_exception(e) from e

    def close(self) -> None:
        self._response.close()


class HTTPXSession(Session):
    """
        .. _httpx: https://pypi.org/project/httpx

        :any:`Session` implementation using the `httpx`_ library.

        .. _httpx.Client: https://www.python-httpx.org/api/#client

        All arguments passed in the constructor are directly forwared to `httpx.Client`_.

        :ivar httpx_client: underlying instance of `httpx.Client`_

        To pass `httpx`-specific arguments from :any:`Client` use :code:`httpx_args` keyword argument.

        Usage example:

        .. code:: python

           import yadisk

           with yadisk.Client(..., session="httpx") as client:
               client.get_meta(
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
        self._client = httpx.Client(*args, **kwargs)
        self._client.follow_redirects = True

    @property
    def httpx_client(self) -> httpx.Client:
        return self._client

    def send_request(self, method: HTTPMethod, url: str, **kwargs) -> Response:
        request_kwargs, send_kwargs = convert_args_for_httpx(self._client, kwargs)

        try:
            request = self._client.build_request(method, url, **request_kwargs)
            return HTTPXResponse(self._client.send(request, **send_kwargs))
        except httpx.HTTPError as e:
            raise convert_httpx_exception(e) from e

    def close(self) -> None:
        self._client.close()
