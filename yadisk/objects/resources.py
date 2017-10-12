#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .YaDiskObject import YaDiskObject
from .disk import UserObject
from ..common import typed_list, yandex_date

__all__ = ["CommentIDsObject", "EXIFObject", "FilesResourceListObject",
           "LastUploadedResourceListObject", "LinkObject", "PublicResourcesListObject",
           "ResourceListObject", "ResourceObject", "ResourceUploadLinkObject",
           "ShareInfoObject", "PublicResourceObject", "PublicResourceListObject",
           "TrashResourceObject", "TrashResourceListObject"]

class CommentIDsObject(YaDiskObject):
    """
        Comment IDs object.

        :param comment_ids: `dict` or `None`

        private_resource
            `str`, comment ID for private resources
        public_resource
            `str`, comment ID for public resources
    """

    def __init__(self, comment_ids=None):
        YaDiskObject.__init__(self, {"private_resource": str,
                                     "public_resource":  str})

        self.import_fields(comment_ids)

class EXIFObject(YaDiskObject):
    """
        EXIF metadata object.

        :param exif: `dict` or `None`

        date_time
            `datetime.datetime`, capture date
    """

    def __init__(self, exif=None):
        YaDiskObject.__init__(self, {"date_time": yandex_date})

        self.import_fields(exif)

class FilesResourceListObject(YaDiskObject):
    """
        Flat list of files.

        :param files_resource_list: `dict` or `None`

        items
            `list`, flat list of files (`ResourceObject`)
        limit
            `int`, maximum number of elements in the list
        offset
            `int`, offset from the beginning of the list
    """

    def __init__(self, files_resource_list=None):
        YaDiskObject.__init__(self, {"items":  typed_list(ResourceObject),
                                     "limit":  int,
                                     "offset": int})

        self.import_fields(files_resource_list)

class LastUploadedResourceListObject(YaDiskObject):
    """
        List of last uploaded resources.

        :param last_uploaded_resources_list: `dict` or `None`

        items
            `list`, list of resources (`ResourceObject`)
        limit
            `int`, maximum number of elements in the list
    """

    def __init__(self, last_uploaded_resources_list=None):
        YaDiskObject.__init__(self, {"items":  typed_list(ResourceObject),
                                     "limit":  int})
        self.import_fields(last_uploaded_resources_list)

class LinkObject(YaDiskObject):
    """
        Link object.

        :param link: `dict` or `None`

        href
            `str`, link URL
        method
            `str`, HTTP method
        templated
            `bool`, tells whether the URL is templated
    """

    def __init__(self, link=None):
        YaDiskObject.__init__(self, {"href":      str,
                                     "method":    str,
                                     "templated": bool})

        self.import_fields(link)

class PublicResourcesListObject(YaDiskObject):
    """
        List of public resources.

        :param public_resources_list: `dict` or `None`

        items
            `list`, list of public resources (`ResourceObject`)
        type
            `str`, resource type to filter by
        limit
            `int`, maximum number of elements in the list
        offset
            `int`, offset from the beginning of the list
    """

    def __init__(self, public_resources_list=None):
        YaDiskObject.__init__(self, {"items":  typed_list(ResourceObject),
                                     "type":   str,
                                     "limit":  int,
                                     "offset": int})

        self.import_fields(public_resources_list)

class ResourceObject(YaDiskObject):
    """
        Resource object.

        :param resource: `dict` or `None`

        size
            `int`, file size
        public_key
            `str`, public resource key
        sha256
            `str`, SHA256 hash
        md5
            `str`, MD5 hash
        embedded
            `ResourceListObject`, list of nested resources
        name
            `str`, filename
        exif
            `EXIFObject`, EXIF metadata
        resource_id
            `str`, resource ID
        custom_properties
            `dict`, custom resource properties
        public_url
            `str`, public URL
        share
            `ShareInfoObject`, shared folder information
        modified
            `datetime.datetime`, date of last modification
        created
            `datetime.datetime`, date of creation
        mime_type
            `str`, MIME type
        path
            `str`, path to the resource
        preview
            `str`, file preview URL
        comment_ids
            `CommentIDsObject`, comment IDs
        type
            `str`, type ("file" or "dir")
        media_type
            `str`, file type as determined by Yandex.Disk
        revision
            `int`, Yandex.Disk revision at the time of last modification
    """

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
        self.set_alias("_embedded", "embedded")
        self.import_fields(resource)

class ResourceListObject(YaDiskObject):
    """
        List of resources.

        :param resource_list: `dict` or `None`

        sort
            `str`, sort type
        items
            `list`, list of resources (`ResourceObject`)
        limit
            `int`, maximum number of elements in the list
        offset
            `int`, offset from the beginning of the list
        path
            `str`, path to the directory that contains the elements of the list
        total
            `int`, number of elements in the list
    """

    def __init__(self, resource_list=None):
        YaDiskObject.__init__(self, {"sort":   str,
                                     "items":  typed_list(ResourceObject),
                                     "limit":  int,
                                     "offset": int,
                                     "path":   str,
                                     "total":  int})
        self.import_fields(resource_list)

class ResourceUploadLinkObject(LinkObject):
    """
        Resource upload link.

        :param resource_upload_link: `dict` or `None`

        operation_id
            `str`, ID of the upload operation
        href
            `str`, link URL
        method
            `str`, HTTP method
        templated
            `bool`, tells whether the URL is templated
    """

    def __init__(self, resource_upload_link=None):
        LinkObject.__init__(self)
        self.set_field_type("operation_id", str)
        self.import_fields(resource_upload_link)

class ShareInfoObject(YaDiskObject):
    """
        Shared folder information object.

        :param share_info: `dict` or `None`

        is_root
            `bool`, tells whether the folder is root
        is_owned
            `bool`, tells whether the user is the owner of this directory
        rights
            `str`, access rights
    """

    def __init__(self, share_info=None):
        YaDiskObject.__init__(self, {"is_root":  bool,
                                     "is_owned": bool,
                                     "rights":   str})
        self.import_fields(share_info)

class PublicResourceObject(ResourceObject):
    """
        Public resource object.

        :param resource: `dict` or `None`

        size
            `int`, file size
        public_key
            `str`, public resource key
        sha256
            `str`, SHA256 hash
        md5
            `str`, MD5 hash
        embedded
            `PublicResourceObject`, list of nested resources
        name
            `str`, filename
        exif
            `EXIFObject`, EXIF metadata
        resource_id
            `str`, resource ID
        custom_properties
            `dict`, custom resource properties
        public_url
            `str`, public URL
        share
            `ShareInfoObject`, shared folder information
        modified
            `datetime.datetime`, date of last modification
        created
            `datetime.datetime`, date of creation
        mime_type
            `str`, MIME type
        path
            `str`, path to the resource
        preview
            `str`, file preview URL
        comment_ids
            `CommentIDsObject`, comment IDs
        type
            `str`, type ("file" or "dir")
        media_type
            `str`, file type as determined by Yandex.Disk
        revision
            `int`, Yandex.Disk revision at the time of last modification
        view_count
            `int`, number of times the public resource was viewed
        owner
            `UserObject`, owner of the public resource
    """

    def __init__(self, public_resource=None):
        ResourceObject.__init__(self)
        self.set_field_type("views_count", int)
        self.set_alias("view_count", "views_count")
        self.set_field_type("embedded", PublicResourceListObject)
        self.set_field_type("owner", UserObject)
        self.import_fields(public_resource)

class PublicResourceListObject(ResourceListObject):
    """
        List of public resources.

        :param public_resource_list: `dict` or `None`

        sort
            `str`, sort type
        items
            `list`, list of resources (`ResourceObject`)
        limit
            `int`, maximum number of elements in the list
        offset
            `int`, offset from the beginning of the list
        path
            `str`, path to the directory that contains the elements of the list
        total
            `int`, number of elements in the list
        public_key
            `str`, public key of the resource
    """

    def __init__(self, public_resource_list=None):
        ResourceListObject.__init__(self)
        self.set_field_type("public_key", str)
        self.set_field_type("embedded", typed_list(PublicResourceObject))
        self.import_fields(public_resource_list)

class TrashResourceObject(ResourceObject):
    """
        Trash resource object.

        :param trash_resource: `dict` or `None`

        size
            `int`, file size
        public_key
            `str`, public resource key
        sha256
            `str`, SHA256 hash
        md5
            `str`, MD5 hash
        embedded
            `TrashResourceList`, list of nested resources
        name
            `str`, filename
        exif
            `EXIFObject`, EXIF metadata
        resource_id
            `str`, resource ID
        custom_properties
            `dict`, custom resource properties
        public_url
            `str`, public URL
        share
            `ShareInfoObject`, shared folder information
        modified
            `datetime.datetime`, date of last modification
        created
            `datetime.datetime`, date of creation
        mime_type
            `str`, MIME type
        path
            `str`, path to the resource
        preview
            `str`, file preview URL
        comment_ids
            `CommentIDsObject`, comment IDs
        type
            `str`, type ("file" or "dir")
        media_type
            `str`, file type as determined by Yandex.Disk
        revision
            `int`, Yandex.Disk revision at the time of last modification
        origin_path
            `str`, original path
        deleted
            `datetime.datetime`, date of deletion
    """

    def __init__(self, trash_resource=None):
        ResourceObject.__init__(self)
        self.set_field_type("embedded", TrashResourceListObject)
        self.set_field_type("origin_path", str)
        self.set_field_type("deleted", yandex_date)
        self.import_fields(trash_resource)

class TrashResourceListObject(ResourceListObject):
    """
        List of trash resources.

        :param trash_resource_list: `dict` or `None`

        sort
            `str`, sort type
        items
            `list`, list of resources (`TrashResourceObject`)
        limit
            `int`, maximum number of elements in the list
        offset
            `int`, offset from the beginning of the list
        path
            `str`, path to the directory that contains the elements of the list
        total
            `int`, number of elements in the list
    """

    def __init__(self, trash_resource_list=None):
        ResourceListObject.__init__(self)
        self.set_field_type("embedded", typed_list(TrashResourceObject))
        self.import_fields(trash_resource_list)
