# -*- coding: utf-8 -*-

from ..session import Session, Response
from ..compat import Iterable
from ..types import JSON, ConsumeCallback, Headers, HTTPMethod

from .httpx_common import *

import httpx

__all__ = ["HTTPXSession"]

class HTTPXResponse(Response):
    def __init__(self, response: httpx.Response):
        self._response = response
        self.status = response.status_code

    def json(self) -> JSON:
        self._response.read()
        return self._response.json()

    def download(self, consume_callback: ConsumeCallback) -> None:
        try:
            for chunk in self._response.iter_bytes(8192):
                consume_callback(chunk)
        except httpx.HTTPError as e:
            raise convert_httpx_exception(e)

    def close(self) -> None:
        self._response.close()

class HTTPXSession(Session):
    def __init__(self, *args, **kwargs):
        self._session = httpx.Client(*args, **kwargs)
        self._session.follow_redirects = True

    @property
    def httpx_session(self) -> httpx.Client:
        return self._session

    def set_headers(self, headers: Headers) -> None:
        self._session.headers.update(headers)

    def remove_headers(self, headers: Iterable[str]) -> None:
        for h in headers:
            self._session.headers.pop(h, None)

    def send_request(self, method: HTTPMethod, url: str, **kwargs) -> Response:
        request_kwargs, send_kwargs = convert_args_for_httpx(self._session, kwargs)

        try:
            request = self._session.build_request(method, url, **request_kwargs)
            return HTTPXResponse(self._session.send(request, **send_kwargs))
        except httpx.HTTPError as e:
            raise convert_httpx_exception(e)

    def close(self) -> None:
        self._session.close()
