# -*- coding: utf-8 -*-

__all__ = ["DEFAULT_TIMEOUT", "DEFAULT_N_RETRIES", "DEFAULT_UPLOAD_TIMEOUT",
           "DEFAULT_UPLOAD_RETRY_INTERVAL", "BASE_API_URL", "BASE_OAUTH_API_URL"]

# `tuple` of 2 numbers (`int` or float`), default timeout for requests.
# First number is the connect timeout, the second one is the read timeout.
DEFAULT_TIMEOUT = (10.0, 15.0)

# `int`, default number of retries
DEFAULT_N_RETRIES = 3

# `float`, default retry interval
DEFAULT_RETRY_INTERVAL = 0.0

# Analogous to `DEFAULT_TIMEOUT` but for `upload` function
DEFAULT_UPLOAD_TIMEOUT = DEFAULT_TIMEOUT

# Analogous to `DEFAULT_RETRY_INTERVAL` but for `upload` function
DEFAULT_UPLOAD_RETRY_INTERVAL = 0.0

# Base URL for Yandex.Disk's REST API
# Can be overriden for testing and other purposes
BASE_API_URL = "https://cloud-api.yandex.net"

# Base URL for Yandex.Disk's OAuth API
# Can be overriden for testing and other purposes
BASE_OAUTH_API_URL = "https://oauth.yandex.ru"
