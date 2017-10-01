#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..YaDiskObject import YaDiskObject
from ..resources import LinkObject

__all__ = ["OperationStatusObject"]

class OperationStatusObject(YaDiskObject):
    def __init__(self, operation_status=None):
        YaDiskObject.__init__(self, {"type":         str,
                                     "status":       str,
                                     "operation_id": str,
                                     "link":         LinkObject,
                                     "data":         dict})

        self.import_fields(operation_status)
