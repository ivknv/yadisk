# -*- coding: utf-8 -*-

from ..session import Session, Response
from ..types import JSON, ConsumeCallback, Headers, HTTPMethod

from .httpx_common import *

import httpx

__all__ = ["HTTPXSession"]


class HTTPXResponse(Response):
    def __init__(self, response: httpx.Response):
        self._response = response

    def status(self) -> int:
        return self._response.status_code

    def json(self) -> JSON:
        self._response.read()
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
                       "proxies":"http://localhost:11234",
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

    def set_headers(self, headers: Headers) -> None:
        self._client.headers.update(headers)

    def send_request(self, method: HTTPMethod, url: str, **kwargs) -> Response:
        request_kwargs, send_kwargs = convert_args_for_httpx(self._client, kwargs)

        try:
            request = self._client.build_request(method, url, **request_kwargs)
            return HTTPXResponse(self._client.send(request, **send_kwargs))
        except httpx.HTTPError as e:
            raise convert_httpx_exception(e) from e

    def close(self) -> None:
        self._client.close()
