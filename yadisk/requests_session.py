# -*- coding: utf-8 -*-

from .exceptions import RequestError, TooManyRedirectsError, RequestTimeoutError, YaDiskConnectionError
from .session import Session, Response
from .compat import Dict, Iterable
from .common import CaseInsensitiveDict

import threading

import requests

__all__ = ["RequestsSession"]

def convert_requests_exception(exc: requests.RequestException) -> Exception:
    if isinstance(exc, requests.exceptions.TooManyRedirects):
        return TooManyRedirectsError(str(exc))
    elif isinstance(exc, requests.exceptions.Timeout):
        return RequestTimeoutError(str(exc))
    elif isinstance(exc, requests.exceptions.ConnectionError):
        return YaDiskConnectionError(str(exc))
    elif isinstance(exc, requests.RequestException):
        return RequestError(str(exc))
    else:
        return exc

class RequestsResponse(Response):
    def __init__(self, response: requests.Response):
        self._response = response
        self.status = response.status_code

    def json(self) -> Response.JSON:
        return self._response.json()

    def download(self, consume_callback) -> None:
        try:
            for chunk in self._response.iter_content(8192):
                consume_callback(chunk)
        except requests.RequestException as e:
            raise convert_requests_exception(e)

    def release(self) -> None:
        self._response.close()

class RequestsSession(Session):
    def __init__(self, *args, **kwargs):
        self._args, self._kwargs = args, kwargs
        self._local = threading.local()
        self._headers = CaseInsensitiveDict()

    @property
    def requests_session(self) -> requests.Session:
        if not hasattr(self._local, "session"):
            self._local.session = requests.Session(*self._args, **self._kwargs)

        return self._local.session

    def set_headers(self, headers: Dict[str, str]) -> None:
        self._headers.update(headers)

    def remove_headers(self, headers: Iterable[str]) -> None:
        for h in headers:
            self._headers.pop(h, None)

    def send_request(self, method: str, url: str, /, **kwargs) -> Response:
        headers = CaseInsensitiveDict(self.requests_session.headers)
        headers.update(self._headers)

        if "requests_args" in kwargs:
            kwargs.update(kwargs.pop("requests_args"))

        headers.update(kwargs.get("headers", {}))

        kwargs["headers"] = headers

        try:
            return RequestsResponse(self.requests_session.request(method, url, **kwargs))
        except requests.exceptions.RequestException as e:
            raise convert_requests_exception(e)

    def close(self) -> None:
        self.requests_session.close()
