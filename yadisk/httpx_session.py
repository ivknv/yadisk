# -*- coding: utf-8 -*-

from typing import Optional, Union

from .exceptions import RequestError, TooManyRedirectsError, RequestTimeoutError, YaDiskConnectionError
from .session import Session, Response
from .compat import Dict, Iterable, Tuple

import httpx

__all__ = ["HTTPXSession"]

def convert_httpx_exception(exc: httpx.HTTPError) -> Exception:
    if isinstance(exc, httpx.TooManyRedirects):
        return TooManyRedirectsError(str(exc))
    elif isinstance(exc, httpx.TimeoutException):
        return RequestTimeoutError(str(exc))
    elif isinstance(exc, httpx.ConnectError):
        return YaDiskConnectionError(str(exc))
    elif isinstance(exc, httpx.HTTPError):
        return RequestError(str(exc))
    else:
        return exc

class HTTPXResponse(Response):
    def __init__(self, response: httpx.Response):
        self._response = response
        self.status = response.status_code

    def json(self) -> Response.JSON:
        self._response.read()
        return self._response.json()

    def download(self, consume_callback) -> None:
        try:
            for chunk in self._response.iter_bytes(8192):
                consume_callback(chunk)
        except httpx.HTTPError as e:
            raise convert_httpx_exception(e)

    def release(self) -> None:
        self._response.close()

def convert_timeout(timeout: Optional[Union[float, Tuple[float, float]]]) -> Optional[httpx.Timeout]:
    if timeout is None:
        return None

    if isinstance(timeout, (int, float)):
        return httpx.Timeout(timeout)

    connect, read = timeout

    return httpx.Timeout(connect=connect, pool=connect, read=read, write=read)

class HTTPXSession(Session):
    def __init__(self, *args, **kwargs):
        self._session = httpx.Client(*args, **kwargs)
        self._session.follow_redirects = True

    @property
    def httpx_session(self) -> httpx.Client:
        return self._session

    def set_headers(self, headers: Dict[str, str]) -> None:
        self._session.headers.update(headers)

    def remove_headers(self, headers: Iterable[str]) -> None:
        for h in headers:
            self._session.headers.pop(h, None)

    def send_request(self, method: str, url: str, /, **kwargs) -> Response:
        if "timeout" in kwargs:
            kwargs["timeout"] = convert_timeout(kwargs["timeout"])

        if "data" in kwargs:
            kwargs["content"] = kwargs.pop("data")

        if "httpx_args" in kwargs:
            kwargs.update(kwargs.pop("httpx_args"))

        request_kwargs = {
            "content": kwargs.pop("content", None),
            "params": kwargs.get("params"),
            "cookies": kwargs.get("cookies"),
            "headers": kwargs.get("headers"),
            "extensions": kwargs.get("extensions"),
            "timeout": kwargs.get("timeout", self._session.timeout)
        }

        for i in request_kwargs:
            kwargs.pop(i, None)

        send_kwargs = kwargs

        try:
            request = self._session.build_request(method, url, **request_kwargs)
            return HTTPXResponse(self._session.send(request, **send_kwargs))
        except httpx.HTTPError as e:
            raise convert_httpx_exception(e)

    def close(self) -> None:
        self._session.close()
