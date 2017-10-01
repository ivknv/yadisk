#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .LinkObject import LinkObject

__all__ = ["ResourceUploadLink"]

class ResourceUploadLink(LinkObject):
    def __init__(self, resource_upload_link=None):
        LinkObject.__init__(self)
        self.set_field_type("operation_id", str)
        self.import_fields(resource_upload_link)
