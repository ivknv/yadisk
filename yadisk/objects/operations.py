# -*- coding: utf-8 -*-

from functools import partial

from .yadisk_object import YaDiskObject
from .resources import LinkObject

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..yadisk import YaDisk

__all__ = ["OperationStatusObject"]

class OperationStatusObject(YaDiskObject):
    """
        Operation status object.

        :param operation_status: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar type: `str`, type of the operation
        :ivar status: `str`, status of the operation
        :ivar operation_id: `str`, ID of the operation
        :ivar link: :any:`LinkObject`, link to the operation
        :ivar data: `dict`, other information about the operation
    """

    def __init__(self,
                 operation_status: Optional[dict] = None,
                 yadisk: Optional["YaDisk"] = None):
        YaDiskObject.__init__(
            self,
            {"type":         str,
             "status":       str,
             "operation_id": str,
             "link":         partial(LinkObject, yadisk=yadisk),
             "data":         dict},
            yadisk)

        self.import_fields(operation_status)
