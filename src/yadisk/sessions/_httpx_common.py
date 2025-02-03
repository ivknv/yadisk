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

from typing import Any, Optional, Union

from ..exceptions import (
    RequestError, TooManyRedirectsError,
    RequestTimeoutError, YaDiskConnectionError
)

from ..types import TimeoutParameter
from .._typing_compat import Dict, Tuple
from .. import settings

import httpx

__all__ = ["convert_args_for_httpx", "convert_httpx_exception", "convert_timeout"]


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


def convert_args_for_httpx(
    session: Union[httpx.Client, httpx.AsyncClient],
    kwargs: Dict[str, Any]
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    request_kwargs = {
        "params": kwargs.get("params"),
        "headers": kwargs.get("headers"),
        "content": kwargs.get("data"),
        "timeout": session.timeout
    }

    if "timeout" in kwargs:
        request_kwargs["timeout"] = convert_timeout(kwargs["timeout"])

    send_kwargs = {"stream": kwargs.get("stream", False)}

    if "httpx_args" in kwargs:
        httpx_args = dict(kwargs["httpx_args"] or {})

        for key in ("stream", "auth", "follow_redirects"):
            if key in httpx_args:
                send_kwargs[key] = httpx_args.pop(key)

        request_kwargs.update(httpx_args)

    return request_kwargs, send_kwargs
