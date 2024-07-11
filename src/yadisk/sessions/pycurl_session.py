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

from io import BytesIO
import json
from typing import Any, Optional

from ..exceptions import (
    RequestError, RequestTimeoutError,
    TooManyRedirectsError, YaDiskConnectionError
)

from .._session import Session, Response
from .._typing_compat import Iterator, Tuple, Dict
from ..utils import CaseInsensitiveDict
from ..types import JSON, ConsumeCallback, HTTPMethod, Headers, Payload, TimeoutParameter
from .. import settings

from urllib.parse import urlencode

import pycurl

__all__ = ["PycURLSession"]


def convert_curl_error(error: pycurl.error) -> RequestError:
    code, msg = error.args

    mapping = {pycurl.E_TOO_MANY_REDIRECTS:      TooManyRedirectsError,
               pycurl.E_COULDNT_CONNECT:         YaDiskConnectionError,
               pycurl.E_NO_CONNECTION_AVAILABLE: YaDiskConnectionError,
               pycurl.E_OPERATION_TIMEDOUT:      RequestTimeoutError}

    exc = mapping.get(code) or RequestError
    return exc(msg)


# see PycurlResponse.download() implementation
MAX_RESPONSE_BUFFER_SIZE = 128 * 1024


class PycURLResponse(Response):
    def __init__(self, curl: pycurl.Curl, response: bytes):
        super().__init__()

        self._curl = curl
        self._response = response

        self._update_status()

    def _update_status(self) -> None:
        self.status = self._curl.getinfo(pycurl.RESPONSE_CODE)

    def _perform(self) -> None:
        try:
            self._curl.perform()
        except pycurl.error as e:
            raise convert_curl_error(e) from e

        self._update_status()

    def _perform_rb(self) -> None:
        try:
            self._response = self._curl.perform_rb()
        except pycurl.error as e:
            raise convert_curl_error(e) from e

        self._update_status()

    def json(self) -> JSON:
        if not self.status:
            self._perform_rb()

        return json.loads(self._response)

    def download(self, consume_callback: ConsumeCallback) -> None:
        buffer = BytesIO()

        def write_cb(chunk: bytes) -> int:
            # Write up to `MAX_RESPONSE_BUFFER_SIZE` bytes of data into an in-memory buffer
            # This is a hack to detect bad HTTP status codes to give
            # `consume_callback` an opportunity to check status before writing
            if buffer.tell() < MAX_RESPONSE_BUFFER_SIZE:
                buffer.write(chunk)
                return len(chunk)
            elif buffer.tell():
                buffer.seek(0)

                chunk_from_buffer = buffer.read()
                consume_callback(chunk_from_buffer)

                buffer.seek(0)
                buffer.truncate(0)

            consume_callback(chunk)
            return len(chunk)

        self._curl.setopt(pycurl.WRITEFUNCTION, write_cb)

        self._perform()

        # Write left over data from the buffer
        if buffer.tell():
            buffer.seek(0)
            consume_callback(buffer.read())

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


def convert_timeout(timeout: TimeoutParameter) -> Tuple[float, float]:
    if timeout is ...:
        return convert_timeout(settings.DEFAULT_TIMEOUT)

    if isinstance(timeout, tuple):
        connect_timeout, read_timeout = timeout
    else:
        connect_timeout = read_timeout = timeout

    MAX_TIMEOUT = 4294967  # in seconds

    if connect_timeout is None:
        connect_timeout = MAX_TIMEOUT
    elif connect_timeout <= 0.001:
        # If connect_timeout gets rounded down to 0, the default connect
        # timeout would be applied instead by cURL
        connect_timeout = 0.001

    if read_timeout is None:
        # 0 disables LOW_SPEED_TIME
        read_timeout = 0
    elif read_timeout <= 1.0:
        # If read_timeout gets rounded down to 0, the low speed time will be disabled
        # 1 second is the lowest possible timeout
        read_timeout = 1.0

    return connect_timeout, read_timeout

class PycURLSession(Session):
    """
        .. _pycurl: https://pypi.org/project/pycurl

        :any:`Session` implementation using the `pycurl`_ library.

        To pass `pycurl`-specific arguments from :any:`Client` use :code:`curl_options` keyword argument.

        Usage example:

        .. code:: python

           import yadisk
           import pycurl

           with yadisk.Client(..., session="pycurl") as client:
               client.get_meta(
                   "/my_file.txt",
                   n_retries=5,
                   curl_options={
                       pycurl.MAX_SEND_SPEED_LARGE: 5 * 1024**2,
                       pycurl.MAX_RECV_SPEED_LARGE: 5 * 1024**2,
                       pycurl.PROXY: "http://localhost:12345",
                       pycurl.MAXREDIRS: 15
                   }
                )
    """

    def __init__(self) -> None:
        self._share = pycurl.CurlShare()

        self._share.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_CONNECT)
        self._share.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_DNS)
        self._share.setopt(pycurl.SH_SHARE, pycurl.LOCK_DATA_SSL_SESSION)

    def send_request(
        self,
        method: HTTPMethod,
        url: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Payload] = None,
        headers: Optional[Headers] = None,
        stream: bool = False,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Response:
        curl_headers = CaseInsensitiveDict({"connection": "keep-alive"})
        curl_headers.update(headers or {})

        if params:
            url = url + "?" + urlencode(params)

        curl = pycurl.Curl()
        curl.setopt(pycurl.NOSIGNAL, True)
        curl.setopt(pycurl.FOLLOWLOCATION, True)
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.SHARE, self._share)

        if "timeout" in kwargs:
            connect_timeout, read_timeout = convert_timeout(kwargs["timeout"])

            curl.setopt(pycurl.CONNECTTIMEOUT_MS, int(connect_timeout * 1000))
            curl.setopt(pycurl.LOW_SPEED_TIME, int(read_timeout))
            curl.setopt(pycurl.LOW_SPEED_LIMIT, 64)

        curl.setopt(pycurl.HTTPHEADER, [f"{k}:{v}" for k, v in curl_headers.items() if k and v])


        if curl_options is not None:
            for option, value in curl_options.items():
                curl.setopt(option, value)

        if isinstance(data, bytes):
            data = BytesIO(data)

        uploading_file = False

        if data is not None:
            curl.setopt(pycurl.UPLOAD, True)
            uploading_file = True

            if isinstance(data, Iterator):
                curl_data = IterableReader(data)
            else:
                curl_data = data

            curl.setopt(pycurl.READDATA, curl_data)

        curl.setopt(pycurl.CUSTOMREQUEST, method)

        if not stream or uploading_file:
            try:
                response = curl.perform_rb()
            except pycurl.error as e:
                raise convert_curl_error(e) from e
        else:
            response = b""

        return PycURLResponse(curl, response)

    def close(self) -> None:
        self._share.close()
