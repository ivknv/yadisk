#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .YaDiskObject import YaDiskObject
from .resources import LinkObject

__all__ = ["OperationStatusObject"]

class OperationStatusObject(YaDiskObject):
    """
        Operation status object.

        :param operation_status: `dict` or `None`

        type
            `str`, type of the operation
        status
            `str`, status of the operation
        operation_id
            `str`, ID of the operation
        link
            `LinkObject`, link to the operation
        data
            `dict`, other information about the operation
    """

    def __init__(self, operation_status=None):
        YaDiskObject.__init__(self, {"type":         str,
                                     "status":       str,
                                     "operation_id": str,
                                     "link":         LinkObject,
                                     "data":         dict})

        self.import_fields(operation_status)
