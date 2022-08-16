# -*- coding: utf-8 -*-

from collections import defaultdict
import time

import requests.exceptions

from .objects import ErrorObject
from .exceptions import *
from . import settings

__all__ = ["get_exception", "auto_retry"]

EXCEPTION_MAP = {400: defaultdict(lambda: BadRequestError,
                                  {"FieldValidationError": FieldValidationError}),
                 401: defaultdict(lambda: UnauthorizedError),
                 403: defaultdict(lambda: ForbiddenError),
                 404: defaultdict(lambda: NotFoundError,
                                  {"DiskNotFoundError": PathNotFoundError,
                                   "DiskOperationNotFoundError": OperationNotFoundError}),
                 406: defaultdict(lambda: NotAcceptableError),
                 409: defaultdict(lambda: ConflictError,
                                  {"DiskPathDoesntExistsError": ParentNotFoundError,
                                   "DiskPathPointsToExistentDirectoryError": DirectoryExistsError,
                                   "DiskResourceAlreadyExistsError": PathExistsError,
                                   "MD5DifferError": MD5DifferError}),
                 415: defaultdict(lambda: UnsupportedMediaError),
                 423: defaultdict(lambda: LockedError,
                                  {"DiskResourceLockedError": ResourceIsLockedError}),
                 429: defaultdict(lambda: TooManyRequestsError),
                 500: defaultdict(lambda: InternalServerError),
                 502: defaultdict(lambda: BadGatewayError),
                 503: defaultdict(lambda: UnavailableError),
                 504: defaultdict(lambda: GatewayTimeoutError),
                 509: defaultdict(lambda: InsufficientStorageError)}

def get_exception(response):
    """
        Get an exception instance based on response, assuming the request has failed.

        :param response: an instance of :any:`requests.Response`

        :returns: an exception instance, subclass of :any:`YaDiskError`
    """

    exc_group = EXCEPTION_MAP.get(response.status_code, None)

    if exc_group is None:
        return UnknownYaDiskError("Unknown Yandex.Disk error")

    try:
        js = response.json()
    except (ValueError, RuntimeError):
        js = None

    error = ErrorObject(js)

    msg = error.message or "<empty>"
    desc = error.description or "<empty>"

    exc = exc_group[error.error]

    return exc(error.error, "%s (%s / %s)" % (msg, desc, error.error), response)

def auto_retry(func, n_retries=None, retry_interval=None):
    """
        Attempt to perform a request with automatic retries.
        A retry is triggered by :any:`requests.exceptions.RequestException` or :any:`RetriableYaDiskError`.

        :param func: function to run, must not require any arguments
        :param n_retries: `int`, maximum number of retries
        :param retry_interval: `int` or `float`, delay between retries (in seconds)

        :returns: return value of func()
    """

    if n_retries is None:
        n_retries = settings.DEFAULT_N_RETRIES

    if retry_interval is None:
        retry_interval = settings.DEFAULT_RETRY_INTERVAL

    for i in range(n_retries + 1):
        try:
            return func()
        except (requests.exceptions.RequestException, RetriableYaDiskError) as e:
            if i == n_retries:
                raise e

        if retry_interval:
            time.sleep(retry_interval)
