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

from ._yadisk_object import YaDiskObject
from ._link_object import LinkObject
from .._common import str_or_error
from ..types import OperationStatus

from typing import Any, Optional

__all__ = [
    "AsyncOperationLinkObject",
    "OperationLinkObject",
    "OperationStatusObject",
    "SyncOperationLinkObject"
]


class OperationStatusObject(YaDiskObject):
    """
        Operation status object.

        :param operation_status: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar status: `str`, status of the operation
    """

    status: OperationStatus

    def __init__(self,
                 operation_status: Optional[dict] = None,
                 yadisk: Optional[Any] = None):
        YaDiskObject.__init__(
            self,
            {"status": str_or_error},
            yadisk)

        self.import_fields(operation_status)


class OperationLinkObject(LinkObject):
    """
        Operation link object.

        :param link: `dict` or `None`
        :param yadisk: :any:`Client`/:any:`AsyncClient` or `None`, `YaDisk` object

        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
    """

    pass


class SyncOperationLinkObject(OperationLinkObject):
    """
        Operation link object.

        :param link: `dict` or `None`
        :param yadisk: :any:`Client` or `None`, `YaDisk` object

        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
    """

    def get_status(self, **kwargs) -> OperationStatus:
        """
            Get operation status.

            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises OperationNotFoundError: requested operation was not found

            :returns: `str`, :code:`"in-progress"` indicates that the operation
                      is currently running, :code:`"success"` indicates that
                      the operation was successful, :code:`"failed"` means that
                      the operation failed
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.href is None:
            raise ValueError("OperationLinkObject has no link")

        return self._yadisk.get_operation_status(self.href, **kwargs)

    def wait(self, **kwargs) -> None:
        """
            Wait until an operation is completed. If the operation fails, an
            exception is raised. Waiting is performed by calling :any:`time.sleep`.

            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.href is None:
            raise ValueError("OperationLinkObject has no link")

        return self._yadisk.wait_for_operation(self.href, **kwargs)


class AsyncOperationLinkObject(OperationLinkObject):
    """
        Operation link object.

        :param link: `dict` or `None`
        :param yadisk: :any:`AsyncClient` or `None`, `YaDisk` object

        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
    """

    async def get_status(self, **kwargs) -> OperationStatus:
        """
            Get operation status.

            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises OperationNotFoundError: requested operation was not found

            :returns: `str`, :code:`"in-progress"` indicates that the operation
                      is currently running, :code:`"success"` indicates that
                      the operation was successful, :code:`"failed"` means that
                      the operation failed
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.href is None:
            raise ValueError("OperationLinkObject has no link")

        return await self._yadisk.get_operation_status(self.href, **kwargs)

    async def wait(self, **kwargs) -> None:
        """
            Wait until an operation is completed. If the operation fails, an
            exception is raised. Waiting is performed by calling :any:`asyncio.sleep`.

            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.href is None:
            raise ValueError("OperationLinkObject has no link")

        return await self._yadisk.wait_for_operation(self.href, **kwargs)
