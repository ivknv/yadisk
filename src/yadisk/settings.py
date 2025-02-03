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

import logging
from .types import TimeoutParameter

__all__ = [
    "BASE_API_URL",
    "BASE_OAUTH_API_URL",
    "DEFAULT_N_RETRIES",
    "DEFAULT_RETRY_INTERVAL",
    "DEFAULT_TIMEOUT",
    "DEFAULT_UPLOAD_RETRY_INTERVAL",
    "DEFAULT_UPLOAD_TIMEOUT",
    "logger"
]

#: `tuple` of 2 numbers (`int` or `float`), default timeout for requests.
#: First number is the connect timeout, the second one is the read timeout.
DEFAULT_TIMEOUT: TimeoutParameter = (10.0, 15.0)

#: `int`, default number of retries
DEFAULT_N_RETRIES: int = 3

#: `float`, default retry interval
DEFAULT_RETRY_INTERVAL: float = 0.0

#: Analogous to :any:`settings.DEFAULT_TIMEOUT` but for
#: :any:`Client.upload()`/:any:`AsyncClient.upload()` function
DEFAULT_UPLOAD_TIMEOUT: TimeoutParameter = DEFAULT_TIMEOUT

#: Analogous to :any:`settings.DEFAULT_RETRY_INTERVAL` but for
#: :any:`Client.upload()`/:any:`AsyncClient.upload()` function
DEFAULT_UPLOAD_RETRY_INTERVAL: float = 0.0

#: Base URL for Yandex.Disk's REST API.
#: Can be overriden for testing and other purposes
BASE_API_URL: str = "https://cloud-api.yandex.net"

#: Base URL for Yandex.Disk's OAuth API.
#: Can be overriden for testing and other purposes
BASE_OAUTH_API_URL: str = "https://oauth.yandex.ru"

#: Logger for the library. Logs include information about requests to the API
#: and automatic retry attempts.
logger = logging.getLogger("yadisk")
