# -*- coding: utf-8 -*-

from io import BytesIO
import json

from ..exceptions import (
    RequestError, RequestTimeoutError,
    TooManyRedirectsError, YaDiskConnectionError
)

from ..session import Session, Response
from ..compat import Iterator
from ..common import CaseInsensitiveDict
from ..types import JSON, ConsumeCallback, Headers, HTTPMethod

from urllib.parse import urlencode

import pycurl

__all__ = ["PycurlSession"]

def convert_curl_error(error: pycurl.error) -> RequestError:
    code, msg = error.args

    mapping = {pycurl.E_TOO_MANY_REDIRECTS:      TooManyRedirectsError,
               pycurl.E_COULDNT_CONNECT:         YaDiskConnectionError,
               pycurl.E_NO_CONNECTION_AVAILABLE: YaDiskConnectionError,
               pycurl.E_OPERATION_TIMEDOUT:      RequestTimeoutError}

    exc = mapping.get(code) or RequestError
    return exc(msg)

class PycurlResponse(Response):
    def __init__(self, curl: pycurl.Curl, response: bytes):
        self._curl = curl
        self._response = response

    @property
    def status(self) -> int:
        return self._curl.getinfo(pycurl.RESPONSE_CODE)

    def json(self) -> JSON:
        if not self.status:
            try:
                self._response = self._curl.perform_rb()
            except pycurl.error as e:
                raise convert_curl_error(e)

        return json.loads(self._response)

    def download(self, consume_callback: ConsumeCallback) -> None:
        def write_cb(chunk: bytes) -> int:
            consume_callback(chunk)
            return len(chunk)

        self._curl.setopt(pycurl.WRITEFUNCTION, write_cb)

        try:
            self._curl.perform()
        except pycurl.error as e:
            raise convert_curl_error(e)

    def close(self) -> None:
        self._curl.close()

class IterableReader:
    def __init__(self, iterator: Iterator[bytes]):
        self.iterator = iterator
        self._current_chunk = b""
        self._position_in_chunk = 0

    def read(self, size=-1) -> bytes:
        if size < 0:
            return self.readall()

        data = b""
        while len(data) < size:
            if self._position_in_chunk >= len(self._current_chunk):
                try:
                    self._current_chunk = next(self.iterator)
                except StopIteration:
                    return data

                self._position_in_chunk = 0

            remaining = size - len(data)

            chunk_fragment = self._current_chunk[self._position_in_chunk:self._position_in_chunk + remaining]

            data += chunk_fragment
            self._position_in_chunk += len(chunk_fragment)

        return data

    def readall(self) -> bytes:
        data = b""

        while True:
            if self._position_in_chunk >= len(self._current_chunk):
                try:
                    self._current_chunk = next(self.iterator)
                except StopIteration:
                    return data

                self._position_in_chunk = 0

            chunk_fragment = self._current_chunk[self._position_in_chunk:]

            data += chunk_fragment
            self._position_in_chunk += len(chunk_fragment)

class PycurlSession(Session):
    def __init__(self):
        self._share = pycurl.CurlShare()
        self._headers = CaseInsensitiveDict()

    def set_headers(self, headers: Headers) -> None:
        self._headers.update(headers)

    def send_request(self, method: HTTPMethod, url: str, **kwargs) -> Response:
        params = kwargs.get("params", {})
        data = kwargs.get("data")
        stream = kwargs.get("stream", False)
        headers = CaseInsensitiveDict(self._headers)
        headers.update(kwargs.get("headers", {}))

        options = kwargs.get("curl_options", {})

        if params:
            url = url + "?" + urlencode(params)

        curl = pycurl.Curl()
        curl.setopt(pycurl.NOSIGNAL, True)
        curl.setopt(pycurl.FOLLOWLOCATION, True)
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.SHARE, self._share)

        if "timeout" in kwargs:
            timeout = kwargs["timeout"]

            if isinstance(timeout, tuple):
                connect_timeout, read_timeout = timeout
            else:
                connect_timeout = read_timeout = timeout

            MAX_TIMEOUT = 4294967 # in seconds

            if connect_timeout is None:
                connect_timeout = MAX_TIMEOUT

            if read_timeout is None:
                read_timeout = MAX_TIMEOUT

            curl.setopt(pycurl.CONNECTTIMEOUT_MS, int(connect_timeout * 1000))
            curl.setopt(pycurl.LOW_SPEED_TIME, int(read_timeout))
            curl.setopt(pycurl.LOW_SPEED_LIMIT, 64)

        for option, value in options.items():
            curl.setopt(option, value)

        if isinstance(data, bytes):
            data = BytesIO(data)

        uploading_file = False

        if data is not None:
            curl.setopt(pycurl.UPLOAD, True)
            uploading_file = True

            if isinstance(data, Iterator):
                data = IterableReader(data)

            curl.setopt(pycurl.READDATA, data)

        curl.setopt(pycurl.CUSTOMREQUEST, method)

        curl.setopt(pycurl.HTTPHEADER, [f"{k}:{v}" for k, v in self._headers.items()])

        if not stream or uploading_file:
            try:
                response = curl.perform_rb()
            except pycurl.error as e:
                raise convert_curl_error(e)
        else:
            response = b""

        return PycurlResponse(curl, response)

    def close(self):
        self._share.close()