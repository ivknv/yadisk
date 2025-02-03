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

from typing import TYPE_CHECKING, Any, Optional, TypeVar
from ._typing_compat import Dict
from .types import (
    AsyncConsumeCallback, JSON, HTTPMethod, AsyncPayload, Headers, TimeoutParameter
)
from .objects import ErrorObject
from .utils import get_exception

if TYPE_CHECKING:  # pragma: no cover
    from .exceptions import YaDiskError

__all__ = ["AsyncResponse", "AsyncSession"]


class AsyncResponse:
    """
        Represents an HTTP response.

        In case an error occurs, methods of this class should throw one of exceptions
        derived from :any:`YaDiskError`.

        :ivar status: `int`, HTTP status code
    """

    _Self = TypeVar("_Self", bound="AsyncResponse")

    status: int

    def __init__(self) -> None:
        """Constructs an :any:`AsyncResponse` object."""

        self.status = 0

    async def json(self) -> JSON:
        """
            Returns JSON-content of the response (parses JSON).

            .. note::
               This is an abstract method that needs to be implemented.

            :raises RequestError: could not receive the response's body
            :raises ValueError: could not parse JSON

            :returns: `dict`, `list`, `str`, `int`, `float` or `None`
        """
        raise NotImplementedError

    async def download(self, consume_callback: AsyncConsumeCallback) -> None:
        """
            Downloads response's content.

            .. note::
               This is an abstract method that needs to be implemented.

            :param consume_callback: regular or async function, takes one
                                     parameter - chunk of data (bytes),
                                     consumes the chunk (e.g. by writing to a file)

            :raises RequestError: could not receive the response's body
        """
        raise NotImplementedError

    async def get_exception(self) -> "YaDiskError":
        """
            Convenience wrapper for :any:`yadisk.utils.get_exception`.

            :returns: :any:`YaDiskError`
        """

        try:
            js = await self.json()
        except ValueError:
            js = None

        error = ErrorObject(js)

        return get_exception(self, error)

    async def close(self) -> None:
        """
            Closes the response and releases the underlying connection into the pool.

            .. note::
               This is an abstract method that needs to be implemented.
        """
        raise NotImplementedError

    async def __aenter__(self: _Self) -> _Self:
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        """Closes the response and releases the underlying connection into the pool"""

        await self.close()


class AsyncSession:
    """
        HTTP session class. Maintains open connections, stores headers and
        some other request parameters.

        Must be explicitly closed (can be done using the `with` statement).
    """

    _Self = TypeVar("_Self", bound="AsyncSession")

    async def send_request(self,
                           method: HTTPMethod,
                           url: str,
                           *,
                           params:  Optional[Dict[str, Any]] = None,
                           data:    Optional[AsyncPayload] = None,
                           timeout: TimeoutParameter = ...,
                           headers: Optional[Headers] = None,
                           stream:  bool = False,
                           **kwargs) -> AsyncResponse:
        """
            Sends an HTTP request with given parameters.
            In case an error occurs, the method should throw one of exceptions
            derived from :any:`YaDiskError`.
            Additional keyword arguments may be passed, they may be forwarded
            to the underlying HTTP client without modification.

            .. note::
               This is an abstract method that needs to be implemented.

            :param method: `str`, HTTP method
            :param url: `str`, URL
            :param params: `dict`, GET parameters
            :param data: `bytes`, iterator (possibly async) or a file-like object (possible async),
                         data to be sent in the request body
            :param headers: `dict`, additional headers to be set
            :param timeout: request timeout, a `tuple` of `(read timeout, connect timeout)`,
                            `float` or `None` (no timeout)
            :param stream: `bool`, if `False`, the response content will be immediately downloaded

            :returns: :any:`Response`, response object
        """
        raise NotImplementedError

    async def close(self) -> None:
        """
            Closes the session.

            .. note::
               This is an abstract method that needs to be implemented.
        """
        raise NotImplementedError

    async def __aenter__(self: _Self) -> _Self:
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        """Closes the session."""
        return await self.close()
