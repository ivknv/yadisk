#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..ResourceObject import ResourceObject, ResourceListObject
from ....common import typed_list

__all__ = ["TrashResourceObject", "TrashResourceListObject"]

class TrashResourceObject(ResourceObject):
    def __init__(self, trash_resource=None):
        ResourceObject.__init__(self)
        self.set_field_type("embedded", TrashResourceListObject)
        self.set_field_type("origin_path", str)
        self.set_field_type("deleted", str)
        self.import_fields(trash_resource)

class TrashResourceListObject(ResourceListObject):
    def __init__(self, trash_resource_list=None):
        ResourceListObject.__init__(self)
        self.set_field_type("embedded", typed_list(TrashResourceObject))
        self.import_fields(trash_resource_list)
