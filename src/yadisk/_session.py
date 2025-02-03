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

from typing import Optional, Any, TypeVar
from .exceptions import YaDiskError
from ._typing_compat import Dict
from .utils import get_exception
from .objects import ErrorObject
from .types import (
    ConsumeCallback, JSON, HTTPMethod, Headers, Payload, TimeoutParameter
)

__all__ = ["Response", "Session"]


class Response:
    """
        Represents an HTTP response.

        In case an error occurs, methods of this class should throw one of exceptions
        derived from :any:`YaDiskError`.

        :ivar status: `int`, HTTP status code
    """

    _Self = TypeVar("_Self", bound="Response")

    status: int

    def __init__(self) -> None:
        """Constructs a :any:`Response` object."""

        self.status = 0

    def json(self) -> JSON:
        """
            Returns JSON-content of the response (parses JSON).

            .. note::
               This is an abstract method that needs to be implemented.

            :raises RequestError: could not receive the response's body
            :raises ValueError: could not parse JSON

            :returns: `dict`, `list`, `str`, `int`, `float` or `None`
        """
        raise NotImplementedError

    def download(self, consume_callback: ConsumeCallback) -> None:
        """
            Downloads response's content.

            .. note::
               This is an abstract method that needs to be implemented.

            :param consume_callback: function, takes one parameter - chunk of data (bytes),
                                     consumes the chunk (e.g. by writing to a file)

            :raises RequestError: could not receive the response's body
        """
        raise NotImplementedError

    def get_exception(self) -> YaDiskError:
        """
            Convenience wrapper for :any:`yadisk.utils.get_exception`.

            :returns: :any:`YaDiskError`
        """

        try:
            js = self.json()
        except ValueError:
            js = None

        error = ErrorObject(js)

        return get_exception(self, error)

    def close(self) -> None:
        """
            Closes the response and releases the underlying connection into the pool

            .. note::
               This is an abstract method that needs to be implemented.
        """
        raise NotImplementedError

    def __enter__(self: _Self) -> _Self:
        return self

    def __exit__(self, *args, **kwargs) -> None:
        """Closes the response and releases the underlying connection into the pool"""
        self.close()


class Session:
    """
        HTTP session class. Maintains open connections, stores headers and
        some other request parameters.

        Must be explicitly closed (can be done using the `with` statement).
    """

    _Self = TypeVar("_Self", bound="Session")

    def send_request(self,
                     method: HTTPMethod,
                     url: str,
                     *,
                     params:  Optional[Dict[str, Any]] = None,
                     data:    Optional[Payload] = None,
                     timeout: TimeoutParameter = ...,
                     headers: Optional[Headers] = None,
                     stream:  bool = False,
                     **kwargs) -> Response:
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
            :param data: `bytes`, an iterator or a file-like object, data to be sent in the request body
            :param headers: `dict`, additional headers to be set
            :param timeout: request timeout, a `tuple` of `(read timeout, connect timeout)`,
                            `float` or `None` (no timeout)
            :param stream: `bool`, if `False`, the response content will be immediately downloaded

            :returns: :any:`Response`, response object
        """
        raise NotImplementedError

    def close(self) -> None:
        """
            Closes the session.

            .. note::
               This is an abstract method that needs to be implemented.
        """
        raise NotImplementedError

    def __enter__(self: _Self) -> _Self:
        return self

    def __exit__(self, *args, **kwargs) -> None:
        """Closes the session."""
        return self.close()
