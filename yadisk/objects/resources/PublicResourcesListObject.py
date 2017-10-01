#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..YaDiskObject import YaDiskObject
from .ResourceObject import ResourceObject
from ...common import typed_list

__all__ = ["PublicResourcesListObject"]

class PublicResourcesListObject(YaDiskObject):
    def __init__(self, public_resources_list=None):
        YaDiskObject.__init__(self, {"items":  typed_list(ResourceObject),
                                     "type":   str,
                                     "limit":  int,
                                     "offset": int})

        self.import_fields(public_resources_list)
