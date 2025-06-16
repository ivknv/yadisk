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

from typing import Optional, Any
from .._typing_compat import Dict, Tuple, Type

from ._yadisk_object import YaDiskObject
from ._link_object import LinkObject

from ..types import OperationStatus, TimeoutParameter, Headers

__all__ = [
    "AsyncOperationLinkObject",
    "OperationLinkObject",
    "OperationStatusObject",
    "SyncOperationLinkObject"
]


class OperationStatusObject(YaDiskObject):
    status: OperationStatus

    def __init__(self,
                 operation_status: Optional[dict] = None,
                 yadisk: Optional[Any] = None) -> None:
        ...

class OperationLinkObject(LinkObject):
    ...

class SyncOperationLinkObject(OperationLinkObject):
    def get_status(
        self,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> OperationStatus: ...

    def wait(
        self,
        *,
        poll_interval: float = ...,
        poll_timeout: Optional[float] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> None:
        ...


class AsyncOperationLinkObject(OperationLinkObject):
    async def get_status(
        self,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> OperationStatus: ...

    async def wait(
        self,
        *,
        poll_interval: float = ...,
        poll_timeout: Optional[float] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> None:
        ...
