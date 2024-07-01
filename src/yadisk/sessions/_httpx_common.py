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

from typing import Optional, Union

from ..exceptions import (
    RequestError, TooManyRedirectsError,
    RequestTimeoutError, YaDiskConnectionError
)

from ..types import TimeoutParameter
from .. import settings

import httpx

__all__ = ["convert_httpx_exception", "convert_timeout", "convert_args_for_httpx"]


def convert_httpx_exception(exc: httpx.HTTPError) -> Union[RequestError, httpx.HTTPError]:
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


def convert_timeout(timeout: TimeoutParameter) -> Optional[httpx.Timeout]:
    if timeout is ...:
        return convert_timeout(settings.DEFAULT_TIMEOUT)
    elif timeout is None:
        return None
    elif isinstance(timeout, (int, float)):
        return httpx.Timeout(timeout)

    connect, read = timeout

    return httpx.Timeout(connect=connect, pool=connect, read=read, write=read)


def convert_args_for_httpx(session, kwargs):
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
        "timeout": kwargs.get("timeout", session.timeout)
    }

    for i in request_kwargs:
        kwargs.pop(i, None)

    send_kwargs = kwargs

    return request_kwargs, send_kwargs
