#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..YaDiskObject import YaDiskObject
from .ResourceObject import ResourceObject
from ...common import typed_list

__all__ = ["LastUploadedResourceListObject"]

class LastUploadedResourceListObject(YaDiskObject):
    def __init__(self, last_uploaded_resources_list=None):
        YaDiskObject.__init__(self, {"items":  typed_list(ResourceObject),
                                     "limit":  int})
        self.import_fields(last_uploaded_resources_list)
