# -*- coding: utf-8 -*-

from typing import Union, Optional, Tuple, Self
from .compat import Dict, Iterable, List, Generator, Callable

__all__ = ["Session", "Response", "TimeoutParameter"]

TimeoutParameter = Union[float, Tuple[Optional[float], Optional[float]]]
Payload = Union[bytes, Generator[bytes, None, None]]
ConsumeCallback = Callable[[bytes], None]

class Response:
    """
        Represents an HTTP response.

        :ivar status: `int`, HTTP status code
    """

    JSON = Union[Dict, List, str, int, float, None]

    status: int

    def json(self) -> JSON:
        """
            Returns JSON-content of the response (parses JSON).

            :returns: `dict`, `list`, `str`, `int`, `float` or `None`
        """
        raise NotImplementedError

    def download(self, consume_callback: ConsumeCallback) -> None:
        """
            Downloads response's content.

            :param consume_callback: function, takes one parameter - chunk of data (bytes),
                                     consumes the chunk (e.g. by writing to a file)
        """
        raise NotImplementedError

    def release(self) -> None:
        """Closes the response and releases the underlying connection into the pool"""
        raise NotImplementedError

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args, **kwargs) -> None:
        """Closes the response and releases the underlying connection into the pool"""
        self.release()

class Session:
    """
        HTTP session class. Maintains open connections, stores headers and other
        some other request parameters.

        Must be explicitly closed (can be done using the `with` statement).
    """

    def set_headers(self, headers: Dict[str, str]) -> None:
        """
            Updates session's headers.

            :param headers: dictionary of headers to be set
        """
        raise NotImplementedError

    def remove_headers(self, keys: Iterable[str]) -> None:
        """
            Removes session's headers.

            :param headers: list of headers to be removed
        """
        raise NotImplementedError

    def set_token(self, token: str) -> None:
        """
            Sets token for the session by setting the Authorization header.

            :param token: `str`, API token
        """

        self.set_headers({"Authorization": "OAuth " + token})

    def send_request(self, method: str, url: str, /, **kwargs) -> Response:
        """
            Sends an HTTP request with given parameters.
            In case an error occurs, the method should throw one of exceptions
            derived from :any:`YaDiskError`.
            Additional keyword arguments may be passed, they may be forwarded
            to the underlying HTTP client without modification.

            :param method: `str`, HTTP method
            :param url: `str`, URL
            :param params: `dict`, GET parameters
            :param data: `bytes` or a file-like object, data to be sent in the request body
            :param headers: `dict`, additional headers to be set
            :param timeout: request timeout, a `tuple` of `(read timeout, connect timeout)`, `float` or `None` (no timeout)
            :param stream: `bool`, if `False`, the response content will be immediately downloaded

            :returns: :any:`Response`, response object
        """
        raise NotImplementedError

    def close(self) -> None:
        """Closes the session."""
        raise NotImplementedError

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *args, **kwargs) -> None:
        """Closes the session."""
        return self.close()
