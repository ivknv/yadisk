# -*- coding: utf-8 -*-

from ..exceptions import (
    RequestError, TooManyRedirectsError,
    RequestTimeoutError, YaDiskConnectionError
)

from ..session import Session, Response
from ..compat import Iterable
from ..common import CaseInsensitiveDict
from ..types import JSON, ConsumeCallback, Headers, HTTPMethod

from typing import Union

import threading
import weakref

import requests

__all__ = ["RequestsSession"]

def convert_requests_exception(exc: requests.RequestException) -> Union[RequestError, requests.RequestException]:
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

    def json(self) -> JSON:
        return self._response.json()

    def download(self, consume_callback: ConsumeCallback) -> None:
        try:
            for chunk in self._response.iter_content(8192):
                consume_callback(chunk)
        except requests.RequestException as e:
            raise convert_requests_exception(e)

    def close(self) -> None:
        self._response.close()

class RequestsSession(Session):
    """
        :any:`Session` implementation using the :code:`requests` library.

        All arguments passed in the constructor are directly forwared to :any:`requests.Session`.

        :ivar requests_session: underlying instance of :any:`requests.Session`

        .. note::
           Internally, this class creates thread-local instances of
           :any:`requests.Session`, since it is not currently guaranteed to be
           thread safe.
           Calling :any:`Session.close()` only closes the thread-local session.

        To pass `requests`-specific arguments from :any:`Client` use :code:`requests_args` keyword argument.

        Usage example:

        .. code:: python

           import yadisk
           from yadisk.sessions.requests_session import RequestsSession

           with yadisk.Client(..., session_factory=RequestsSession) as client:
               client.get_meta(
                   "/my_file.txt",
                   n_retries=5,
                   requests_args={
                       "proxies": {"https": "http://example.com:1234"},
                       "verify": False
                   }
                )
    """

    def __init__(self, *args, **kwargs):
        self._args, self._kwargs = args, kwargs
        self._local = threading.local()
        self._headers = CaseInsensitiveDict()

    @property
    def requests_session(self) -> requests.Session:
        if not hasattr(self._local, "session"):
            self._local.session = requests.Session(*self._args, **self._kwargs)

            # Session.close() only closes the thread-local session
            # This is a simple way to ensure it gets closed eventually
            weakref.finalize(self._local.session, self._local.session.close)

        return self._local.session

    def set_headers(self, headers: Headers) -> None:
        self._headers.update(headers)

    def send_request(self, method: HTTPMethod, url: str, **kwargs) -> Response:
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
