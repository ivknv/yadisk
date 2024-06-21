# -*- coding: utf-8 -*-

from functools import partial

from .yadisk_object import YaDiskObject
from .link_object import LinkObject
from ..common import str_or_error, dict_or_error
from ..types import OperationStatus

from typing import Any, Optional

__all__ = [
    "OperationStatusObject", "OperationLinkObject",
    "SyncOperationLinkObject", "AsyncOperationLinkObject"
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

            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

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

            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

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
