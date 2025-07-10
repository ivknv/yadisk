# -*- coding: utf-8 -*-
# Copyright © 2025 Ivan Konovalov

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

from . import objects, exceptions, utils, types

from ._client import Client
from ._async_client import AsyncClient
from ._session import Session, Response
from ._async_session import AsyncSession, AsyncResponse
from ._import_session import import_session, import_async_session

__version__ = "3.4.0"

YaDisk = Client
AsyncYaDisk = AsyncClient

__all__ = [
    "AsyncClient",
    "AsyncResponse",
    "AsyncSession",
    "AsyncYaDisk",
    "Client",
    "Response",
    "Session",
    "YaDisk",
    "import_async_session",
    "import_session"
]
