# -*- coding: utf-8 -*-

from .yadisk_object import YaDiskObject
from .disk import UserPublicInfoObject
from ..common import typed_list, yandex_date

__all__ = ["CommentIDsObject", "EXIFObject", "FilesResourceListObject",
           "LastUploadedResourceListObject", "LinkObject", "OperationLinkObject",
           "PublicResourcesListObject", "ResourceListObject", "ResourceObject",
           "ResourceUploadLinkObject", "ShareInfoObject", "PublicResourceObject",
           "PublicResourceListObject", "TrashResourceObject", "TrashResourceListObject"]

class CommentIDsObject(YaDiskObject):
    """
        Comment IDs object.

        :param comment_ids: `dict` or `None`

        :ivar private_resource: `str`, comment ID for private resources
        :ivar public_resource: `str`, comment ID for public resources
    """

    def __init__(self, comment_ids=None):
        YaDiskObject.__init__(self, {"private_resource": str,
                                     "public_resource":  str})

        self.import_fields(comment_ids)

class EXIFObject(YaDiskObject):
    """
        EXIF metadata object.

        :param exif: `dict` or `None`

        :ivar date_time: :any:`datetime.datetime`, capture date
    """

    def __init__(self, exif=None):
        YaDiskObject.__init__(self, {"date_time": yandex_date})

        self.import_fields(exif)

class FilesResourceListObject(YaDiskObject):
    """
        Flat list of files.

        :param files_resource_list: `dict` or `None`

        :ivar items: `list`, flat list of files (:any:`ResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
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

        :ivar items: `list`, list of resources (:any:`ResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
    """

    def __init__(self, last_uploaded_resources_list=None):
        YaDiskObject.__init__(self, {"items":  typed_list(ResourceObject),
                                     "limit":  int})
        self.import_fields(last_uploaded_resources_list)

class LinkObject(YaDiskObject):
    """
        Link object.

        :param link: `dict` or `None`

        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
    """

    def __init__(self, link=None):
        YaDiskObject.__init__(self, {"href":      str,
                                     "method":    str,
                                     "templated": bool})

        self.import_fields(link)

class OperationLinkObject(LinkObject):
    """
        Operation link object.

        :param link: `dict` or `None`

        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
    """

    pass

class PublicResourcesListObject(YaDiskObject):
    """
        List of public resources.

        :param public_resources_list: `dict` or `None`

        :ivar items: `list`, list of public resources (:any:`PublicResourceObject`)
        :ivar type: `str`, resource type to filter by
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
    """

    def __init__(self, public_resources_list=None):
        YaDiskObject.__init__(self, {"items":  typed_list(PublicResourceObject),
                                     "type":   str,
                                     "limit":  int,
                                     "offset": int})

        self.import_fields(public_resources_list)

class ResourceObject(YaDiskObject):
    """
        Resource object.

        :param resource: `dict` or `None`

        :ivar antivirus_status: `str`, antivirus check status
        :ivar file: `str`, download URL
        :ivar size: `int`, file size
        :ivar public_key: `str`, public resource key
        :ivar sha256: `str`, SHA256 hash
        :ivar md5: `str`, MD5 hash
        :ivar embedded: :any:`ResourceListObject`, list of nested resources
        :ivar name: `str`, filename
        :ivar exif: :any:`EXIFObject`, EXIF metadata
        :ivar resource_id: `str`, resource ID
        :ivar custom_properties: `dict`, custom resource properties
        :ivar public_url: `str`, public URL
        :ivar share: :any:`ShareInfoObject`, shared folder information
        :ivar modified: :any:`datetime.datetime`, date of last modification
        :ivar created: :any:`datetime.datetime`, date of creation
        :ivar photoslice_time: :any:`datetime.datetime`, photo/video creation date
        :ivar mime_type: `str`, MIME type
        :ivar path: `str`, path to the resource
        :ivar preview: `str`, file preview URL
        :ivar comment_ids: :any:`CommentIDsObject`, comment IDs
        :ivar type: `str`, type ("file" or "dir")
        :ivar media_type: `str`, file type as determined by Yandex.Disk
        :ivar revision: `int`, Yandex.Disk revision at the time of last modification
    """

    def __init__(self, resource=None):
        YaDiskObject.__init__(self, {"antivirus_status":  str,
                                     "file":              str,
                                     "size":              int,
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
                                     "photoslice_time":   yandex_date,
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

        :ivar sort: `str`, sort type
        :ivar items: `list`, list of resources (:any:`ResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
        :ivar path: `str`, path to the directory that contains the elements of the list
        :ivar total: `int`, number of elements in the list
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

        :ivar operation_id: `str`, ID of the upload operation
        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
    """

    def __init__(self, resource_upload_link=None):
        LinkObject.__init__(self)
        self.set_field_type("operation_id", str)
        self.import_fields(resource_upload_link)

class ShareInfoObject(YaDiskObject):
    """
        Shared folder information object.

        :param share_info: `dict` or `None`

        :ivar is_root: `bool`, tells whether the folder is root
        :ivar is_owned: `bool`, tells whether the user is the owner of this directory
        :ivar rights: `str`, access rights
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

        :ivar antivirus_status: `str`, antivirus check status
        :ivar file: `str`, download URL
        :ivar size: `int`, file size
        :ivar public_key: `str`, public resource key
        :ivar sha256: `str`, SHA256 hash
        :ivar md5: `str`, MD5 hash
        :ivar embedded: :any:`PublicResourceObject`, list of nested resources
        :ivar name: `str`, filename
        :ivar exif: :any:`EXIFObject`, EXIF metadata
        :ivar resource_id: `str`, resource ID
        :ivar custom_properties: `dict`, custom resource properties
        :ivar public_url: `str`, public URL
        :ivar share: :any:`ShareInfoObject`, shared folder information
        :ivar modified: :any:`datetime.datetime`, date of last modification
        :ivar created: :any:`datetime.datetime`, date of creation
        :ivar photoslice_time: :any:`datetime.datetime`, photo/video creation date
        :ivar mime_type: `str`, MIME type
        :ivar path: `str`, path to the resource
        :ivar preview: `str`, file preview URL
        :ivar comment_ids: :any:`CommentIDsObject`, comment IDs
        :ivar type: `str`, type ("file" or "dir")
        :ivar media_type: `str`, file type as determined by Yandex.Disk
        :ivar revision: `int`, Yandex.Disk revision at the time of last modification
        :ivar view_count: `int`, number of times the public resource was viewed
        :ivar owner: :any:`UserPublicInfoObject`, owner of the public resource
    """

    def __init__(self, public_resource=None):
        ResourceObject.__init__(self)
        self.set_field_type("views_count", int)
        self.set_alias("view_count", "views_count")
        self.set_field_type("embedded", PublicResourceListObject)
        self.set_field_type("owner", UserPublicInfoObject)
        self.import_fields(public_resource)

class PublicResourceListObject(ResourceListObject):
    """
        List of public resources.

        :param public_resource_list: `dict` or `None`

        :ivar sort: `str`, sort type
        :ivar items: `list`, list of resources (:any:`ResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
        :ivar path: `str`, path to the directory that contains the elements of the list
        :ivar total: `int`, number of elements in the list
        :ivar public_key: `str`, public key of the resource
    """

    def __init__(self, public_resource_list=None):
        ResourceListObject.__init__(self)
        self.set_field_type("public_key", str)
        self.set_field_type("items", typed_list(PublicResourceObject))
        self.import_fields(public_resource_list)

class TrashResourceObject(ResourceObject):
    """
        Trash resource object.

        :param trash_resource: `dict` or `None`

        :ivar antivirus_status: `str`, antivirus check status
        :ivar file: `str`, download URL
        :ivar size: `int`, file size
        :ivar public_key: `str`, public resource key
        :ivar sha256: `str`, SHA256 hash
        :ivar md5: `str`, MD5 hash
        :ivar embedded: :any:`TrashResourceListObject`, list of nested resources
        :ivar name: `str`, filename
        :ivar exif: :any:`EXIFObject`, EXIF metadata
        :ivar resource_id: `str`, resource ID
        :ivar custom_properties: `dict`, custom resource properties
        :ivar public_url: `str`, public URL
        :ivar share: :any:`ShareInfoObject`, shared folder information
        :ivar modified: :any:`datetime.datetime`, date of last modification
        :ivar created: :any:`datetime.datetime`, date of creation
        :ivar photoslice_time: :any:`datetime.datetime`, photo/video creation date
        :ivar mime_type: `str`, MIME type
        :ivar path: `str`, path to the resource
        :ivar preview: `str`, file preview URL
        :ivar comment_ids: :any:`CommentIDsObject`, comment IDs
        :ivar type: `str`, type ("file" or "dir")
        :ivar media_type: `str`, file type as determined by Yandex.Disk
        :ivar revision: `int`, Yandex.Disk revision at the time of last modification
        :ivar origin_path: `str`, original path
        :ivar deleted: :any:`datetime.datetime`, date of deletion
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

        :ivar sort: `str`, sort type
        :ivar items: `list`, list of resources (:any:`TrashResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
        :ivar path: `str`, path to the directory that contains the elements of the list
        :ivar total: `int`, number of elements in the list
    """

    def __init__(self, trash_resource_list=None):
        ResourceListObject.__init__(self)
        self.set_field_type("items", typed_list(TrashResourceObject))
        self.import_fields(trash_resource_list)
