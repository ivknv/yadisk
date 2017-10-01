#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..YaDiskObject import YaDiskObject
from .EXIFObject import EXIFObject
from .ShareInfoObject import ShareInfoObject
from .CommentIDsObject import CommentIDsObject
from ...common import typed_list, yandex_date

__all__ = ["ResourceObject", "ResourceListObject"]

class ResourceObject(YaDiskObject):
    def __init__(self, resource=None):
        YaDiskObject.__init__(self, {"size":              int,
                                     "public_key":        str,
                                     "sha256":            str,
                                     "embedded":          ResourceListObject,
                                     "name":              str,
                                     "exif":              EXIFObject,
                                     "resource_id":       str,
                                     "custom_properties": dict,
                                     "public_url":        str,
                                     "share":             ShareInfoObject,
                                     "modified":          yandex_date,
                                     "created":           yandex_date,
                                     "mime_type":         str,
                                     "path":              str,
                                     "preview":           str,
                                     "comment_ids":       CommentIDsObject,
                                     "type":              str,
                                     "media_type":        str,
                                     "md5":               str,
                                     "revision":          int})
        self.import_fields(resource)
        if resource is not None:
            self.embedded = resource.get("_embedded")

class ResourceListObject(YaDiskObject):
    def __init__(self, resource_list=None):
        YaDiskObject.__init__(self, {"sort":   str,
                                     "items":  typed_list(ResourceObject),
                                     "limit":  int,
                                     "offset": int,
                                     "path":   str,
                                     "total":  int})
        self.import_fields(resource_list)
