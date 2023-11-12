# -*- coding: utf-8 -*-

from . import api, objects, exceptions, utils

from .client import Client
from .async_client import AsyncClient

__version__ = "1.3.4"

YaDisk = Client
AsyncYaDisk = AsyncClient

__all__ = ["Client", "AsyncClient", "YaDisk", "AsyncYaDisk"]
