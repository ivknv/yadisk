#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .YaDiskObject import YaDiskObject
from .resources import LinkObject
from ..common import typed_list

__all__ = ["OperationStatusObject", "OperationStatusListObject"]

class OperationStatusObject(YaDiskObject):
    def __init__(self, operation_status=None):
        YaDiskObject.__init__(self, {"type":         str,
                                     "status":       str,
                                     "operation_id": str,
                                     "link":         LinkObject,
                                     "data":         dict})

        self.import_fields(operation_status)

class OperationStatusListObject(YaDiskObject):
    def __init__(self, operation_status_list=None):
        YaDiskObject.__init__(self, {"items": typed_list(OperationStatusObject)})
        self.import_fields(operation_status_list)
