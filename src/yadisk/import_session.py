# -*- coding: utf-8 -*-

from typing import Type, TYPE_CHECKING

if TYPE_CHECKING:
    from .session import Session
    from .async_session import AsyncSession
    from .types import AsyncSessionName, SessionName

__all__ = ["import_session", "import_async_session"]

sessions = {
    "httpx":    ("sessions.httpx_session",    "HTTPXSession"),
    "pycurl":   ("sessions.pycurl_session",   "PycURLSession"),
    "requests": ("sessions.requests_session", "RequestsSession")
}

async_sessions = {
    "aiohttp": ("sessions.aiohttp_session",     "AIOHTTPSession"),
    "httpx":   ("sessions.async_httpx_session", "AsyncHTTPXSession")
}


def import_session(name: "SessionName") -> Type["Session"]:
    """
        Imports relevant session class based on provided name.

        The following sessions are available:

          * :code:`"httpx"` - :any:`HTTPXSession`
          * :code:`"pycurl"` - :any:`PycURLSession`
          * :code:`"requests"` - :any:`RequestsSession`

        :param name: `str`, session name

        :raises ImportError: could not import module
        :raises ValueError: unknown name

        :returns: subclass of :any:`Session`
    """

    try:
        module_path, class_name = sessions[name]
    except KeyError:
        raise ValueError(f"unknown session name: {repr(name)}") from None

    return getattr(
        __import__(module_path, globals(), locals(), level=1, fromlist=(class_name,)),
        class_name
    )


def import_async_session(name: "AsyncSessionName") -> Type["AsyncSession"]:
    """
        Imports relevant asynchronous session class based on provided name.

        :param name: `str`, session name

        The following sessions are available:

          * :code:`"aiohttp"` - :any:`AIOHTTPSession`
          * :code:`"httpx"` - :any:`AsyncHTTPXSession`

        :raises ImportError: could not import module
        :raises ValueError: unknown name

        :returns: subclass of :any:`AsyncSession`
    """

    try:
        module_path, class_name = async_sessions[name]
    except KeyError:
        raise ValueError(f"unknown asynchronous session name: {repr(name)}") from None

    return getattr(
        __import__(module_path, globals(), locals(), level=1, fromlist=(class_name,)),
        class_name
    )
