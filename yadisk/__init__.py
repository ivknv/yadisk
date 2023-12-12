# -*- coding: utf-8 -*-

from . import api, objects, exceptions, utils

from .client import Client
from .async_client import AsyncClient
from .session import Session, Response
from .async_session import AsyncSession, AsyncResponse

__version__ = "2.0.0"

YaDisk = Client
AsyncYaDisk = AsyncClient

__all__ = [
    "Client", "AsyncClient", "YaDisk", "AsyncYaDisk", "Session", "Response",
    "AsyncSession", "AsyncResponse"
]
