#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..ResourceObject import ResourceObject, ResourceListObject
from .UserPublicInfoObject import UserPublicInfoObject
from ....common import typed_list

__all__ = ["PublicResourceObject", "PublicResourceListObject"]

class PublicResourceObject(ResourceObject):
    def __init__(self, public_resource=None):
        ResourceObject.__init__(self)
        self.set_field_type("views_count", int)
        self.set_field_type("embedded", PublicResourceListObject)
        self.set_field_type("owner", UserPublicInfoObject)
        self.import_fields(public_resource)

class PublicResourceListObject(ResourceListObject):
    def __init__(self, public_resource_list=None):
        ResourceListObject.__init__(self)
        self.set_field_type("public_key", str)
        self.set_field_type("embedded", typed_list(PublicResourceObject))
        self.import_fields(public_resource_list)
