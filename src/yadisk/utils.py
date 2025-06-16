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

import asyncio
from collections import defaultdict
import sys
import time

from .objects import ErrorObject
from .exceptions import *
from . import settings

from typing import Any, Optional, Union, TypeVar

from ._typing_compat import Callable, Awaitable, Dict, Tuple, Type
from .types import AnyResponse

__all__ = ["CaseInsensitiveDict", "async_auto_retry", "auto_retry", "get_exception"]


class _UnexpectedRequestError(YaDiskError):
    # Used for testing (see tests/disk_gateway.py)
    pass


if sys.version_info >= (3, 11) and hasattr(Exception, "add_note"):
    def _add_exception_note(exc: Exception, note: str) -> None:
        exc.add_note(note)
else:
    def _add_exception_note(exc: Exception, note: str) -> None:
        pass


EXCEPTION_MAP: Dict[int, Dict[str, Type[YaDiskError]]] = {
    400: defaultdict(
        lambda: BadRequestError,
        {
            "FieldValidationError":   FieldValidationError,
            "authorization_pending":  AuthorizationPendingError,
            "invalid_client":         InvalidClientError,
            "invalid_grant":          InvalidGrantError,
            "bad_verification_code":  BadVerificationCodeError,
            "unsupported_token_type": UnsupportedTokenTypeError
        }
    ),
    401: defaultdict(lambda: UnauthorizedError),
    403: defaultdict(
        lambda: ForbiddenError,
        {
            "DiskSymlinkPasswordRequiredError": PasswordRequiredError
        }
    ),
    404: defaultdict(
        lambda: NotFoundError,
        {
            "DiskNotFoundError":          PathNotFoundError,
            "DiskOperationNotFoundError": OperationNotFoundError
        }
    ),
    406: defaultdict(lambda: NotAcceptableError),
    409: defaultdict(
        lambda: ConflictError,
        {
            "DiskPathDoesntExistsError":              ParentNotFoundError,
            "DiskPathPointsToExistentDirectoryError": DirectoryExistsError,
            "DiskResourceAlreadyExistsError":         PathExistsError,
            "MD5DifferError":                         MD5DifferError
        }
    ),
    410: defaultdict(lambda: GoneError),
    413: defaultdict(lambda: PayloadTooLargeError),
    415: defaultdict(lambda: UnsupportedMediaError),
    423: defaultdict(
        lambda: LockedError,
        {
            "DiskResourceLockedError":        ResourceIsLockedError,
            "DiskUploadTrafficLimitExceeded": UploadTrafficLimitExceededError
        }
    ),
    429: defaultdict(
        lambda: TooManyRequestsError,
        {"DiskResourceDownloadLimitExceededError": ResourceDownloadLimitExceededError}
    ),
    500: defaultdict(lambda: InternalServerError),
    502: defaultdict(lambda: BadGatewayError),
    503: defaultdict(lambda: UnavailableError),
    504: defaultdict(lambda: GatewayTimeoutError),
    507: defaultdict(lambda: InsufficientStorageError),

    # This is a special value for testing
    499: defaultdict(lambda: _UnexpectedRequestError)
}


def get_exception(response: AnyResponse, error: Optional[ErrorObject]) -> YaDiskError:
    """
        Get an exception instance based on response, assuming the request has failed.

        :param response: an instance of :any:`Response` or :any:`AsyncResponse`
        :param error: an instance of :any:`ErrorObject` or `None`

        :returns: an exception instance, subclass of :any:`YaDiskError`
    """

    exc_group = EXCEPTION_MAP.get(response.status, None)

    if exc_group is None:
        return UnknownYaDiskError(f"Unknown Yandex.Disk error: status code {response.status}")

    if error is not None:
        msg = error.message or ""
        desc = error.description or ""
        error_name = error.error or ""
    else:
        msg = ""
        desc = ""
        error_name = ""

    exc = exc_group[error_name]

    exc_message = ""

    if msg:
        exc_message = msg

    if desc:
        if exc_message:
            exc_message += " | "

        exc_message += f"Error description: {desc.rstrip('.')}."

    if error_name:
        if exc_message:
            exc_message += " | "

        exc_message += f"Error code: {error_name}"

    if exc_message:
        exc_message += " | "

    exc_message += f"Status code: {response.status}"

    return exc(error_name, exc_message, response)


T = TypeVar("T")


def auto_retry(
    func: Callable[..., T],
    n_retries: Optional[int] = None,
    retry_interval: Optional[Union[int, float]] = None,
    args: Optional[Tuple] = None,
    kwargs: Optional[Dict[str, Any]] = None,
    retry_on: Tuple[Type[Exception], ...] = tuple()
) -> T:
    """
        Attempt to perform a request with automatic retries.
        A retry is triggered by :any:`RequestError` or :any:`RetriableYaDiskError`,
        unless the raised exception has :code:`disable_retry` set to :code:`True`.

        :param func: function to run, must not require any arguments
        :param n_retries: `int`, maximum number of retries
        :param retry_interval: `int` or `float`, delay between retries (in seconds)
        :param args: `tuple` or `None`, additional arguments for `func`
        :param kwargs: `dict` or `None`, additional keyword arguments for `func`
        :param retry_on: `tuple`, additional exception classes to retry on

        :returns: return value of func()
    """

    if n_retries is None:
        n_retries = settings.DEFAULT_N_RETRIES

    if retry_interval is None:
        retry_interval = settings.DEFAULT_RETRY_INTERVAL

    if args is None:
        args = tuple()

    if kwargs is None:
        kwargs = {}

    exceptions: Tuple[Type[Exception], ...] = (RequestError, RetriableYaDiskError, *retry_on)

    for i in range(n_retries + 1):
        try:
            return func(*args, **kwargs)
        except exceptions as e:
            if i == n_retries or (isinstance(e, YaDiskError) and e.disable_retry):
                settings.logger.info(
                    f"not triggering an automatic retry: ({i + 1} out of {n_retries}), got {e.__class__.__name__}: {e}"
                )

                if i:
                    _add_exception_note(e, f"Got the error after {i} retry attempts")

                raise

            settings.logger.info(
                f"automatic retry triggered: ({i + 1} out of {n_retries}), got {e.__class__.__name__}: {e}"
            )

        if retry_interval:
            time.sleep(retry_interval)

    # This should never be reachable
    raise AssertionError()


async def async_auto_retry(
    func: Union[Callable[..., Any], Callable[..., Awaitable[Any]]],
    n_retries: Optional[int] = None,
    retry_interval: Optional[Union[int, float]] = None,
    args: Optional[Tuple] = None,
    kwargs: Optional[Dict[str, Any]] = None,
    retry_on: Tuple[Type[Exception], ...] = tuple()
) -> Any:
    """
        Attempt to perform a request with automatic retries.
        A retry is triggered by :any:`RequestError` or :any:`RetriableYaDiskError`,
        unless the raised exception has :code:`disable_retry` set to :code:`True`.

        :param func: function to run, must not require any arguments
        :param n_retries: `int`, maximum number of retries
        :param retry_interval: `int` or `float`, delay between retries (in seconds)
        :param args: `tuple` or `None`, additional arguments for `func`
        :param kwargs: `dict` or `None`, additional keyword arguments for `func`
        :param retry_on: `tuple`, additional exception classes to retry on

        :returns: return value of func()
    """

    if n_retries is None:
        n_retries = settings.DEFAULT_N_RETRIES

    if retry_interval is None:
        retry_interval = settings.DEFAULT_RETRY_INTERVAL

    if args is None:
        args = tuple()

    if kwargs is None:
        kwargs = {}

    is_coro = asyncio.iscoroutinefunction(func)

    # Suppress false type hint errors
    callback: Any = func

    exceptions: Tuple[Type[Exception], ...] = (RequestError, RetriableYaDiskError, *retry_on)

    for i in range(n_retries + 1):
        try:
            if is_coro:
                return await callback(*args, **kwargs)
            else:
                return callback(*args, **kwargs)
        except exceptions as e:
            if i == n_retries or (isinstance(e, YaDiskError) and e.disable_retry):
                settings.logger.info(
                    f"not triggering an automatic retry: ({i + 1} out of {n_retries}), got {e.__class__.__name__}: {e}"
                )

                if i:
                    _add_exception_note(e, f"Got the error after {i} retry attempts")

                raise

            settings.logger.info(
                f"automatic retry triggered: ({i + 1} out of {n_retries}), got {e.__class__.__name__}: {e}"
            )

        if retry_interval:
            await asyncio.sleep(retry_interval)

    # This should never be reachable
    raise AssertionError()


class CaseInsensitiveDict(dict):
    """A case-insensitive dictionary. All keys are converted to lowercase."""

    @classmethod
    def _k(cls, key: str) -> str:
        return key.lower()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._convert_keys()

    def __getitem__(self, key: str) -> Any:
        return super().__getitem__(self.__class__._k(key))

    def __setitem__(self, key: str, value: Any) -> None:
        super().__setitem__(self.__class__._k(key), value)

    def __delitem__(self, key: str) -> Any:
        return super().__delitem__(self.__class__._k(key))

    def __contains__(self, key: Any) -> bool:
        return super().__contains__(self.__class__._k(key))

    def pop(self, key: str, /, *args, **kwargs) -> Any:
        return super().pop(self.__class__._k(key), *args, **kwargs)

    def get(self, key: str, /, *args, **kwargs) -> Any:
        return super().get(self.__class__._k(key), *args, **kwargs)

    def setdefault(self, key: str, *args, **kwargs) -> Any:
        return super().setdefault(self.__class__._k(key), *args, **kwargs)

    def update(self, *args, **kwargs) -> None:
        super().update(*(self.__class__(arg) for arg in args), **self.__class__(kwargs))

    def _convert_keys(self) -> None:
        for k in list(self.keys()):
            v = super(CaseInsensitiveDict, self).pop(k)
            self.__setitem__(k, v)
