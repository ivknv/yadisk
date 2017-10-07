#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .YaDiskObject import YaDiskObject
from ..common import typed_list, yandex_date

__all__ = ["CommentIDsObject", "EXIFObject", "FilesResourceListObject",
           "LastUploadedResourceListObject", "LinkObject", "PublicResourcesListObject",
           "ResourceListObject", "ResourceObject", "ResourceUploadLinkObject",
           "ShareInfoObject", "PublicResourceObject", "PublicResourceListObject",
           "UserPublicInfoObject", "TrashResourceObject", "TrashResourceListObject"]

class CommentIDsObject(YaDiskObject):
    def __init__(self, comment_ids=None):
        YaDiskObject.__init__(self, {"private_resource": str,
                                     "public_resource":  str})

        self.import_fields(comment_ids)

class EXIFObject(YaDiskObject):
    def __init__(self, exif=None):
        YaDiskObject.__init__(self, {"date_time": yandex_date})

        self.import_fields(exif)

class FilesResourceListObject(YaDiskObject):
    def __init__(self, files_resource_list=None):
        YaDiskObject.__init__(self, {"items":  typed_list(ResourceObject),
                                     "limit":  int,
                                     "offset": int})

        self.import_fields(files_resource_list)

class LastUploadedResourceListObject(YaDiskObject):
    def __init__(self, last_uploaded_resources_list=None):
        YaDiskObject.__init__(self, {"items":  typed_list(ResourceObject),
                                     "limit":  int})
        self.import_fields(last_uploaded_resources_list)

class LinkObject(YaDiskObject):
    def __init__(self, link=None):
        YaDiskObject.__init__(self, {"href":      str,
                                     "method":    str,
                                     "templated": bool})

        self.import_fields(link)

class PublicResourcesListObject(YaDiskObject):
    def __init__(self, public_resources_list=None):
        YaDiskObject.__init__(self, {"items":  typed_list(ResourceObject),
                                     "type":   str,
                                     "limit":  int,
                                     "offset": int})

        self.import_fields(public_resources_list)

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

class ResourceUploadLinkObject(LinkObject):
    def __init__(self, resource_upload_link=None):
        LinkObject.__init__(self)
        self.set_field_type("operation_id", str)
        self.import_fields(resource_upload_link)

class ShareInfoObject(YaDiskObject):
    def __init__(self, share_info=None):
        YaDiskObject.__init__(self, {"is_root":  bool,
                                     "is_owned": bool,
                                     "rights":   str})
        self.import_fields(share_info)

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

class UserPublicInfoObject(YaDiskObject):
    def __init__(self, user_public_info=None):
        YaDiskObject.__init__(self, {"login":        str,
                                     "display_name": str,
                                     "uid":          str})
        self.import_fields(user_public_info)

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
