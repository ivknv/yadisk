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
from ._compat import Dict
from .utils import get_exception
from .objects import ErrorObject
from .types import ConsumeCallback, JSON, HTTPMethod, Payload, TimeoutParameter

__all__ = ["Session", "Response"]


class Response:
    """
        Represents an HTTP response.

        In case an error occurs, methods of this class should throw one of exceptions
        derived from :any:`YaDiskError`.
    """

    _Self = TypeVar("_Self", bound="Response")

    def status(self) -> int:
        """
            Returns HTTP status code.

            .. note::
               This is an abstract method that needs to be implemented.

            :returns: `int`
        """

        raise NotImplementedError

    def json(self) -> JSON:
        """
            Returns JSON-content of the response (parses JSON).

            .. note::
               This is an abstract method that needs to be implemented.

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
        """
        raise NotImplementedError

    def get_exception(self) -> YaDiskError:
        """
            Convenience wrapper for :any:`yadisk.utils.get_exception`.
        """

        try:
            js = self.json()
        except (ValueError, RuntimeError):
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

    def set_headers(self, headers: Dict[str, str]) -> None:
        """
            Updates session's headers.

            .. note::
               This is an abstract method that needs to be implemented.

            :param headers: dictionary of headers to be set
        """
        raise NotImplementedError

    def set_token(self, token: str) -> None:
        """
            Sets token for the session by setting the Authorization header.

            :param token: `str`, API token
        """

        self.set_headers({"Authorization": "OAuth " + token})

    def send_request(self,
                     method: HTTPMethod,
                     url: str,
                     *,
                     params:  Optional[Dict[str, Any]] = None,
                     data:    Optional[Payload] = None,
                     timeout: TimeoutParameter = None,
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
