# -*- coding: utf-8 -*-

from typing import Optional, Any
from .exceptions import YaDiskError
from .compat import Dict, Self
from .utils import get_exception
from .objects import ErrorObject
from .types import ConsumeCallback, JSON, HTTPMethod, Payload, TimeoutParameter

__all__ = ["Session", "Response"]

class Response:
    """
        Represents an HTTP response.

        :ivar status: `int`, HTTP status code
    """

    status: int

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

    def __enter__(self) -> Self:
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
            :param timeout: request timeout, a `tuple` of `(read timeout, connect timeout)`, `float` or `None` (no timeout)
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

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args, **kwargs) -> None:
        """Closes the session."""
        return self.close()
