#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..YaDiskObject import YaDiskObject
from .ResourceObject import ResourceObject
from ...common import typed_list

__all__ = ["FilesResourceListObject"]

class FilesResourceListObject(YaDiskObject):
    def __init__(self, files_resource_list=None):
        YaDiskObject.__init__(self, {"items":  typed_list(ResourceObject),
                                     "limit":  int,
                                     "offset": int})

        self.import_fields(files_resource_list)
