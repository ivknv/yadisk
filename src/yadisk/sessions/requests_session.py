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

from ..exceptions import (
    RequestError, TooManyRedirectsError,
    RequestTimeoutError, YaDiskConnectionError
)

from .._session import Session, Response
from ..utils import CaseInsensitiveDict
from ..types import JSON, ConsumeCallback, HTTPMethod, unspecified
from .. import settings

from typing import Union

import threading

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
        super().__init__()

        self._response = response
        self.status = self._response.status_code

    def json(self) -> JSON:
        return self._response.json()

    def download(self, consume_callback: ConsumeCallback) -> None:
        try:
            for chunk in self._response.iter_content(8192):
                consume_callback(chunk)
        except requests.RequestException as e:
            raise convert_requests_exception(e) from e

    def close(self) -> None:
        self._response.close()


class RequestsSession(Session):
    """
        .. _requests: https://pypi.org/project/requests

        :any:`Session` implementation using the `requests`_ library.

        All arguments passed in the constructor are directly forwared to :any:`requests.Session`.

        :ivar requests_session: underlying instance of :any:`requests.Session`

        .. note::
           Internally, this class creates thread-local instances of
           :any:`requests.Session`, since it is not currently guaranteed to be
           thread safe.
           Calling :any:`Session.close()` will close all thread-local sessions
           managed by this object.

        To pass `requests`-specific arguments from :any:`Client` use :code:`requests_args` keyword argument.

        Usage example:

        .. code:: python

           import yadisk

           with yadisk.Client(..., session="requests") as client:
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
        self._sessions = []

    @property
    def requests_session(self) -> requests.Session:
        if not hasattr(self._local, "session"):
            self._local.session = requests.Session(*self._args, **self._kwargs)
            self._sessions.append(self._local.session)

        return self._local.session

    def _close_local(self) -> None:
        if not hasattr(self._local, "session"):
            return

        session = self._local.session

        session.close()
        self._sessions.remove(session)

    def send_request(self, method: HTTPMethod, url: str, **kwargs) -> Response:
        headers = CaseInsensitiveDict(self.requests_session.headers)

        if "requests_args" in kwargs:
            kwargs.update(kwargs.pop("requests_args"))

        headers.update(kwargs.get("headers", {}))

        kwargs["headers"] = headers

        if "timeout" in kwargs:
            timeout = kwargs["timeout"]

            if timeout is unspecified:
                kwargs["timeout"] = settings.DEFAULT_TIMEOUT

        try:
            return RequestsResponse(self.requests_session.request(method, url, **kwargs))
        except requests.exceptions.RequestException as e:
            raise convert_requests_exception(e) from e

    def close(self) -> None:
        while self._sessions:
            session = self._sessions.pop()
            session.close()
