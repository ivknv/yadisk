#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..YaDiskObject import YaDiskObject
from .OperationStatusObject import OperationStatusObject
from ...common import typed_list

__all__ = ["OperationStatusListObject"]

class OperationStatusListObject(YaDiskObject):
    def __init__(self, operation_status_list=None):
        YaDiskObject.__init__(self, {"items": typed_list(OperationStatusObject)})
        self.import_fields(operation_status_list)
