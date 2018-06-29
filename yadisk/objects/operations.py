# -*- coding: utf-8 -*-

from .yadisk_object import YaDiskObject
from .resources import LinkObject

__all__ = ["OperationStatusObject"]

class OperationStatusObject(YaDiskObject):
    """
        Operation status object.

        :param operation_status: `dict` or `None`

        :ivar type: `str`, type of the operation
        :ivar status: `str`, status of the operation
        :ivar operation_id: `str`, ID of the operation
        :ivar link: :any:`LinkObject`, link to the operation
        :ivar data: `dict`, other information about the operation
    """

    def __init__(self, operation_status=None):
        YaDiskObject.__init__(self, {"type":         str,
                                     "status":       str,
                                     "operation_id": str,
                                     "link":         LinkObject,
                                     "data":         dict})

        self.import_fields(operation_status)
