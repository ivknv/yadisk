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

from ..exceptions import InvalidResponseError

from ..utils import auto_retry, async_auto_retry, CaseInsensitiveDict
from .. import settings

from typing import Any, Optional, Union, TypeVar, TYPE_CHECKING
from .._typing_compat import Set, Dict
import json

if TYPE_CHECKING:
    from .._session import Session
    from .._async_session import AsyncSession
    from ..types import AnySession, HTTPMethod, JSON
    from .._client import Client
    from .._async_client import AsyncClient

__all__ = ["APIRequest"]

# For cases when None can't be used
_DEFAULT_TIMEOUT = object()


class APIRequest(object):
    """
        Base class for all API requests.

        :param session: an instance of :any:`Session`
        :param timeout: `float` or `tuple`, request timeout
        :param headers: `dict` or `None`, additional request headers
        :param n_retries: `int`, maximum number of retries
        :param retry_interval: delay between retries in seconds
        :param kwargs: other arguments for :any:`Session.send_request`

        :ivar base_url: `str`, base URL for sending the request
        :ivar url: `str`, request URL
        :ivar path: `str`, URL path for the request
        :ivar method: `str`, request method
        :ivar content_type: `str`, Content-Type header ("application/x-www-form-urlencoded" by default)
        :ivar timeout: `float` or `tuple`, request timeout
        :ivar n_retries: `int`, maximum number of retries
        :ivar success_codes: `list`-like, list of response codes that indicate request's success
        :ivar retry_interval: `float`, delay between retries in seconds
    """

    base_url: str = ""
    url: str = ""
    path: str = ""
    method: Optional["HTTPMethod"] = None
    content_type: str = "application/x-www-form-urlencoded"
    timeout = _DEFAULT_TIMEOUT
    n_retries: Optional[int] = None
    success_codes: Set[int] = {200}
    retry_interval: Optional[Union[int, float]] = None

    data: Union[Dict, bytes]
    params: Dict[str, Any]
    send_kwargs: Dict[str, Any]

    session: Any

    T = TypeVar("T")

    def __init__(self, session: "AnySession", **kwargs):
        base_url = self.base_url or settings.BASE_API_URL
        n_retries = kwargs.pop("n_retries", None)
        retry_interval = kwargs.pop("retry_interval", None)
        headers = kwargs.pop("headers", {})

        if headers is None:
            headers = {}

        try:
            timeout = kwargs["timeout"]
        except KeyError:
            timeout = self.timeout

        if timeout is _DEFAULT_TIMEOUT:
            timeout = settings.DEFAULT_TIMEOUT

        kwargs["timeout"] = timeout

        if n_retries is None:
            n_retries = self.n_retries
        if n_retries is None:
            n_retries = settings.DEFAULT_N_RETRIES

        if retry_interval is None:
            retry_interval = self.retry_interval
        if retry_interval is None:
            retry_interval = settings.DEFAULT_RETRY_INTERVAL

        self.session = session
        self.send_kwargs = kwargs
        self.base_url = base_url
        self.timeout = timeout
        self.n_retries = n_retries
        self.retry_interval = retry_interval
        self.headers = headers
        self.data = {}
        self.content = None
        self.params = {}

        if not self.url:
            self.url = f"{self.base_url}/{self.path.lstrip('/')}"

    def _prepare_send_args(self) -> Dict[str, Any]:
        headers = CaseInsensitiveDict()
        headers["Content-Type"] = self.content_type
        headers.update(self.headers)

        if self.data:
            if isinstance(self.data, Dict):
                data = json.dumps(self.data).encode("utf8")
            else:
                data = self.data
        else:
            data = None

        kwargs = dict(self.send_kwargs)
        kwargs.update({"headers": headers,
                       "data":    data,
                       "params":  self.params})

        return kwargs

    def _attempt(self) -> Optional["JSON"]:
        assert self.method is not None
        assert self.url

        kwargs = self._prepare_send_args()

        session: "Session" = self.session
        response = session.send_request(self.method, self.url, **kwargs)

        success = response.status in self.success_codes

        if not success:
            raise response.get_exception()

        try:
            return response.json()
        except ValueError:
            return None

    async def _async_attempt(self) -> Optional["JSON"]:
        assert self.method is not None
        assert self.url

        kwargs = self._prepare_send_args()

        session: "AsyncSession" = self.session

        response = await session.send_request(self.method, self.url, **kwargs)

        success = response.status in self.success_codes

        if not success:
            raise await response.get_exception()

        try:
            return await response.json()
        except ValueError:
            return None

    def send(self, yadisk: Optional["Client"]) -> Any:
        """
            Actually send the request

            :param yadisk: :any:`Client` instance that will be passed to :any:`process_json()`

            :returns: :any:`Response` (`self.response`)
        """

        json = auto_retry(self._attempt, self.n_retries, self.retry_interval)

        try:
            return self.process_json(json, yadisk=yadisk)
        except ValueError as e:
            raise InvalidResponseError(f"Server returned invalid response: {e}") from e

    def process_json(self, js: "JSON", **kwargs) -> Any:
        """
            Process the JSON response.

            :param js: `dict` or `None`, JSON response
            :param kwargs: extra arguments (optional)

            :returns: processed response, can be anything
        """

        raise NotImplementedError

    async def asend(self, yadisk: Optional["AsyncClient"]) -> Any:
        """
            Actually send the request

            :param yadisk: :any:`AsyncClient` instance that will be passed to :any:`aprocess_json()`

            :returns: :any:`AsyncResponse` (`self.response`)
        """

        json = await async_auto_retry(self._async_attempt, self.n_retries, self.retry_interval)

        try:
            return self.process_json(json, yadisk=yadisk)
        except ValueError as e:
            raise InvalidResponseError(f"Server returned invalid response: {e}") from e
