# -*- coding: utf-8 -*-

from functools import partial
from pathlib import PurePosixPath
from urllib.parse import urlencode, urlparse, parse_qs

from .yadisk_object import YaDiskObject
from .disk import UserPublicInfoObject
from ..common import (
    typed_list, yandex_date, is_resource_link, is_public_resource_link,
    ensure_path_has_schema, str_or_error, int_or_error, bool_or_error,
    dict_or_error, str_or_dict_or_error)

from typing import overload, Union, IO, AnyStr, Protocol, Optional, TYPE_CHECKING

from ..compat import Generator, List

if TYPE_CHECKING:
    from ..yadisk import YaDisk
    import datetime

__all__ = ["CommentIDsObject", "EXIFObject", "FilesResourceListObject",
           "LastUploadedResourceListObject", "LinkObject", "OperationLinkObject",
           "PublicResourcesListObject", "ResourceListObject", "ResourceObject",
           "ResourceUploadLinkObject", "ShareInfoObject", "PublicResourceObject",
           "PublicResourceListObject", "TrashResourceObject", "TrashResourceListObject",
           "ResourceLinkObject", "PublicResourceLinkObject", "ResourceDownloadLinkObject"]

class CommentIDsObject(YaDiskObject):
    """
        Comment IDs object.

        :param comment_ids: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar private_resource: `str`, comment ID for private resources
        :ivar public_resource: `str`, comment ID for public resources
    """

    private_resource: Optional[str]
    public_resource: Optional[str]

    def __init__(self,
                 comment_ids: Optional[dict] = None,
                 yadisk: Optional["YaDisk"] = None):
        YaDiskObject.__init__(
            self,
            {"private_resource": str_or_error,
             "public_resource":  str_or_error},
            yadisk)

        self.import_fields(comment_ids)

class EXIFObject(YaDiskObject):
    """
        EXIF metadata object.

        :param exif: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar date_time: :any:`datetime.datetime`, capture date
    """

    date_time: Optional["datetime.datetime"]

    def __init__(self,
                 exif: Optional[dict] = None,
                 yadisk: Optional["YaDisk"] = None):
        YaDiskObject.__init__(self, {"date_time": yandex_date}, yadisk)

        self.import_fields(exif)

class FilesResourceListObject(YaDiskObject):
    """
        Flat list of files.

        :param files_resource_list: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar items: `list`, flat list of files (:any:`ResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
    """

    items: Optional[List["ResourceObject"]]
    limit: Optional[int]
    offset: Optional[int]

    def __init__(self,
                 files_resource_list: Optional[dict] = None,
                 yadisk: Optional["YaDisk"] = None):
        YaDiskObject.__init__(
            self,
            {"items":  typed_list(partial(ResourceObject, yadisk=yadisk)),
             "limit":  int_or_error,
             "offset": int_or_error},
            yadisk)

        self.import_fields(files_resource_list)

class LastUploadedResourceListObject(YaDiskObject):
    """
        List of last uploaded resources.

        :param last_uploaded_resources_list: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar items: `list`, list of resources (:any:`ResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
    """

    items: Optional[List["ResourceObject"]]
    limit: Optional[int]

    def __init__(self,
                 last_uploaded_resources_list: Optional[dict] = None,
                 yadisk: Optional["YaDisk"] = None):
        YaDiskObject.__init__(
            self,
            {"items": typed_list(partial(ResourceObject, yadisk=yadisk)),
             "limit": int_or_error},
            yadisk)
        self.import_fields(last_uploaded_resources_list)

class LinkObject(YaDiskObject):
    """
        Link object.

        :param link: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
    """

    href: Optional[str]
    method: Optional[str]
    templated: Optional[bool]

    def __init__(self,
                 link: Optional[dict] = None,
                 yadisk: Optional["YaDisk"] = None):
        YaDiskObject.__init__(
            self,
            {"href":      str_or_error,
             "method":    str_or_error,
             "templated": bool_or_error},
            yadisk)

        self.import_fields(link)

class OperationLinkObject(LinkObject):
    """
        Operation link object.

        :param link: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
    """

    def get_status(self, **kwargs) -> str:
        """
            Get operation status.

            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises OperationNotFoundError: requested operation was not found

            :returns: `str`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.href is None:
            raise ValueError("OperationLinkObject has no link")

        return self._yadisk.get_operation_status(self.href, **kwargs)

class PublicResourcesListObject(YaDiskObject):
    """
        List of public resources.

        :param public_resources_list: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar items: `list`, list of public resources (:any:`PublicResourceObject`)
        :ivar type: `str`, resource type to filter by
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
    """

    items: Optional[List["PublicResourceObject"]]
    type: Optional[str]
    limit: Optional[int]
    offset: Optional[int]

    def __init__(self,
                 public_resources_list: Optional[dict] = None,
                 yadisk: Optional["YaDisk"] = None):
        YaDiskObject.__init__(
            self,
            {"items":  typed_list(partial(PublicResourceObject, yadisk=yadisk)),
             "type":   str_or_error,
             "limit":  int_or_error,
             "offset": int_or_error},
            yadisk)

        self.import_fields(public_resources_list)

class ResourceProtocol(Protocol):
    @property
    def type(self) -> Optional[str]: ...

    @property
    def path(self) -> Optional[str]: ...

    @property
    def public_key(self) -> Optional[str]: ...

    @property
    def public_url(self) -> Optional[str]: ...

    @property
    def file(self) -> Optional[str]: ...

    @property
    def _yadisk(self) -> Optional["YaDisk"]: ...

class ResourceObjectMethodsMixin:
    def get_meta(self: ResourceProtocol,
                 relative_path: Optional[str] = None, /, **kwargs) -> "ResourceObject":
        """
            Get meta information about a file/directory.

            :param relative_path: `str` or `None`, relative path from resource
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param sort: `str`, field to be used as a key to sort children resources
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: :any:`ResourceObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.get_meta(str(path), **kwargs)

    def get_public_meta(self: ResourceProtocol, **kwargs) -> "PublicResourceObject":
        """
            Get meta-information about a public resource.

            :param path: relative path to a resource in a public folder.
            :param offset: offset from the beginning of the list of nested resources
            :param limit: maximum number of nested elements to be included in the list
            :param sort: `str`, field to be used as a key to sort children resources
            :param preview_size: file preview size
            :param preview_crop: `bool`, allow preview crop
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: :any:`PublicResourceObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        public_key_or_url = self.public_key or self.public_url

        if public_key_or_url is None:
            raise ValueError("ResourceObject doesn't have a public_key/public_url")

        return self._yadisk.get_public_meta(public_key_or_url, **kwargs)

    def exists(self: ResourceProtocol,
               relative_path: Optional[str] = None, /, **kwargs) -> bool:
        """
            Check whether resource exists.

            :param relative_path: `str` or `None`, relative path from the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `bool`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.exists(str(path), **kwargs)

    def get_type(self: ResourceProtocol,
                 relative_path: Optional[str] = None, /, **kwargs) -> str:
        """
            Get resource type.

            :param relative_path: relative path from the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: "file" or "dir"
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.get_type(str(path), **kwargs)

    def is_dir(self: ResourceProtocol,
               relative_path: Optional[str] = None, /, **kwargs) -> bool:
        """
            Check whether resource is a directory.

            :param relative_path: relative path from the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.is_dir(str(path), **kwargs)

    def is_file(self: ResourceProtocol,
                relative_path: Optional[str] = None, /, **kwargs) -> bool:
        """
            Check whether resource is a file.

            :param relative_path: relative path from the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a file, `False` otherwise (even if it doesn't exist)
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.is_file(str(path), **kwargs)

    def listdir(self: ResourceProtocol,
                relative_path: Optional[str] = None, /, **kwargs) -> Generator["ResourceObject", None, None]:
        """
            Get contents of the resource.

            :param relative_path: relative path from resource
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises WrongResourceTypeError: resource is not a directory

            :returns: generator of :any:`ResourceObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.listdir(str(path), **kwargs)

    def public_listdir(self: ResourceProtocol, **kwargs) -> Generator["PublicResourceObject", None, None]:
        """
            Get contents of a public directory.

            :param path: relative path to the resource in the public folder.
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises WrongResourceTypeError: resource is not a directory

            :returns: generator of :any:`PublicResourceObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        public_key_or_url = self.public_key or self.public_url

        if public_key_or_url is None:
            raise ValueError("ResourceObject doesn't have a public_key/public_url")

        return self._yadisk.public_listdir(public_key_or_url, **kwargs)

    def get_upload_link(self: ResourceProtocol,
                        relative_path: Optional[str] = None, /, **kwargs) -> str:
        """
            Get a link to upload the file using the PUT request.

            :param relative_path: `str` or `None`, relative path to the resource
            :param overwrite: `bool`, determines whether to overwrite the destination
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises InsufficientStorageError: cannot upload file due to lack of storage space
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded

            :returns: `str`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.get_upload_link(str(path), **kwargs)

    def upload(self: ResourceProtocol,
               path_or_file: Union[str, IO[AnyStr]],
               relative_path: Optional[str] = None, /, **kwargs) -> "ResourceLinkObject":
        """
            Upload a file to disk.

            :param path_or_file: path or file-like object to be uploaded
            :param relative_path: `str` or `None`, destination path relative to the resource
            :param overwrite: if `True`, the resource will be overwritten if it already exists,
                              an error will be raised otherwise
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises InsufficientStorageError: cannot upload file due to lack of storage space
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded

            :returns: :any:`ResourceLinkObject`, link to the destination resource
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        dst_path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.upload(path_or_file, str(dst_path), **kwargs)

    def upload_url(self: ResourceProtocol,
                   url: str,
                   relative_path: Optional[str] = None, /, **kwargs) -> OperationLinkObject:
        """
            Upload a file from URL.

            :param url: source URL
            :param relative_path: `str` or `None`, destination path relative to the resource
            :param disable_redirects: `bool`, forbid redirects
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises PathExistsError: destination path already exists
            :raises InsufficientStorageError: cannot upload file due to lack of storage space
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded

            :returns: :any:`OperationLinkObject`, link to the asynchronous operation
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        dst_path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.upload_url(url, str(dst_path), **kwargs)

    def get_download_link(self: ResourceProtocol,
                          relative_path: Optional[str] = None, /, **kwargs) -> str:
        """
            Get a download link for a file (or a directory).

            :param relative_path: `str` or `None`, path relative to the resource
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: `str`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.get_download_link(str(path), **kwargs)

    @overload
    def download(self: ResourceProtocol,
                 dst_path_or_file: Union[str, IO[AnyStr]], /, **kwargs) -> "ResourceLinkObject":
        pass

    @overload
    def download(self: ResourceProtocol,
                 relative_path: Optional[str],
                 dst_path_or_file: Union[str, IO[AnyStr]], /, **kwargs) -> "ResourceLinkObject":
        pass

    def download(self: ResourceProtocol, *args, **kwargs) -> "ResourceLinkObject":
        """
            Download the file. This method takes 1 or 2 positional arguments:

            1. :code:`download(dst_path_or_file, /, **kwargs)`
            2. :code:`download(relative_path, dst_path_or_file, /, **kwargs)`

            If `relative_path` is empty or None (or not specified) this method
            will try to use the `file` attribute as a download link.

            :param relative_path: `str` or `None`, source path relative to the resource
            :param dst_path_or_file: destination path or file-like object
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`ResourceLinkObject`, link to the source resource
        """

        if len(args) == 1:
            relative_path, dst_path_or_file = None, args[0]
        elif len(args) == 2:
            relative_path, dst_path_or_file = args
        else:
            raise TypeError("download() takes 1 or 2 positional arguments")

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if not relative_path and hasattr(self, "file") and self.file is not None:
            self._yadisk.download_by_link(self.file, dst_path_or_file, **kwargs)

            return ResourceLinkObject.from_path(self.path, yadisk=self._yadisk)

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        src_path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.download(str(src_path), dst_path_or_file, **kwargs)

    @overload
    def patch(self: ResourceProtocol, properties: dict, **kwargs) -> "ResourceObject":
        pass

    @overload
    def patch(self: ResourceProtocol,
              relative_path: Union[str, None],
              properties: dict, **kwargs) -> "ResourceObject":
        pass

    def patch(self: ResourceProtocol, *args, **kwargs) -> "ResourceObject":
        """
            Update custom properties of a resource.
            This method takes 1 or 2 positional arguments:

            1. :code:`patch(properties, /, **kwargs)`
            2. :code:`patch(relative_path, properties, /, **kwargs)`

            :param relative_path: `str` or `None`, path relative to the resource
            :param properties: `dict`, custom properties to update
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`ResourceObject`
        """

        if len(args) == 1:
            relative_path, properties = None, args[0]
        elif len(args) == 2:
            relative_path, properties = args
        else:
            raise TypeError("patch() takes 1 or 2 positional arguments")

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.patch(str(path), properties, **kwargs)

    def publish(self: ResourceProtocol,
                relative_path: Optional[str] = None, /, **kwargs) -> "ResourceLinkObject":
        """
            Make a resource public.

            :param relative_path: `str` or `None`, relative path to the resource to be published
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`ResourceLinkObject`, link to the resource
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.publish(str(path), **kwargs)

    def unpublish(self: ResourceProtocol,
                  relative_path: Optional[str] = None, /, **kwargs) -> "ResourceLinkObject":
        """
            Make a public resource private.

            :param relative_path: `str` or `None`, relative path to the resource to be unpublished
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`ResourceLinkObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.unpublish(str(path), **kwargs)

    def mkdir(self: ResourceProtocol,
              relative_path: Optional[str] = None, /, **kwargs) -> "ResourceLinkObject":
        """
            Create a new directory.

            :param relative_path: `str` or `None`, relative path to the directory to be created
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises DirectoryExistsError: destination path already exists
            :raises InsufficientStorageError: cannot create directory due to lack of storage space
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`ResourceLinkObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.mkdir(str(path), **kwargs)

    def remove(self: ResourceProtocol,
               relative_path: Optional[str] = None, /, **kwargs) -> Optional[OperationLinkObject]:
        """
            Remove the resource.

            :param relative_path: `str` or `None`, relative path to the resource to be removed
            :param permanently: if `True`, the resource will be removed permanently,
                                otherwise, it will be just moved to the trash
            :param md5: `str`, MD5 hash of the file to remove
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises BadRequestError: MD5 check is only available for files
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`OperationLinkObject` if the operation is performed asynchronously, `None` otherwise
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.remove(str(path), **kwargs)

    @overload
    def move(self: ResourceProtocol,
             dst_path: str, /, **kwargs) -> Union["ResourceLinkObject", OperationLinkObject]:
        pass

    @overload
    def move(self: ResourceProtocol,
             relative_path: Optional[str],
             dst_path: str, /, **kwargs) -> Union["ResourceLinkObject", OperationLinkObject]:
        pass

    def move(self: ResourceProtocol, *args, **kwargs) -> Union["ResourceLinkObject", OperationLinkObject]:
        """
            Move resource to `dst_path`.
            This method takes 1 or 2 positional arguments:

            1. :code:`move(dst_path, /, **kwargs)`
            2. :code:`move(relative_path, dst_path, /, **kwargs)`

            :param relative_path: `str` or `None`, source path to be moved relative to the resource
            :param dst_path: destination path
            :param overwrite: `bool`, determines whether to overwrite the destination
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`ResourceLinkObject` or :any:`OperationLinkObject`
        """

        if len(args) == 1:
            relative_path, dst_path = None, args[0]
        elif len(args) == 2:
            relative_path, dst_path = args
        else:
            raise TypeError("move() takes 1 or 2 positional arguments")

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        src_path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.move(str(src_path), dst_path, **kwargs)

    @overload
    def rename(self: ResourceProtocol,
               new_name: str, /, **kwargs) -> Union["ResourceLinkObject", OperationLinkObject]:
        pass

    @overload
    def rename(self: ResourceProtocol,
               relative_path: Optional[str],
               new_name: str, /, **kwargs) -> Union["ResourceLinkObject", OperationLinkObject]:
        pass

    def rename(self: ResourceProtocol, *args, **kwargs) -> Union["ResourceLinkObject", OperationLinkObject]:
        """
            Rename `src_path` to have filename `new_name`.
            Does the same as `move()` but changes only the filename.

            :param relative_path: `str` or `None`, source path to be renamed relative to the resource
            :param new_name: target filename to rename to
            :param overwrite: `bool`, determines whether to overwrite the destination
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises ValueError: `new_name` is not a valid filename

            :returns: :any:`ResourceLinkObject` or :any:`OperationLinkObject`
        """

        if len(args) == 1:
            relative_path, new_name = None, args[0]
        elif len(args) == 2:
            relative_path, new_name = args
        else:
            raise TypeError("rename() takes 1 or 2 positional arguments")

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.rename(str(path), new_name, **kwargs)

    @overload
    def copy(self: ResourceProtocol,
             dst_path: str, /, **kwargs) -> Union["ResourceLinkObject", OperationLinkObject]:
        pass

    @overload
    def copy(self: ResourceProtocol,
             relative_path: Optional[str],
             dst_path: str, /, **kwargs) -> Union["ResourceLinkObject", OperationLinkObject]:
        pass

    def copy(self: ResourceProtocol, *args, **kwargs) -> Union["ResourceLinkObject", OperationLinkObject]:
        """
            Copy resource to `dst_path`.
            If the operation is performed asynchronously, returns the link to the operation,
            otherwise, returns the link to the newly created resource.

            This method takes 1 or 2 positional arguments:

            1. :code:`copy(dst_path, /, **kwargs)`
            2. :code:`copy(relative_path, dst_path, /, **kwargs)`

            :param src_path: `str` or `None`, source path relative to the resource
            :param dst_path: destination path
            :param overwrite: if `True` the destination path can be overwritten,
                              otherwise, an error will be raised
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises InsufficientStorageError: cannot complete request due to lack of storage space
            :raises ResourceIsLockedError: resource is locked by another request
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded

            :returns: :any:`ResourceLinkObject` or :any:`OperationLinkObject`
        """

        if len(args) == 1:
            relative_path, dst_path = None, args[0]
        elif len(args) == 2:
            relative_path, dst_path = args
        else:
            raise TypeError("copy() takes 1 or 2 positional arguments")

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        src_path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.copy(str(src_path), dst_path, **kwargs)

class ResourceObject(YaDiskObject, ResourceObjectMethodsMixin):
    """
        Resource object.

        :param resource: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

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

    antivirus_status: Optional[str]
    file: Optional[str]
    size: Optional[int]
    public_key: Optional[str]
    sha256: Optional[str]
    embedded: Optional["ResourceListObject"]
    _embedded: Optional["ResourceListObject"]
    name: Optional[str]
    exif: Optional[EXIFObject]
    resource_id: Optional[str]
    custom_properties: Optional[dict]
    public_url: Optional[str]
    share: Optional["ShareInfoObject"]
    modified: Optional["datetime.datetime"]
    created: Optional["datetime.datetime"]
    photoslice_time: Optional["datetime.datetime"]
    mime_type: Optional[str]
    path: Optional[str]
    preview: Optional[str]
    comment_ids: Optional[CommentIDsObject]
    type: Optional[str]
    media_type: Optional[str]
    md5: Optional[str]
    revision: Optional[int]

    def __init__(self, resource: Optional[dict] = None, yadisk: Optional["YaDisk"] = None):
        YaDiskObject.__init__(
            self,
            {"antivirus_status":  str_or_dict_or_error,
             "file":              str_or_error,
             "size":              int_or_error,
             "public_key":        str_or_error,
             "sha256":            str_or_error,
             "embedded":          partial(ResourceListObject, yadisk=yadisk),
             "name":              str_or_error,
             "exif":              partial(EXIFObject, yadisk=yadisk),
             "resource_id":       str_or_error,
             "custom_properties": dict_or_error,
             "public_url":        str_or_error,
             "share":             partial(ShareInfoObject, yadisk=yadisk),
             "modified":          yandex_date,
             "created":           yandex_date,
             "photoslice_time":   yandex_date,
             "mime_type":         str_or_error,
             "path":              str_or_error,
             "preview":           str_or_error,
             "comment_ids":       partial(CommentIDsObject, yadisk=yadisk),
             "type":              str_or_error,
             "media_type":        str_or_error,
             "md5":               str_or_error,
             "revision":          int_or_error},
            yadisk)
        self.set_alias("_embedded", "embedded")
        self.import_fields(resource)

class ResourceLinkObject(LinkObject, ResourceObjectMethodsMixin):
    """
        Resource link object.

        :param link: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
        :ivar path: `str`, path to the resource
    """

    path: Optional[str]

    def __init__(self, link: Optional[dict] = None, yadisk: Optional["YaDisk"] = None):
        LinkObject.__init__(self, link, yadisk)
        self.set_field_type("path", str_or_error)

        if self.href is not None and is_resource_link(self.href):
            try:
                self.path = ensure_path_has_schema(
                    parse_qs(urlparse(self.href).query).get("path", [])[0])
            except IndexError:
                pass

    @staticmethod
    def from_path(path: Optional[str], yadisk: Optional["YaDisk"] = None) -> "ResourceLinkObject":
        if path is None:
            return ResourceLinkObject(yadisk=yadisk)

        path = ensure_path_has_schema(path)

        return ResourceLinkObject(
            {"method": "GET",
             "href": "https://cloud-api.yandex.net/v1/disk/resources?" + urlencode({"path": path}),
             "templated": False},
            yadisk=yadisk)

class PublicResourceLinkObject(LinkObject, ResourceObjectMethodsMixin):
    """
        Public resource link object.

        :param link: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
        :ivar public_key: `str`, public key of the resource
        :ivar public_url: `str`, public URL of the resource
    """

    public_key: Optional[str]
    public_url: Optional[str]

    def __init__(self, link: Optional[dict] = None, yadisk: Optional["YaDisk"] = None):
        LinkObject.__init__(self, link, yadisk)
        self.set_field_type("public_key", str_or_error)
        self.set_field_type("public_url", str_or_error)
        self.set_field_type("path", str_or_error)

        if self.href is not None and is_public_resource_link(self.href):
            try:
                public_key_or_url = parse_qs(urlparse(self.href).query).get("public_key", [])[0]
            except IndexError:
                public_key_or_url = ""

            if public_key_or_url.startswith("http://") or public_key_or_url.startswith("https://"):
                self.public_url = public_key_or_url
            else:
                self.public_key = public_key_or_url

    @staticmethod
    def from_public_key(public_key: Optional[str], yadisk: Optional["YaDisk"] = None) -> "PublicResourceLinkObject":
        if public_key is None:
            return PublicResourceLinkObject(yadisk=yadisk)

        return PublicResourceLinkObject(
            {"method": "GET",
             "href": "https://cloud-api.yandex.net/v1/disk/public/resources?" + urlencode({"public_key": public_key}),
             "templated": False},
            yadisk=yadisk)

class ResourceListObject(YaDiskObject):
    """
        List of resources.

        :param resource_list: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar sort: `str`, sort type
        :ivar items: `list`, list of resources (:any:`ResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
        :ivar path: `str`, path to the directory that contains the elements of the list
        :ivar total: `int`, number of elements in the list
    """

    sort: Optional[str]
    items: Optional[List[ResourceObject]]
    limit: Optional[int]
    offset: Optional[int]
    path: Optional[str]
    total: Optional[int]

    def __init__(self, resource_list: Optional[dict] = None, yadisk: Optional["YaDisk"] = None):
        YaDiskObject.__init__(
            self,
            {"sort":   str_or_error,
             "items":  typed_list(partial(ResourceObject, yadisk=yadisk)),
             "limit":  int_or_error,
             "offset": int_or_error,
             "path":   str_or_error,
             "total":  int_or_error},
            yadisk)
        self.import_fields(resource_list)

class ResourceUploadLinkObject(LinkObject):
    """
        Resource upload link.

        :param resource_upload_link: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar operation_id: `str`, ID of the upload operation
        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
    """

    operation_id: Optional[str]

    def __init__(self,
                 resource_upload_link: Optional[dict] = None,
                 yadisk: Optional["YaDisk"] = None):
        LinkObject.__init__(self, None, yadisk)
        self.set_field_type("operation_id", str_or_error)
        self.import_fields(resource_upload_link)

class ResourceDownloadLinkObject(LinkObject):
    """
        Resource download link.

        :param link: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
    """

    pass

class ShareInfoObject(YaDiskObject):
    """
        Shared folder information object.

        :param share_info: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar is_root: `bool`, tells whether the folder is root
        :ivar is_owned: `bool`, tells whether the user is the owner of this directory
        :ivar rights: `str`, access rights
    """

    is_root: Optional[bool]
    is_owned: Optional[bool]
    rights: Optional[str]

    def __init__(self, share_info: Optional[dict] = None, yadisk: Optional["YaDisk"] = None):
        YaDiskObject.__init__(
            self,
            {"is_root":  bool_or_error,
             "is_owned": bool_or_error,
             "rights":   str_or_error},
            yadisk)
        self.import_fields(share_info)

class PublicResourceObject(ResourceObject):
    """
        Public resource object.

        :param resource: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

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

    views_count: Optional[int]
    view_count: Optional[int]
    embedded: Optional["PublicResourceListObject"]
    _embedded: Optional["PublicResourceListObject"]
    owner: Optional[UserPublicInfoObject]

    def __init__(self, public_resource=None, yadisk=None):
        ResourceObject.__init__(self, None, yadisk)
        self.set_field_type("views_count", int_or_error)
        self.set_alias("view_count", "views_count")
        self.set_field_type("embedded", partial(PublicResourceListObject, yadisk=yadisk))
        self.set_field_type("owner", partial(UserPublicInfoObject, yadisk=yadisk))
        self.import_fields(public_resource)

class PublicResourceListObject(ResourceListObject):
    """
        List of public resources.

        :param public_resource_list: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar sort: `str`, sort type
        :ivar items: `list`, list of resources (:any:`ResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
        :ivar path: `str`, path to the directory that contains the elements of the list
        :ivar total: `int`, number of elements in the list
        :ivar public_key: `str`, public key of the resource
    """

    public_key: Optional[str]
    items: Optional[List[PublicResourceObject]]

    def __init__(self,
                 public_resource_list: Optional[dict] = None,
                 yadisk: Optional["YaDisk"] = None):
        ResourceListObject.__init__(self, None, yadisk)
        self.set_field_type("public_key", str_or_error)
        self.set_field_type("items", typed_list(partial(PublicResourceObject, yadisk=yadisk)))
        self.import_fields(public_resource_list)

class TrashResourceObject(ResourceObject):
    """
        Trash resource object.

        :param trash_resource: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

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

    embedded: Optional["TrashResourceListObject"]
    _embedded: Optional["TrashResourceListObject"]
    origin_path: Optional[str]
    deleted: Optional["datetime.datetime"]

    def __init__(self,
                 trash_resource: Optional[dict] = None,
                 yadisk: Optional["YaDisk"] = None):
        ResourceObject.__init__(self, None, yadisk)
        self.set_field_type("embedded", partial(TrashResourceListObject, yadisk=yadisk))
        self.set_field_type("origin_path", str_or_error)
        self.set_field_type("deleted", yandex_date)
        self.import_fields(trash_resource)

    def get_meta(self: ResourceProtocol,
                 relative_path: Optional[str] = None, /, **kwargs) -> "TrashResourceObject":
        """
            Get meta information about a trash resource.

            :param relative_path: `str` or `None`, relative path to the trash resource
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param sort: `str`, field to be used as a key to sort children resources
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: :any:`TrashResourceObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.get_trash_meta(str(path), **kwargs)

    def exists(self: ResourceProtocol,
               relative_path: Optional[str] = None, /, **kwargs) -> bool:
        """
            Check whether the trash resource exists.

            :param relative_path: `str` or `None`, relative path to the trash resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `bool`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("TrashResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.trash_exists(str(path), **kwargs)

    def get_type(self: ResourceProtocol,
                 relative_path: Optional[str] = None, /, **kwargs) -> str:
        """
            Get trash resource type.

            :param relative_path: `str` or `None`, relative path to the trash resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: "file" or "dir"
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("TrashResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.get_trash_type(str(path), **kwargs)

    def is_dir(self: ResourceProtocol,
               relative_path: Optional[str] = None, /, **kwargs) -> bool:
        """
            Check whether resource is a trash directory.

            :param relative_path: `str` or `None`, relative path to the trash resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("TrashResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.is_trash_dir(str(path), **kwargs)

    def is_file(self: ResourceProtocol,
                relative_path: Optional[str] = None, /, **kwargs) -> bool:
        """
            Check whether resource is a trash file.

            :param relative_path: `str` or `None`, relative path to the trash resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a file, `False` otherwise (even if it doesn't exist)
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("TrashResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.is_trash_file(str(path), **kwargs)

    def listdir(self: ResourceProtocol,
                relative_path: Optional[str] = None, /, **kwargs) -> Generator["TrashResourceObject", None, None]:
        """
            Get contents of a trash resource.

            :param relative_path: `str` or `None`, relative path to the directory in the trash bin
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises WrongResourceTypeError: resource is not a directory

            :returns: generator of :any:`TrashResourceObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("TrashResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.trash_listdir(str(path), **kwargs)

    def remove(self: ResourceProtocol,
               relative_path: Optional[str] = None, /, **kwargs) -> Optional[OperationLinkObject]:
        """
            Remove a trash resource.

            :param relative_path: `str` or `None`, relative path to the trash resource to be deleted
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`OperationLinkObject` if the operation is performed asynchronously, `None` otherwise
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("TrashResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.remove_trash(str(path), **kwargs)

    @overload
    def restore(self: ResourceProtocol,
                dst_path: str, /, **kwargs) -> Union[ResourceLinkObject, OperationLinkObject]:
        pass

    @overload
    def restore(self: ResourceProtocol,
                relative_path: Optional[str],
                dst_path: str, /, **kwargs) -> Union[ResourceLinkObject, OperationLinkObject]:
        pass

    def restore(self: ResourceProtocol, *args, **kwargs) -> Union[ResourceLinkObject, OperationLinkObject]:
        """
            Restore a trash resource.
            Returns a link to the newly created resource or a link to the asynchronous operation.

            This method takes 1 or 2 positional arguments:

            1. :code:`restore(dst_path, /, **kwargs)`
            2. :code:`restore(relative_path=None, dst_path, /, **kwargs)`

            :param relative_path: `str` or `None`, relative path to the trash resource to be restored
            :param dst_path: destination path
            :param overwrite: `bool`, determines whether the destination can be overwritten
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :raises PathNotFoundError: resource was not found on Disk
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`ResourceLinkObject` or :any:`OperationLinkObject`
        """

        if len(args) == 0:
            relative_path = dst_path = None
        elif len(args) == 1:
            relative_path, dst_path = None, args[0]
        elif len(args) == 2:
            relative_path, dst_path = args
        else:
            raise TypeError("restore() takes up to 2 positional arguments")

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("TrashResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.restore_trash(str(path), dst_path, **kwargs)

    def get_public_meta(self, *args, **kwargs):
        """"""
        raise NotImplementedError

    def public_listdir(self, *args, **kwargs):
        """"""
        raise NotImplementedError

    def get_download_link(self, *args, **kwargs):
        """"""
        raise NotImplementedError

    def download(self, *args, **kwargs):
        """"""
        raise NotImplementedError

    def get_upload_link(self, *args, **kwargs):
        """"""
        raise NotImplementedError

    def upload(self, *args, **kwargs):
        """"""
        raise NotImplementedError

    def copy(self, *args, **kwargs):
        """"""
        raise NotImplementedError

    def move(self, *args, **kwargs):
        """"""
        raise NotImplementedError

    def rename(self, *args, **kwargs):
        """"""
        raise NotImplementedError

    def upload_url(self, *args, **kwargs):
        """"""
        raise NotImplementedError

    def patch(self, *args, **kwargs):
        raise NotImplementedError

    def publish(self, *args, **kwargs):
        """"""
        raise NotImplementedError

    def unpublish(self, *args, **kwargs):
        """"""
        raise NotImplementedError

    def mkdir(self, *args, **kwargs):
        """"""
        raise NotImplementedError

class TrashResourceListObject(ResourceListObject):
    """
        List of trash resources.

        :param trash_resource_list: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar sort: `str`, sort type
        :ivar items: `list`, list of resources (:any:`TrashResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
        :ivar path: `str`, path to the directory that contains the elements of the list
        :ivar total: `int`, number of elements in the list
    """

    items: Optional[List[TrashResourceObject]]

    def __init__(self,
                 trash_resource_list: Optional[dict] = None,
                 yadisk: Optional["YaDisk"] = None):
        ResourceListObject.__init__(self, None, yadisk)
        self.set_field_type("items", typed_list(partial(TrashResourceObject, yadisk=yadisk)))
        self.import_fields(trash_resource_list)
