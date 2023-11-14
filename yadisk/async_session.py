# -*- coding: utf-8 -*-

from typing import TYPE_CHECKING, Any, Optional
from .compat import Iterable, Self, Dict
from .types import (
    AsyncConsumeCallback, JSON, Headers, HTTPMethod, AsyncPayload, TimeoutParameter
)
from .objects import ErrorObject
from .utils import get_exception

if TYPE_CHECKING:
    from .exceptions import YaDiskError

__all__ = ["AsyncSession", "AsyncResponse"]

class AsyncResponse:
    """
        Represents an HTTP response.

        :ivar status: `int`, HTTP status code
    """

    status: int

    async def json(self) -> JSON:
        """
            Returns JSON-content of the response (parses JSON).

            :returns: `dict`, `list`, `str`, `int`, `float` or `None`
        """
        raise NotImplementedError

    async def download(self, consume_callback: AsyncConsumeCallback) -> None:
        """
            Downloads response's content.

            :param consume_callback: regular or async function, takes one
                                     parameter - chunk of data (bytes),
                                     consumes the chunk (e.g. by writing to a file)
        """
        raise NotImplementedError

    async def get_exception(self) -> "YaDiskError":
        """
            Convenience wrapper for :any:`yadisk.utils.get_exception`.
        """

        try:
            js = await self.json()
        except (ValueError, RuntimeError):
            js = None

        error = ErrorObject(js)

        return get_exception(self, error)

    async def close(self) -> None:
        """Closes the response and releases the underlying connection into the pool"""
        raise NotImplementedError

    async def __aenter__(self) -> Self:
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

    def set_headers(self, headers: Headers) -> None:
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

    async def send_request(self,
                           method: HTTPMethod,
                           url: str,
                           *,
                           params:  Optional[Dict[str, Any]] = None,
                           data:    Optional[AsyncPayload] = None,
                           timeout: TimeoutParameter = None,
                           stream:  bool = False,
                           **kwargs) -> AsyncResponse:
        """
            Sends an HTTP request with given parameters.
            In case an error occurs, the method should throw one of exceptions
            derived from :any:`YaDiskError`.
            Additional keyword arguments may be passed, they may be forwarded
            to the underlying HTTP client without modification.

            :param method: `str`, HTTP method
            :param url: `str`, URL
            :param params: `dict`, GET parameters
            :param data: `bytes`, iterator (possibly async) or a file-like object (possible async),
                         data to be sent in the request body
            :param headers: `dict`, additional headers to be set
            :param timeout: request timeout, a `tuple` of `(read timeout, connect timeout)`, `float` or `None` (no timeout)
            :param stream: `bool`, if `False`, the response content will be immediately downloaded

            :returns: :any:`Response`, response object
        """
        raise NotImplementedError

    async def close(self) -> None:
        """Closes the session."""
        raise NotImplementedError

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args, **kwargs) -> None:
        """Closes the session."""
        return await self.close()
