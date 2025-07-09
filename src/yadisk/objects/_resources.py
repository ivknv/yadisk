# -*- coding: utf-8 -*-
# Copyright © 2024 Ivan Konovalov

# This file is part of a Python library yadisk.

# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, see <http://www.gnu.org/licenses/>.

from functools import partial
from pathlib import PurePosixPath
from urllib.parse import urlencode, urlparse, parse_qs

from ._yadisk_object import YaDiskObject
from ._link_object import LinkObject
from ._disk import UserPublicInfoObject
from .._common import (
    typed_list, yandex_date, is_resource_link, is_public_resource_link,
    ensure_path_has_schema, str_or_error, int_or_error, float_or_error,
    bool_or_error, dict_or_error, str_or_dict_or_error
)
from ..types import (
    JSON, AsyncFileOrPath, AsyncFileOrPathDestination, FileOrPath,
    FileOrPathDestination
)

from .. import settings

from typing import (
    TYPE_CHECKING, Any, Literal, overload, Union, Protocol, Optional
)

from .._typing_compat import Generator, Dict, List, AsyncGenerator

if TYPE_CHECKING:  # pragma: no cover
    import datetime
    from ._operations import (
        OperationLinkObject, AsyncOperationLinkObject, SyncOperationLinkObject
    )

__all__ = [
    "AsyncFilesResourceListObject",
    "AsyncLastUploadedResourceListObject",
    "AsyncPublicResourceLinkObject",
    "AsyncPublicResourceListObject",
    "AsyncPublicResourceObject",
    "AsyncPublicResourcesListObject",
    "AsyncResourceLinkObject",
    "AsyncResourceListObject",
    "AsyncResourceObject",
    "AsyncTrashResourceListObject",
    "AsyncTrashResourceObject",
    "AvailableUntilVerboseObject",
    "CommentIDsObject",
    "EXIFObject",
    "ExternalOrganizationIdVerboseObject",
    "FilesResourceListObject",
    "LastUploadedResourceListObject",
    "PasswordVerboseObject",
    "PublicAccessObject",
    "PublicAvailableSettingsObject",
    "PublicDefaultObject",
    "PublicResourceLinkObject",
    "PublicResourceListObject",
    "PublicResourceObject",
    "PublicResourcesListObject",
    "PublicSettingsObject",
    "ResourceDownloadLinkObject",
    "ResourceLinkObject",
    "ResourceListObject",
    "ResourceObject",
    "ResourceUploadLinkObject",
    "ShareInfoObject",
    "SyncFilesResourceListObject",
    "SyncLastUploadedResourceListObject",
    "SyncPublicResourceLinkObject",
    "SyncPublicResourceListObject",
    "SyncPublicResourceObject",
    "SyncPublicResourcesListObject",
    "SyncResourceLinkObject",
    "SyncResourceListObject",
    "SyncResourceObject",
    "SyncTrashResourceListObject",
    "SyncTrashResourceObject",
    "TrashResourceListObject",
    "TrashResourceObject",
]


class CommentIDsObject(YaDiskObject):
    """
        Comment IDs object.

        :param comment_ids: `dict` or `None`
        :param yadisk: :any:`Client`/:any:`AsyncClient` or `None`, `YaDisk` object

        :ivar private_resource: `str`, comment ID for private resources
        :ivar public_resource: `str`, comment ID for public resources
    """

    private_resource: Optional[str]
    public_resource: Optional[str]

    def __init__(self,
                 comment_ids: Optional[Dict] = None,
                 yadisk: Optional[Any] = None):
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
        :param yadisk: :any:`Client`/:any:`AsyncClient` or `None`, `YaDisk` object

        :ivar date_time: :any:`datetime.datetime`, capture date
        :ivar gps_longitude: `float`, longitude of the photo's location
        :ivar gps_latitude: `float`, latitude of the photo's location
    """

    date_time:     Optional["datetime.datetime"]
    gps_longitude: Optional[float]
    gps_latitude:  Optional[float]

    def __init__(
        self,
        exif: Optional[Dict] = None,
        yadisk: Optional[Any] = None
    ) -> None:
        YaDiskObject.__init__(
            self,
            {
                "date_time": yandex_date,
                "gps_longitude": float_or_error,
                "gps_latitude": float_or_error
            },
            yadisk
        )

        self.import_fields(exif)


class FilesResourceListObject(YaDiskObject):
    """
        Flat list of files.

        :param files_resource_list: `dict` or `None`
        :param yadisk: :any:`Client`/:any:`AsyncClient` or `None`, `YaDisk` object

        :ivar items: `list`, flat list of files (:any:`ResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
    """

    items: Optional[List["ResourceObject"]]
    limit: Optional[int]
    offset: Optional[int]

    def __init__(self,
                 files_resource_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None):
        YaDiskObject.__init__(
            self,
            {"items":  typed_list(partial(ResourceObject, yadisk=yadisk)),
             "limit":  int_or_error,
             "offset": int_or_error},
            yadisk)

        self.import_fields(files_resource_list)


class SyncFilesResourceListObject(FilesResourceListObject):
    """
        Flat list of files.

        :param files_resource_list: `dict` or `None`
        :param yadisk: :any:`Client` or `None`, `YaDisk` object

        :ivar items: `list`, flat list of files (:any:`SyncResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
    """

    items: Optional[List["SyncResourceObject"]]  # type: ignore[assignment]

    def __init__(self,
                 files_resource_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None):
        FilesResourceListObject.__init__(self, None, yadisk)

        self.set_field_type("items", typed_list(partial(SyncResourceObject, yadisk=yadisk)))
        self.import_fields(files_resource_list)


class AsyncFilesResourceListObject(FilesResourceListObject):
    """
        Flat list of files.

        :param files_resource_list: `dict` or `None`
        :param yadisk: :any:`AsyncClient` or `None`, `YaDisk` object

        :ivar items: `list`, flat list of files (:any:`AsyncResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
    """

    items: Optional[List["AsyncResourceObject"]]  # type: ignore[assignment]

    def __init__(self,
                 files_resource_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None):
        FilesResourceListObject.__init__(self, None, yadisk)

        self.set_field_type("items", typed_list(partial(AsyncResourceObject, yadisk=yadisk)))
        self.import_fields(files_resource_list)


class LastUploadedResourceListObject(YaDiskObject):
    """
        List of last uploaded resources.

        :param last_uploaded_resources_list: `dict` or `None`
        :param yadisk: :any:`Client`/:any:`AsyncClient` or `None`, `YaDisk` object

        :ivar items: `list`, list of resources (:any:`ResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
    """

    items: Optional[List["ResourceObject"]]
    limit: Optional[int]

    def __init__(self,
                 last_uploaded_resources_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None):
        YaDiskObject.__init__(
            self,
            {"items": typed_list(partial(ResourceObject, yadisk=yadisk)),
             "limit": int_or_error},
            yadisk)
        self.import_fields(last_uploaded_resources_list)


class SyncLastUploadedResourceListObject(LastUploadedResourceListObject):
    """
        List of last uploaded resources.

        :param last_uploaded_resources_list: `dict` or `None`
        :param yadisk: :any:`Client` or `None`, `YaDisk` object

        :ivar items: `list`, list of resources (:any:`SyncResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
    """

    items: Optional[List["SyncResourceObject"]]  # type: ignore[assignment]

    def __init__(self,
                 last_uploaded_resources_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None):
        LastUploadedResourceListObject.__init__(self, None, yadisk)

        self.set_field_type("items", typed_list(partial(SyncResourceObject, yadisk=yadisk)))
        self.import_fields(last_uploaded_resources_list)


class AsyncLastUploadedResourceListObject(LastUploadedResourceListObject):
    """
        List of last uploaded resources.

        :param last_uploaded_resources_list: `dict` or `None`
        :param yadisk: :any:`AsyncClient` or `None`, `YaDisk` object

        :ivar items: `list`, list of resources (:any:`AsyncResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
    """

    items: Optional[List["AsyncResourceObject"]]  # type: ignore[assignment]

    def __init__(self,
                 last_uploaded_resources_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None):
        LastUploadedResourceListObject.__init__(self, None, yadisk)

        self.set_field_type("items", typed_list(partial(AsyncResourceObject, yadisk=yadisk)))
        self.import_fields(last_uploaded_resources_list)


class PublicResourcesListObject(YaDiskObject):
    """
        List of public resources.

        :param public_resources_list: `dict` or `None`
        :param yadisk: :any:`Client`/:any:`AsyncClient` or `None`, `YaDisk` object

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
                 public_resources_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None):
        YaDiskObject.__init__(
            self,
            {"items":  typed_list(partial(PublicResourceObject, yadisk=yadisk)),
             "type":   str_or_error,
             "limit":  int_or_error,
             "offset": int_or_error},
            yadisk)

        self.import_fields(public_resources_list)


class SyncPublicResourcesListObject(PublicResourcesListObject):
    """
        List of public resources.

        :param public_resources_list: `dict` or `None`
        :param yadisk: :any:`Client` or `None`, `YaDisk` object

        :ivar items: `list`, list of public resources (:any:`SyncPublicResourceObject`)
        :ivar type: `str`, resource type to filter by
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
    """

    items: Optional[List["SyncPublicResourceObject"]]  # type: ignore[assignment]

    def __init__(self,
                 public_resources_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None):
        PublicResourcesListObject.__init__(self, None, yadisk)
        self.set_field_type("items", typed_list(partial(SyncPublicResourceObject, yadisk=yadisk)))

        self.import_fields(public_resources_list)


class AsyncPublicResourcesListObject(PublicResourcesListObject):
    """
        List of public resources.

        :param public_resources_list: `dict` or `None`
        :param yadisk: :any:`AsyncClient` or `None`, `YaDisk` object

        :ivar items: `list`, list of public resources (:any:`AsyncPublicResourceObject`)
        :ivar type: `str`, resource type to filter by
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
    """

    items: Optional[List["AsyncPublicResourceObject"]]  # type: ignore[assignment]

    def __init__(self,
                 public_resources_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None):
        PublicResourcesListObject.__init__(self, None, yadisk)
        self.set_field_type("items", typed_list(partial(AsyncPublicResourceObject, yadisk=yadisk)))

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
    def _yadisk(self) -> Optional[Any]: ...


class ResourceObjectMethodsMixin:
    def get_meta(self: ResourceProtocol,
                 relative_path: Optional[str] = None, /, **kwargs) -> "SyncResourceObject":
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
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: :any:`SyncResourceObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.get_meta(str(path), **kwargs)

    def get_public_meta(self: ResourceProtocol, **kwargs) -> "SyncPublicResourceObject":
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
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: :any:`SyncPublicResourceObject`
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
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

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
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

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
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

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
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a file, `False` otherwise (even if it doesn't exist)
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.is_file(str(path), **kwargs)

    def listdir(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        **kwargs
    ) -> Generator["SyncResourceObject", None, None]:
        """
            Get contents of the resource.

            :param relative_path: relative path from resource
            :param limit: number of children resources to be included in the response
            :param max_items: `int` or `None`, maximum number of returned items (`None` means unlimited)
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises WrongResourceTypeError: resource is not a directory

            :returns: generator of :any:`SyncResourceObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.listdir(str(path), **kwargs)

    def public_listdir(
        self: ResourceProtocol,
        **kwargs
    ) -> Generator["SyncPublicResourceObject", None, None]:
        """
            Get contents of a public directory.

            :param path: relative path to the resource in the public folder.
            :param max_items: `int` or `None`, maximum number of returned items (`None` means unlimited)
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises WrongResourceTypeError: resource is not a directory

            :returns: generator of :any:`SyncPublicResourceObject`
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
            :param spoof_user_agent: `bool`, if `True` (default), the `User-Agent` header
                will be set to a special value, which should allow bypassing of
                Yandex.Disk's upload speed limit
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

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

    def get_upload_link_object(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        **kwargs
    ) -> "ResourceUploadLinkObject":
        """
            Get a link to upload the file using the PUT request.
            This is similar to :any:`Client.get_upload_link()`, except it returns
            an instance of :any:`ResourceUploadLinkObject` which also contains
            an asynchronous operation ID.

            :param relative_path: `str` or `None`, relative path to the resource
            :param overwrite: `bool`, determines whether to overwrite the destination
            :param fields: list of keys to be included in the response
            :param spoof_user_agent: `bool`, if `True` (default), the `User-Agent` header
                will be set to a special value, which should allow bypassing of
                Yandex.Disk's upload speed limit
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises InsufficientStorageError: cannot upload file due to lack of storage space
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded

            :returns: :any:`ResourceUploadLinkObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.get_upload_link_object(str(path), **kwargs)

    def upload(self: ResourceProtocol,
               path_or_file: FileOrPath,
               relative_path: Optional[str] = None, /, **kwargs) -> "SyncResourceLinkObject":
        """
            Upload a file to disk.

            :param path_or_file: path or file-like object to be uploaded
            :param relative_path: `str` or `None`, destination path relative to the resource
            :param overwrite: if `True`, the resource will be overwritten if it already exists,
                              an error will be raised otherwise
            :param spoof_user_agent: `bool`, if `True` (default), the `User-Agent` header
                will be set to a special value, which should allow bypassing of
                Yandex.Disk's upload speed limit
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises InsufficientStorageError: cannot upload file due to lack of storage space
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded

            :returns: :any:`SyncResourceLinkObject`, link to the destination resource
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        dst_path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.upload(path_or_file, str(dst_path), **kwargs)

    def upload_url(self: ResourceProtocol,
                   url: str,
                   relative_path: Optional[str] = None, /, **kwargs) -> "OperationLinkObject":
        """
            Upload a file from URL.

            :param url: source URL
            :param relative_path: `str` or `None`, destination path relative to the resource
            :param disable_redirects: `bool`, forbid redirects
            :param fields: list of keys to be included in the response
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises PathExistsError: destination path already exists
            :raises InsufficientStorageError: cannot upload file due to lack of storage space
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            :returns: :any:`SyncOperationLinkObject`, link to the asynchronous operation
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
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

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
                 dst_path_or_file: FileOrPathDestination, /, **kwargs) -> "SyncResourceLinkObject":
        pass

    @overload
    def download(self: ResourceProtocol,
                 relative_path: Optional[str],
                 dst_path_or_file: FileOrPathDestination, /, **kwargs) -> "SyncResourceLinkObject":
        pass

    def download(self: ResourceProtocol, /, *args, **kwargs) -> "SyncResourceLinkObject":
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
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`SyncResourceLinkObject`, link to the source resource
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

            return SyncResourceLinkObject.from_path(self.path, yadisk=self._yadisk)

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        src_path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.download(str(src_path), dst_path_or_file, **kwargs)

    @overload
    def patch(self: ResourceProtocol, properties: Dict, **kwargs) -> "SyncResourceObject":
        pass

    @overload
    def patch(self: ResourceProtocol,
              relative_path: Union[str, None],
              properties: Dict, **kwargs) -> "SyncResourceObject":
        pass

    def patch(self: ResourceProtocol, *args, **kwargs) -> "SyncResourceObject":
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
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`SyncResourceObject`
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

    def publish(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        **kwargs
    ) -> "SyncResourceLinkObject":
        """
            Make a resource public.

            :param relative_path: `str` or `None`, relative path to the resource to be published
            :param allow_address_access: `bool`, specifies the request format, i.e.
                with personal access settings (when set to `True`) or without
            :param public_settings: :any:`PublicSettings` or `None`, public access settings for the resource
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`SyncResourceLinkObject`, link to the resource
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.publish(str(path), **kwargs)

    def unpublish(self: ResourceProtocol,
                  relative_path: Optional[str] = None, /, **kwargs) -> "SyncResourceLinkObject":
        """
            Make a public resource private.

            :param relative_path: `str` or `None`, relative path to the resource to be unpublished
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`SyncResourceLinkObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.unpublish(str(path), **kwargs)

    def get_public_settings(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        **kwargs
    ) -> "PublicSettingsObject":
        """
            Get public settings of a resource.

            :param relative_path: `str` or `None`, relative path to the resource to be published
            :param allow_address_access: `bool`, specifies the request format, i.e.
                with personal access settings (when set to `True`) or without
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`PublicSettingsObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.get_public_settings(str(path), **kwargs)

    def get_public_available_settings(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        **kwargs
    ) -> "PublicSettingsObject":
        """
            Get public settings of a shared resource for the current OAuth token owner.

            :param relative_path: `str` or `None`, relative path to the resource to be published
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`PublicAvailableSettingsObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.get_public_available_settings(str(path), **kwargs)

    def update_public_settings(
        self: ResourceProtocol,
        *args,
        **kwargs
    ) -> "PublicSettingsObject":
        """
            Get public settings of a shared resource for the current OAuth token owner.
            This method takes 1 or 2 positional arguments:
            1. :code:`update_public_settings(public_settings, /, **kwargs)`
            2. :code:`update_public_settings(relative_path, public_settings, /, **kwargs)`

            :param relative_path: `str` or `None`, relative path to the resource to be published
            :param public_settings: :any:`PublicSettings`, public access settings for the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`PublicAvailableSettingsObject`
        """

        if len(args) == 1:
            relative_path, public_settings = None, args[0]
        elif len(args) == 2:
            relative_path, public_settings = args
        else:
            raise TypeError("update_public_settings() takes 1 or 2 positional arguments")

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.update_public_settings(str(path), public_settings, **kwargs)

    def mkdir(self: ResourceProtocol,
              relative_path: Optional[str] = None, /, **kwargs) -> "SyncResourceLinkObject":
        """
            Create a new directory.

            :param relative_path: `str` or `None`, relative path to the directory to be created
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises DirectoryExistsError: destination path already exists
            :raises InsufficientStorageError: cannot create directory due to lack of storage space
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`SyncResourceLinkObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.mkdir(str(path), **kwargs)

    def makedirs(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        **kwargs
    ) -> "SyncResourceLinkObject":
        """
            Create a new directory at `path`. If its parent directory doesn't
            exist it will also be created recursively.

            :param relative_path: `str` or `None`, relative path to the directory to be created
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises DirectoryExistsError: destination path already exists
            :raises InsufficientStorageError: cannot create directory due to lack of storage space
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`SyncResourceLinkObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.makedirs(str(path), **kwargs)

    def remove(self: ResourceProtocol,
               relative_path: Optional[str] = None, /, **kwargs) -> Optional["SyncOperationLinkObject"]:
        """
            Remove the resource.

            :param relative_path: `str` or `None`, relative path to the resource to be removed
            :param permanently: if `True`, the resource will be removed permanently,
                                otherwise, it will be just moved to the trash
            :param md5: `str`, MD5 hash of the file to remove
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises BadRequestError: MD5 check is only available for files
            :raises ResourceIsLockedError: resource is locked by another request
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            :returns: :any:`SyncOperationLinkObject` if the operation is performed asynchronously, `None` otherwise
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.remove(str(path), **kwargs)

    @overload
    def move(self: ResourceProtocol,
             dst_path: str, /, **kwargs) -> Union["SyncResourceLinkObject", "SyncOperationLinkObject"]:
        pass

    @overload
    def move(self: ResourceProtocol,
             relative_path: Optional[str],
             dst_path: str, /, **kwargs) -> Union["SyncResourceLinkObject", "SyncOperationLinkObject"]:
        pass

    def move(self: ResourceProtocol, /, *args, **kwargs) -> Union["SyncResourceLinkObject", "SyncOperationLinkObject"]:
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
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            :returns: :any:`SyncResourceLinkObject` or :any:`SyncOperationLinkObject`
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
               new_name: str, /, **kwargs) -> Union["SyncResourceLinkObject", "SyncOperationLinkObject"]:
        pass

    @overload
    def rename(self: ResourceProtocol,
               relative_path: Optional[str],
               new_name: str, /, **kwargs) -> Union["SyncResourceLinkObject", "SyncOperationLinkObject"]:
        pass

    def rename(
        self: ResourceProtocol,
        /,
        *args,
        **kwargs
    ) -> Union["SyncResourceLinkObject", "SyncOperationLinkObject"]:
        """
            Rename `src_path` to have filename `new_name`.
            Does the same as `move()` but changes only the filename.

            :param relative_path: `str` or `None`, source path to be renamed relative to the resource
            :param new_name: target filename to rename to
            :param overwrite: `bool`, determines whether to overwrite the destination
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises ValueError: `new_name` is not a valid filename
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            :returns: :any:`SyncResourceLinkObject` or :any:`SyncOperationLinkObject`
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
             dst_path: str, /, **kwargs) -> Union["SyncResourceLinkObject", "SyncOperationLinkObject"]:
        pass

    @overload
    def copy(self: ResourceProtocol,
             relative_path: Optional[str],
             dst_path: str, /, **kwargs) -> Union["SyncResourceLinkObject", "SyncOperationLinkObject"]:
        pass

    def copy(self: ResourceProtocol, /, *args, **kwargs) -> Union["SyncResourceLinkObject", "SyncOperationLinkObject"]:
        """
            Copy resource to `dst_path`.
            If the operation is performed asynchronously, returns the link to the operation,
            otherwise, returns the link to the newly created resource.

            This method takes 1 or 2 positional arguments:

            1. :code:`copy(dst_path, /, **kwargs)`
            2. :code:`copy(relative_src_path, dst_path, /, **kwargs)`

            :param relative_src_path: `str` or `None`, source path relative to the resource
            :param dst_path: destination path
            :param overwrite: if `True` the destination path can be overwritten,
                              otherwise, an error will be raised
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises InsufficientStorageError: cannot complete request due to lack of storage space
            :raises ResourceIsLockedError: resource is locked by another request
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            :returns: :any:`SyncResourceLinkObject` or :any:`SyncOperationLinkObject`
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


class AsyncResourceObjectMethodsMixin:
    async def get_meta(
        self: ResourceProtocol,
        relative_path: Optional[str] = None, /, **kwargs
    ) -> "AsyncResourceObject":
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
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: :any:`AsyncResourceObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.get_meta(str(path), **kwargs)

    async def get_public_meta(self: ResourceProtocol, **kwargs) -> "AsyncPublicResourceObject":
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
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: :any:`AsyncPublicResourceObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        public_key_or_url = self.public_key or self.public_url

        if public_key_or_url is None:
            raise ValueError("ResourceObject doesn't have a public_key/public_url")

        return await self._yadisk.get_public_meta(public_key_or_url, **kwargs)

    async def exists(self: ResourceProtocol,
                     relative_path: Optional[str] = None, /, **kwargs) -> bool:
        """
            Check whether resource exists.

            :param relative_path: `str` or `None`, relative path from the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `bool`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.exists(str(path), **kwargs)

    async def get_type(self: ResourceProtocol,
                       relative_path: Optional[str] = None, /, **kwargs) -> str:
        """
            Get resource type.

            :param relative_path: relative path from the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: "file" or "dir"
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.get_type(str(path), **kwargs)

    async def is_dir(self: ResourceProtocol,
                     relative_path: Optional[str] = None, /, **kwargs) -> bool:
        """
            Check whether resource is a directory.

            :param relative_path: relative path from the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.is_dir(str(path), **kwargs)

    async def is_file(self: ResourceProtocol,
                      relative_path: Optional[str] = None, /, **kwargs) -> bool:
        """
            Check whether resource is a file.

            :param relative_path: relative path from the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a file, `False` otherwise (even if it doesn't exist)
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.is_file(str(path), **kwargs)

    async def listdir(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        **kwargs
    ) -> AsyncGenerator["AsyncResourceObject", None]:
        """
            Get contents of the resource.

            :param relative_path: relative path from resource
            :param max_items: `int` or `None`, maximum number of returned items (`None` means unlimited)
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises WrongResourceTypeError: resource is not a directory

            :returns: generator of :any:`AsyncResourceObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        async for i in self._yadisk.listdir(str(path), **kwargs):
            yield i

    async def public_listdir(
        self: ResourceProtocol,
        **kwargs
    ) -> AsyncGenerator["AsyncPublicResourceObject", None]:
        """
            Get contents of a public directory.

            :param path: relative path to the resource in the public folder.
            :param max_items: `int` or `None`, maximum number of returned items (`None` means unlimited)
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises WrongResourceTypeError: resource is not a directory

            :returns: generator of :any:`AsyncPublicResourceObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        public_key_or_url = self.public_key or self.public_url

        if public_key_or_url is None:
            raise ValueError("ResourceObject doesn't have a public_key/public_url")

        async for i in self._yadisk.public_listdir(public_key_or_url, **kwargs):
            yield i

    async def get_upload_link(self: ResourceProtocol,
                              relative_path: Optional[str] = None, /, **kwargs) -> str:
        """
            Get a link to upload the file using the PUT request.

            :param relative_path: `str` or `None`, relative path to the resource
            :param overwrite: `bool`, determines whether to overwrite the destination
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

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

        return await self._yadisk.get_upload_link(str(path), **kwargs)

    async def get_upload_link_object(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        **kwargs
    ) -> "ResourceUploadLinkObject":
        """
            Get a link to upload the file using the PUT request.
            This is similar to :any:`AsyncClient.get_upload_link()`, except it returns
            an instance of :any:`ResourceUploadLinkObject` which also contains
            an asynchronous operation ID.

            :param relative_path: `str` or `None`, relative path to the resource
            :param overwrite: `bool`, determines whether to overwrite the destination
            :param fields: list of keys to be included in the response
            :param spoof_user_agent: `bool`, if `True` (default), the `User-Agent` header
                will be set to a special value, which should allow bypassing of
                Yandex.Disk's upload speed limit
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises InsufficientStorageError: cannot upload file due to lack of storage space
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded

            :returns: :any:`ResourceUploadLinkObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.get_upload_link_object(str(path), **kwargs)

    async def upload(
        self: ResourceProtocol,
        path_or_file: AsyncFileOrPath,
        relative_path: Optional[str] = None,
        /,
        **kwargs
    ) -> "AsyncResourceLinkObject":
        """
            Upload a file to disk.

            :param path_or_file: path or file-like object to be uploaded
            :param relative_path: `str` or `None`, destination path relative to the resource
            :param overwrite: if `True`, the resource will be overwritten if it already exists,
                              an error will be raised otherwise
            :param spoof_user_agent: `bool`, if `True` (default), the `User-Agent` header
                will be set to a special value, which should allow bypassing of
                Yandex.Disk's upload speed limit
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises InsufficientStorageError: cannot upload file due to lack of storage space
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded

            :returns: :any:`AsyncResourceLinkObject`, link to the destination resource
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        dst_path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.upload(path_or_file, str(dst_path), **kwargs)

    async def upload_url(self: ResourceProtocol,
                         url: str,
                         relative_path: Optional[str] = None, /, **kwargs) -> "AsyncOperationLinkObject":
        """
            Upload a file from URL.

            :param url: source URL
            :param relative_path: `str` or `None`, destination path relative to the resource
            :param disable_redirects: `bool`, forbid redirects
            :param fields: list of keys to be included in the response
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises PathExistsError: destination path already exists
            :raises InsufficientStorageError: cannot upload file due to lack of storage space
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            :returns: :any:`AsyncOperationLinkObject`, link to the asynchronous operation
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        dst_path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.upload_url(url, str(dst_path), **kwargs)

    async def get_download_link(self: ResourceProtocol,
                                relative_path: Optional[str] = None, /, **kwargs) -> str:
        """
            Get a download link for a file (or a directory).

            :param relative_path: `str` or `None`, path relative to the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

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

        return await self._yadisk.get_download_link(str(path), **kwargs)

    @overload
    async def download(
        self: ResourceProtocol,
        dst_path_or_file: AsyncFileOrPathDestination,
        /,
        **kwargs
    ) -> "AsyncResourceLinkObject":
        pass

    @overload
    async def download(
        self: ResourceProtocol,
        relative_path: Optional[str],
        dst_path_or_file: AsyncFileOrPathDestination,
        /,
        **kwargs
    ) -> "AsyncResourceLinkObject":
        pass

    async def download(self: ResourceProtocol, /, *args, **kwargs) -> "AsyncResourceLinkObject":
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
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`AsyncResourceLinkObject`, link to the source resource
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
            await self._yadisk.download_by_link(self.file, dst_path_or_file, **kwargs)

            return AsyncResourceLinkObject.from_path(self.path, yadisk=self._yadisk)

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        src_path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.download(str(src_path), dst_path_or_file, **kwargs)

    @overload
    async def patch(self: ResourceProtocol, properties: Dict, **kwargs) -> "AsyncResourceObject":
        pass

    @overload
    async def patch(
        self: ResourceProtocol,
        relative_path: Union[str, None],
        properties: Dict, **kwargs
    ) -> "AsyncResourceObject":
        pass

    async def patch(self: ResourceProtocol, *args, **kwargs) -> "AsyncResourceObject":
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
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`AsyncResourceObject`
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

        return await self._yadisk.patch(str(path), properties, **kwargs)

    async def publish(self: ResourceProtocol,
                      relative_path: Optional[str] = None, /, **kwargs) -> "AsyncResourceLinkObject":
        """
            Make a resource public.

            :param relative_path: `str` or `None`, relative path to the resource to be published
            :param allow_address_access: `bool`, specifies the request format, i.e.
                with personal access settings (when set to `True`) or without
            :param public_settings: :any:`PublicSettings`, public access settings for the resource
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`AsyncResourceLinkObject`, link to the resource
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.publish(str(path), **kwargs)

    async def unpublish(self: ResourceProtocol,
                        relative_path: Optional[str] = None, /, **kwargs) -> "AsyncResourceLinkObject":
        """
            Make a public resource private.

            :param relative_path: `str` or `None`, relative path to the resource to be unpublished
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

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

        return await self._yadisk.unpublish(str(path), **kwargs)

    async def get_public_settings(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        **kwargs
    ) -> "PublicSettingsObject":
        """
            Get public settings of a resource.

            :param relative_path: `str` or `None`, relative path to the resource to be published
            :param allow_address_access: `bool`, specifies the request format, i.e.
                with personal access settings (when set to `True`) or without
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`PublicSettingsObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.get_public_settings(str(path), **kwargs)

    async def get_public_available_settings(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        **kwargs
    ) -> "PublicSettingsObject":
        """
            Get public settings of a shared resource for the current OAuth token owner.

            :param relative_path: `str` or `None`, relative path to the resource to be published
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`PublicAvailableSettingsObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.get_public_available_settings(str(path), **kwargs)

    async def update_public_settings(
        self: ResourceProtocol,
        *args,
        **kwargs
    ) -> "PublicSettingsObject":
        """
            Get public settings of a shared resource for the current OAuth token owner.
            This method takes 1 or 2 positional arguments:
            1. :code:`update_public_settings(public_settings, /, **kwargs)`
            2. :code:`update_public_settings(relative_path, public_settings, /, **kwargs)`

            :param relative_path: `str` or `None`, relative path to the resource to be published
            :param public_settings: :any:`PublicSettings`, public access settings for the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`PublicAvailableSettingsObject`
        """

        if len(args) == 1:
            relative_path, public_settings = None, args[0]
        elif len(args) == 2:
            relative_path, public_settings = args
        else:
            raise TypeError("update_public_settings() takes 1 or 2 positional arguments")

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.update_public_settings(str(path), public_settings, **kwargs)

    async def mkdir(self: ResourceProtocol,
                    relative_path: Optional[str] = None, /, **kwargs) -> "AsyncResourceLinkObject":
        """
            Create a new directory.

            :param relative_path: `str` or `None`, relative path to the directory to be created
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ParentNotFoundError: parent directory doesn't exist
            :raises DirectoryExistsError: destination path already exists
            :raises InsufficientStorageError: cannot create directory due to lack of storage space
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`AsyncResourceLinkObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.mkdir(str(path), **kwargs)

    async def makedirs(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        **kwargs
    ) -> "AsyncResourceLinkObject":
        """
            Create a new directory at `path`. If its parent directory doesn't
            exist it will also be created recursively.

            :param relative_path: `str` or `None`, relative path to the directory to be created
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises DirectoryExistsError: destination path already exists
            :raises InsufficientStorageError: cannot create directory due to lack of storage space
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request

            :returns: :any:`AsyncSyncResourceLinkObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.makedirs(str(path), **kwargs)

    async def remove(self: ResourceProtocol,
                     relative_path: Optional[str] = None, /, **kwargs) -> Optional["AsyncOperationLinkObject"]:
        """
            Remove the resource.

            :param relative_path: `str` or `None`, relative path to the resource to be removed
            :param permanently: if `True`, the resource will be removed permanently,
                                otherwise, it will be just moved to the trash
            :param md5: `str`, MD5 hash of the file to remove
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises BadRequestError: MD5 check is only available for files
            :raises ResourceIsLockedError: resource is locked by another request
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            :returns: :any:`AsyncOperationLinkObject` if the operation is performed asynchronously, `None` otherwise
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.remove(str(path), **kwargs)

    @overload
    async def move(self: ResourceProtocol,
                   dst_path: str, /, **kwargs) -> Union["AsyncResourceLinkObject", "AsyncOperationLinkObject"]:
        pass

    @overload
    async def move(self: ResourceProtocol,
                   relative_path: Optional[str],
                   dst_path: str, /, **kwargs) -> Union["AsyncResourceLinkObject", "AsyncOperationLinkObject"]:
        pass

    async def move(
        self: ResourceProtocol,
        /,
        *args,
        **kwargs
    ) -> Union["AsyncResourceLinkObject", "AsyncOperationLinkObject"]:
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
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            :returns: :any:`AsyncResourceLinkObject` or :any:`AsyncOperationLinkObject`
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

        return await self._yadisk.move(str(src_path), dst_path, **kwargs)

    @overload
    async def rename(self: ResourceProtocol,
                     new_name: str, /, **kwargs) -> Union["AsyncResourceLinkObject", "AsyncOperationLinkObject"]:
        pass

    @overload
    async def rename(self: ResourceProtocol,
                     relative_path: Optional[str],
                     new_name: str, /, **kwargs) -> Union["AsyncResourceLinkObject", "AsyncOperationLinkObject"]:
        pass

    async def rename(
        self: ResourceProtocol,
        /,
        *args,
        **kwargs
    ) -> Union["AsyncResourceLinkObject", "AsyncOperationLinkObject"]:
        """
            Rename `src_path` to have filename `new_name`.
            Does the same as `move()` but changes only the filename.

            :param relative_path: `str` or `None`, source path to be renamed relative to the resource
            :param new_name: target filename to rename to
            :param overwrite: `bool`, determines whether to overwrite the destination
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises ValueError: `new_name` is not a valid filename
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            :returns: :any:`AsyncResourceLinkObject` or :any:`AsyncOperationLinkObject`
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

        return await self._yadisk.rename(str(path), new_name, **kwargs)

    @overload
    async def copy(self: ResourceProtocol,
                   dst_path: str, /, **kwargs) -> Union["AsyncResourceLinkObject", "AsyncOperationLinkObject"]:
        pass

    @overload
    async def copy(self: ResourceProtocol,
                   relative_path: Optional[str],
                   dst_path: str, /, **kwargs) -> Union["AsyncResourceLinkObject", "AsyncOperationLinkObject"]:
        pass

    async def copy(
        self: ResourceProtocol,
        /,
        *args,
        **kwargs
    ) -> Union["AsyncResourceLinkObject", "AsyncOperationLinkObject"]:
        """
            Copy resource to `dst_path`.
            If the operation is performed asynchronously, returns the link to the operation,
            otherwise, returns the link to the newly created resource.

            This method takes 1 or 2 positional arguments:

            1. :code:`copy(dst_path, /, **kwargs)`
            2. :code:`copy(relative_path, dst_path, /, **kwargs)`

            :param relative_path: `str` or `None`, source path relative to the resource
            :param dst_path: destination path
            :param overwrite: if `True` the destination path can be overwritten,
                              otherwise, an error will be raised
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises InsufficientStorageError: cannot complete request due to lack of storage space
            :raises ResourceIsLockedError: resource is locked by another request
            :raises UploadTrafficLimitExceededError: upload limit has been exceeded
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            :returns: :any:`AsyncResourceLinkObject` or :any:`AsyncOperationLinkObject`
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

        return await self._yadisk.copy(str(src_path), dst_path, **kwargs)


def _convert_list_of_previews(previews: JSON) -> Optional[Dict[str, str]]:
    if previews is None:
        return None

    if not isinstance(previews, list):
        raise ValueError(f"Expected a list, got {type(previews)}")

    result = {}

    for preview in previews:
        if not isinstance(preview, dict):
            raise ValueError(f"Expected a dict, got {type(preview)}")

        try:
            name = preview["name"]
            url = preview["url"]
        except KeyError:
            continue

        if not isinstance(name, str):
            raise ValueError(f"Expected a string, got {type(name)}")

        if not isinstance(url, str):
            raise ValueError(f"Expected a string, got {type(url)}")

        result[name] = url

    return result


class ResourceObject(YaDiskObject):
    """
        Resource object.

        :param resource: `dict` or `None`
        :param yadisk: :any:`Client`/:any:`AsyncClient` or `None`, `YaDisk` object

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
        :ivar sizes: `dict[str, str]`, mapping of all preview sizes,
                     where keys are names and values are download links

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
    custom_properties: Optional[Dict]
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
    sizes: Optional[Dict[str, str]]

    def __init__(self, resource: Optional[Dict] = None, yadisk: Optional[Any] = None):
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
             "revision":          int_or_error,
             "sizes":             _convert_list_of_previews
            },
            yadisk)
        self.set_alias("_embedded", "embedded")
        self.import_fields(resource)


class SyncResourceObject(ResourceObject, ResourceObjectMethodsMixin):
    """
        Resource object.

        :param resource: `dict` or `None`
        :param yadisk: :any:`Client` or `None`, `YaDisk` object

        :ivar antivirus_status: `str`, antivirus check status
        :ivar file: `str`, download URL
        :ivar size: `int`, file size
        :ivar public_key: `str`, public resource key
        :ivar sha256: `str`, SHA256 hash
        :ivar md5: `str`, MD5 hash
        :ivar embedded: :any:`SyncResourceListObject`, list of nested resources
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
        :ivar sizes: `dict[str, str]`, mapping of all preview sizes,
                     where keys are names and values are download links
    """

    embedded: Optional["SyncResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]
    _embedded: Optional["SyncResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(self, resource: Optional[Dict] = None, yadisk: Optional[Any] = None):
        ResourceObject.__init__(self, None, yadisk)
        self.set_field_type("embedded", partial(SyncResourceListObject, yadisk=yadisk))
        self.import_fields(resource)


class AsyncResourceObject(ResourceObject, AsyncResourceObjectMethodsMixin):
    """
        Resource object.

        :param resource: `dict` or `None`
        :param yadisk: :any:`AsyncClient` or `None`, `YaDisk` object

        :ivar antivirus_status: `str`, antivirus check status
        :ivar file: `str`, download URL
        :ivar size: `int`, file size
        :ivar public_key: `str`, public resource key
        :ivar sha256: `str`, SHA256 hash
        :ivar md5: `str`, MD5 hash
        :ivar embedded: :any:`AsyncResourceListObject`, list of nested resources
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
        :ivar sizes: `dict[str, str]`, mapping of all preview sizes,
                     where keys are names and values are download links
    """

    embedded: Optional["AsyncResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]
    _embedded: Optional["AsyncResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(self, resource: Optional[Dict] = None, yadisk: Optional[Any] = None):
        ResourceObject.__init__(self, None, yadisk)
        self.set_field_type("embedded", partial(AsyncResourceListObject, yadisk=yadisk))
        self.import_fields(resource)


class ResourceLinkObject(LinkObject):
    """
        Resource link object.

        :param link: `dict` or `None`
        :param yadisk: :any:`Client`/:any:`AsyncClient` or `None`, `YaDisk` object

        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
        :ivar path: `str`, path to the resource
    """

    type: Optional[str]
    public_key: Optional[str]
    public_url: Optional[str]
    file: Optional[str]

    path: Optional[str]

    def __init__(self, link: Optional[Dict] = None, yadisk: Optional[Any] = None):
        LinkObject.__init__(self, None, yadisk)

        self.set_field_type("path", str_or_error)
        self.set_field_type("public_key", str_or_error)
        self.set_field_type("public_url", str_or_error)
        self.set_field_type("type", str_or_error)
        self.set_field_type("file", str_or_error)

        self.import_fields(link)

        if self.href is not None and is_resource_link(self.href):
            try:
                self.path = ensure_path_has_schema(
                    parse_qs(urlparse(self.href).query).get("path", [])[0])
            except IndexError:
                pass

    @classmethod
    def from_path(cls, path: Optional[str], yadisk: Optional[Any] = None):
        if path is None:
            return cls(yadisk=yadisk)

        path = ensure_path_has_schema(path)

        return cls(
            {"method": "GET",
             "href": f"{settings.BASE_API_URL}/v1/disk/resources?{urlencode({'path': path})}",
             "templated": False},
            yadisk=yadisk)


class SyncResourceLinkObject(ResourceLinkObject, ResourceObjectMethodsMixin):
    """
        Resource link object.

        :param link: `dict` or `None`
        :param yadisk: :any:`Client` or `None`, `YaDisk` object

        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
        :ivar path: `str`, path to the resource
    """

    pass


class AsyncResourceLinkObject(ResourceLinkObject, AsyncResourceObjectMethodsMixin):
    """
        Resource link object.

        :param link: `dict` or `None`
        :param yadisk: :any:`AsyncClient` or `None`, `YaDisk` object

        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
        :ivar path: `str`, path to the resource
    """

    pass


class PublicResourceLinkObject(LinkObject):
    """
        Public resource link object.

        :param link: `dict` or `None`
        :param yadisk: :any:`Client`/:any:`AsyncClient` or `None`, `YaDisk` object

        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
        :ivar public_key: `str`, public key of the resource
        :ivar public_url: `str`, public URL of the resource
    """

    type: Optional[str]
    file: Optional[str]

    path: Optional[str]
    public_key: Optional[str]
    public_url: Optional[str]

    def __init__(self, link: Optional[Dict] = None, yadisk: Optional[Any] = None):
        LinkObject.__init__(self, None, yadisk)
        self.set_field_type("public_key", str_or_error)
        self.set_field_type("public_url", str_or_error)
        self.set_field_type("path", str_or_error)

        self.import_fields(link)

        if self.href is not None and is_public_resource_link(self.href):
            try:
                public_key_or_url = parse_qs(urlparse(self.href).query).get("public_key", [])[0]
            except IndexError:
                public_key_or_url = ""

            if public_key_or_url.startswith(("http://", "https://")):
                self.public_url = public_key_or_url
            else:
                self.public_key = public_key_or_url

    @classmethod
    def from_public_key(cls, public_key: Optional[str], yadisk: Optional[Any] = None):
        if public_key is None:
            return cls(yadisk=yadisk)

        return cls(
            {"method": "GET",
             "href": f"{settings.BASE_API_URL}/v1/disk/public/resources?{urlencode({'public_key': public_key})}",
             "templated": False},
            yadisk=yadisk)


class SyncPublicResourceLinkObject(PublicResourceLinkObject, ResourceObjectMethodsMixin):
    """
        Public resource link object.

        :param link: `dict` or `None`
        :param yadisk: :any:`Client` or `None`, `YaDisk` object

        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
        :ivar public_key: `str`, public key of the resource
        :ivar public_url: `str`, public URL of the resource
    """

    pass


class AsyncPublicResourceLinkObject(PublicResourceLinkObject, AsyncResourceObjectMethodsMixin):
    """
        Public resource link object.

        :param link: `dict` or `None`
        :param yadisk: :any:`AsyncClient` or `None`, `YaDisk` object

        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
        :ivar public_key: `str`, public key of the resource
        :ivar public_url: `str`, public URL of the resource
    """

    pass


class ResourceListObject(YaDiskObject):
    """
        List of resources.

        :param resource_list: `dict` or `None`
        :param yadisk: :any:`Client`/:any:`AsyncClient` or `None`, `YaDisk` object

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

    def __init__(self, resource_list: Optional[Dict] = None, yadisk: Optional[Any] = None):
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


class SyncResourceListObject(ResourceListObject):
    """
        List of resources.

        :param resource_list: `dict` or `None`
        :param yadisk: :any:`Client` or `None`, `YaDisk` object

        :ivar sort: `str`, sort type
        :ivar items: `list`, list of resources (:any:`SyncResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
        :ivar path: `str`, path to the directory that contains the elements of the list
        :ivar total: `int`, number of elements in the list
    """

    items: Optional[List[SyncResourceObject]]  # type: ignore[assignment]

    def __init__(self, resource_list: Optional[Dict] = None, yadisk: Optional[Any] = None):
        ResourceListObject.__init__(self, None, yadisk)
        self.set_field_type("items", typed_list(partial(SyncResourceObject, yadisk=yadisk)))
        self.import_fields(resource_list)


class AsyncResourceListObject(ResourceListObject):
    """
        List of resources.

        :param resource_list: `dict` or `None`
        :param yadisk: :any:`AsyncClient` or `None`, `YaDisk` object

        :ivar sort: `str`, sort type
        :ivar items: `list`, list of resources (:any:`AsyncResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
        :ivar path: `str`, path to the directory that contains the elements of the list
        :ivar total: `int`, number of elements in the list
    """

    items: Optional[List[AsyncResourceObject]]  # type: ignore[assignment]

    def __init__(self, resource_list: Optional[Dict] = None, yadisk: Optional[Any] = None):
        ResourceListObject.__init__(self, None, yadisk)
        self.set_field_type("items", typed_list(partial(AsyncResourceObject, yadisk=yadisk)))
        self.import_fields(resource_list)


class ResourceUploadLinkObject(LinkObject):
    """
        Resource upload link.

        :param resource_upload_link: `dict` or `None`
        :param yadisk: :any:`Client`/:any:`AsyncClient` or `None`, `YaDisk` object

        :ivar operation_id: `str`, ID of the upload operation
        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
    """

    operation_id: Optional[str]

    def __init__(self,
                 resource_upload_link: Optional[Dict] = None,
                 yadisk: Optional[Any] = None):
        LinkObject.__init__(self, None, yadisk)
        self.set_field_type("operation_id", str_or_error)
        self.import_fields(resource_upload_link)


class ResourceDownloadLinkObject(LinkObject):
    """
        Resource download link.

        :param link: `dict` or `None`
        :param yadisk: :any:`Client`/:any:`AsyncClient` or `None`, `YaDisk` object

        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
    """

    pass


class ShareInfoObject(YaDiskObject):
    """
        Shared folder information object.

        :param share_info: `dict` or `None`
        :param yadisk: :any:`Client`/:any:`AsyncClient` or `None`, `YaDisk` object

        :ivar is_root: `bool`, tells whether the folder is root
        :ivar is_owned: `bool`, tells whether the user is the owner of this directory
        :ivar rights: `str`, access rights
    """

    is_root: Optional[bool]
    is_owned: Optional[bool]
    rights: Optional[str]

    def __init__(self, share_info: Optional[Dict] = None, yadisk: Optional[Any] = None):
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
        :param yadisk: :any:`Client`/:any:`AsyncClient` or `None`, `YaDisk` object

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
    embedded: Optional["PublicResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]
    _embedded: Optional["PublicResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]
    owner: Optional[UserPublicInfoObject]

    def __init__(self, public_resource=None, yadisk=None):
        ResourceObject.__init__(self, None, yadisk)
        self.set_field_type("views_count", int_or_error)
        self.set_alias("view_count", "views_count")
        self.set_field_type("embedded", partial(PublicResourceListObject, yadisk=yadisk))
        self.set_field_type("owner", partial(UserPublicInfoObject, yadisk=yadisk))
        self.import_fields(public_resource)


class SyncPublicResourceObject(PublicResourceObject, ResourceObjectMethodsMixin):
    """
        Public resource object.

        :param resource: `dict` or `None`
        :param yadisk: :any:`Client` or `None`, `YaDisk` object

        :ivar antivirus_status: `str`, antivirus check status
        :ivar file: `str`, download URL
        :ivar size: `int`, file size
        :ivar public_key: `str`, public resource key
        :ivar sha256: `str`, SHA256 hash
        :ivar md5: `str`, MD5 hash
        :ivar embedded: :any:`SyncPublicResourceObject`, list of nested resources
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

    embedded: Optional["SyncPublicResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]
    _embedded: Optional["SyncPublicResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(self, public_resource: Optional[Dict] = None, yadisk: Optional[Any] = None):
        PublicResourceObject.__init__(self, None, yadisk)
        self.set_field_type("embedded", partial(SyncPublicResourceListObject, yadisk=yadisk))
        self.import_fields(public_resource)


class AsyncPublicResourceObject(PublicResourceObject, AsyncResourceObjectMethodsMixin):
    """
        Public resource object.

        :param resource: `dict` or `None`
        :param yadisk: :any:`AsyncClient` or `None`, `YaDisk` object

        :ivar antivirus_status: `str`, antivirus check status
        :ivar file: `str`, download URL
        :ivar size: `int`, file size
        :ivar public_key: `str`, public resource key
        :ivar sha256: `str`, SHA256 hash
        :ivar md5: `str`, MD5 hash
        :ivar embedded: :any:`AsyncPublicResourceObject`, list of nested resources
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

    embedded: Optional["AsyncPublicResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]
    _embedded: Optional["AsyncPublicResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(self, public_resource: Optional[Dict] = None, yadisk: Optional[Any] = None):
        PublicResourceObject.__init__(self, None, yadisk)
        self.set_field_type("embedded", partial(AsyncPublicResourceListObject, yadisk=yadisk))
        self.import_fields(public_resource)


class PublicResourceListObject(ResourceListObject):
    """
        List of public resources.

        :param public_resource_list: `dict` or `None`
        :param yadisk: :any:`Client`/:any:`AsyncClient` or `None`, `YaDisk` object

        :ivar sort: `str`, sort type
        :ivar items: `list`, list of resources (:any:`ResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
        :ivar path: `str`, path to the directory that contains the elements of the list
        :ivar total: `int`, number of elements in the list
        :ivar public_key: `str`, public key of the resource
    """

    public_key: Optional[str]
    items: Optional[List[PublicResourceObject]]  # type: ignore[assignment]

    def __init__(self,
                 public_resource_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None):
        ResourceListObject.__init__(self, None, yadisk)
        self.set_field_type("public_key", str_or_error)
        self.set_field_type("items", typed_list(partial(PublicResourceObject, yadisk=yadisk)))
        self.import_fields(public_resource_list)


class SyncPublicResourceListObject(PublicResourceListObject):
    """
        List of public resources.

        :param public_resource_list: `dict` or `None`
        :param yadisk: :any:`Client` or `None`, `YaDisk` object

        :ivar sort: `str`, sort type
        :ivar items: `list`, list of resources (:any:`SyncResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
        :ivar path: `str`, path to the directory that contains the elements of the list
        :ivar total: `int`, number of elements in the list
        :ivar public_key: `str`, public key of the resource
    """

    items: Optional[List[SyncPublicResourceObject]]  # type: ignore[assignment]

    def __init__(self, public_resource_list: Optional[Dict] = None, yadisk: Optional[Any] = None):
        PublicResourceListObject.__init__(self, None, yadisk)
        self.set_field_type("items", typed_list(partial(SyncPublicResourceObject, yadisk=yadisk)))
        self.import_fields(public_resource_list)


class AsyncPublicResourceListObject(PublicResourceListObject):
    """
        List of public resources.

        :param public_resource_list: `dict` or `None`
        :param yadisk: :any:`AsyncClient` or `None`, `YaDisk` object

        :ivar sort: `str`, sort type
        :ivar items: `list`, list of resources (:any:`AsyncResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
        :ivar path: `str`, path to the directory that contains the elements of the list
        :ivar total: `int`, number of elements in the list
        :ivar public_key: `str`, public key of the resource
    """

    items: Optional[List[AsyncPublicResourceObject]]  # type: ignore[assignment]

    def __init__(self, public_resource_list: Optional[Dict] = None, yadisk: Optional[Any] = None):
        PublicResourceListObject.__init__(self, None, yadisk)
        self.set_field_type("items", typed_list(partial(AsyncPublicResourceObject, yadisk=yadisk)))
        self.import_fields(public_resource_list)


class TrashResourceObject(ResourceObject):
    """
        Trash resource object.

        :param trash_resource: `dict` or `None`
        :param yadisk: :any:`Client`/:any:`AsyncClient` or `None`, `YaDisk` object

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
        :ivar sizes: `dict[str, str]`, mapping of all preview sizes,
                     where keys are names and values are download links
    """

    embedded: Optional["TrashResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]
    _embedded: Optional["TrashResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]
    origin_path: Optional[str]
    deleted: Optional["datetime.datetime"]

    def __init__(self,
                 trash_resource: Optional[Dict] = None,
                 yadisk: Optional[Any] = None):
        ResourceObject.__init__(self, None, yadisk)
        self.set_field_type("embedded", partial(TrashResourceListObject, yadisk=yadisk))
        self.set_field_type("origin_path", str_or_error)
        self.set_field_type("deleted", yandex_date)
        self.import_fields(trash_resource)


class SyncTrashResourceObject(TrashResourceObject):
    """
        Trash resource object.

        :param trash_resource: `dict` or `None`
        :param yadisk: :any:`Client` or `None`, `YaDisk` object

        :ivar antivirus_status: `str`, antivirus check status
        :ivar file: `str`, download URL
        :ivar size: `int`, file size
        :ivar public_key: `str`, public resource key
        :ivar sha256: `str`, SHA256 hash
        :ivar md5: `str`, MD5 hash
        :ivar embedded: :any:`SyncTrashResourceListObject`, list of nested resources
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
        :ivar sizes: `dict[str, str]`, mapping of all preview sizes,
                     where keys are names and values are download links
    """

    embedded: Optional["SyncTrashResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]
    _embedded: Optional["SyncTrashResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(self,
                 trash_resource: Optional[Dict] = None,
                 yadisk: Optional[Any] = None):
        TrashResourceObject.__init__(self, None, yadisk)
        self.set_field_type("embedded", partial(SyncTrashResourceListObject, yadisk=yadisk))
        self.import_fields(trash_resource)

    def get_meta(self: ResourceProtocol,
                 relative_path: Optional[str] = None, /, **kwargs) -> "SyncTrashResourceObject":
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
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: :any:`SyncTrashResourceObject`
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
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

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
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

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
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

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
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a file, `False` otherwise (even if it doesn't exist)
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("TrashResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.is_trash_file(str(path), **kwargs)

    def listdir(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        **kwargs
    ) -> Generator["SyncTrashResourceObject", None, None]:
        """
            Get contents of a trash resource.

            :param relative_path: `str` or `None`, relative path to the directory in the trash bin
            :param max_items: `int` or `None`, maximum number of returned items (`None` means unlimited)
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises WrongResourceTypeError: resource is not a directory

            :returns: generator of :any:`SyncTrashResourceObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("TrashResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.trash_listdir(str(path), **kwargs)

    def remove(self: ResourceProtocol,
               relative_path: Optional[str] = None, /, **kwargs) -> Optional["SyncOperationLinkObject"]:
        """
            Remove a trash resource.

            :param relative_path: `str` or `None`, relative path to the trash resource to be deleted
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            :returns: :any:`SyncOperationLinkObject` if the operation is performed asynchronously, `None` otherwise
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("TrashResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return self._yadisk.remove_trash(str(path), **kwargs)

    @overload
    def restore(self: ResourceProtocol,
                dst_path: str, /, **kwargs) -> Union[SyncResourceLinkObject, "SyncOperationLinkObject"]:
        pass

    @overload
    def restore(self: ResourceProtocol,
                relative_path: Optional[str],
                dst_path: str, /, **kwargs) -> Union[SyncResourceLinkObject, "SyncOperationLinkObject"]:
        pass

    def restore(self: ResourceProtocol, /, *args, **kwargs) -> Union[SyncResourceLinkObject, "SyncOperationLinkObject"]:
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
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param requests_args: `dict`, additional parameters for :any:`RequestsSession`
            :param httpx_args: `dict`, additional parameters for :any:`HTTPXSession`
            :param curl_options: `dict`, additional options for :any:`PycURLSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            :returns: :any:`SyncResourceLinkObject` or :any:`SyncOperationLinkObject`
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


class AsyncTrashResourceObject(TrashResourceObject):
    """
        Trash resource object.

        :param trash_resource: `dict` or `None`
        :param yadisk: :any:`AsyncClient` or `None`, `YaDisk` object

        :ivar antivirus_status: `str`, antivirus check status
        :ivar file: `str`, download URL
        :ivar size: `int`, file size
        :ivar public_key: `str`, public resource key
        :ivar sha256: `str`, SHA256 hash
        :ivar md5: `str`, MD5 hash
        :ivar embedded: :any:`AsyncTrashResourceListObject`, list of nested resources
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
        :ivar sizes: `dict[str, str]`, mapping of all preview sizes, where
                     keys are names and values are download links
    """

    embedded: Optional["AsyncTrashResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]
    _embedded: Optional["AsyncTrashResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(self,
                 trash_resource: Optional[Dict] = None,
                 yadisk: Optional[Any] = None):
        TrashResourceObject.__init__(self, None, yadisk)
        self.set_field_type("embedded", partial(AsyncTrashResourceListObject, yadisk=yadisk))
        self.import_fields(trash_resource)

    async def get_meta(self: ResourceProtocol,
                       relative_path: Optional[str] = None, /, **kwargs) -> "AsyncTrashResourceObject":
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
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: :any:`AsyncTrashResourceObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("ResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.get_trash_meta(str(path), **kwargs)

    async def exists(self: ResourceProtocol,
                     relative_path: Optional[str] = None, /, **kwargs) -> bool:
        """
            Check whether the trash resource exists.

            :param relative_path: `str` or `None`, relative path to the trash resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `bool`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("TrashResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.trash_exists(str(path), **kwargs)

    async def get_type(self: ResourceProtocol,
                       relative_path: Optional[str] = None, /, **kwargs) -> str:
        """
            Get trash resource type.

            :param relative_path: `str` or `None`, relative path to the trash resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: "file" or "dir"
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("TrashResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.get_trash_type(str(path), **kwargs)

    async def is_dir(self: ResourceProtocol,
                     relative_path: Optional[str] = None, /, **kwargs) -> bool:
        """
            Check whether resource is a trash directory.

            :param relative_path: `str` or `None`, relative path to the trash resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("TrashResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.is_trash_dir(str(path), **kwargs)

    async def is_file(self: ResourceProtocol,
                      relative_path: Optional[str] = None, /, **kwargs) -> bool:
        """
            Check whether resource is a trash file.

            :param relative_path: `str` or `None`, relative path to the trash resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises ForbiddenError: application doesn't have enough rights for this request

            :returns: `True` if `path` is a file, `False` otherwise (even if it doesn't exist)
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("TrashResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.is_trash_file(str(path), **kwargs)

    async def listdir(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        **kwargs
    ) -> AsyncGenerator["AsyncTrashResourceObject", None]:
        """
            Get contents of a trash resource.

            :param relative_path: `str` or `None`, relative path to the directory in the trash bin
            :param max_items: `int` or `None`, maximum number of returned items (`None` means unlimited)
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises WrongResourceTypeError: resource is not a directory

            :returns: generator of :any:`AsyncTrashResourceObject`
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("TrashResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        async for i in self._yadisk.trash_listdir(str(path), **kwargs):
            yield i

    async def remove(self: ResourceProtocol,
                     relative_path: Optional[str] = None, /, **kwargs) -> Optional["AsyncOperationLinkObject"]:
        """
            Remove a trash resource.

            :param relative_path: `str` or `None`, relative path to the trash resource to be deleted
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            :returns: :any:`AsyncOperationLinkObject` if the operation is performed asynchronously, `None` otherwise
        """

        if self._yadisk is None:
            raise ValueError("This object is not bound to a YaDisk instance")

        if self.path is None:
            raise ValueError("TrashResourceObject doesn't have a path")

        path = PurePosixPath(self.path) / (relative_path or "")

        return await self._yadisk.remove_trash(str(path), **kwargs)

    @overload
    async def restore(self: ResourceProtocol,
                      dst_path: str, /, **kwargs) -> Union[AsyncResourceLinkObject, "AsyncOperationLinkObject"]:
        pass

    @overload
    async def restore(self: ResourceProtocol,
                      relative_path: Optional[str],
                      dst_path: str, /, **kwargs) -> Union[AsyncResourceLinkObject, "AsyncOperationLinkObject"]:
        pass

    async def restore(
        self: ResourceProtocol,
        /,
        *args,
        **kwargs
    ) -> Union[AsyncResourceLinkObject, "AsyncOperationLinkObject"]:
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
            :param wait: `bool`, if :code:`True`, the method will wait until the asynchronous operation is completed
            :param poll_interval: `float`, interval in seconds between subsequent operation status queries
            :param poll_timeout: `float` or `None`, total polling timeout (`None` means no timeout),
                                 if this timeout is exceeded, an exception is raised
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
            :param retry_on: `tuple`, additional exception classes to retry on
            :param aiohttp_args: `dict`, additional parameters for :any:`AIOHTTPSession`
            :param httpx_args: `dict`, additional parameters for :any:`AsyncHTTPXSession`
            :param kwargs: any other parameters, accepted by :any:`Session.send_request()`

            :raises PathNotFoundError: resource was not found on Disk
            :raises PathExistsError: destination path already exists
            :raises ForbiddenError: application doesn't have enough rights for this request
            :raises ResourceIsLockedError: resource is locked by another request
            :raises OperationNotFoundError: requested operation was not found
            :raises AsyncOperationFailedError: requested operation failed
            :raises AsyncOperationPollingTimeoutError: requested operation did not
                                                       complete in specified time
                                                       (when `poll_timeout` is not `None`)

            :returns: :any:`AsyncResourceLinkObject` or :any:`AsyncOperationLinkObject`
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

        return await self._yadisk.restore_trash(str(path), dst_path, **kwargs)


class TrashResourceListObject(ResourceListObject):
    """
        List of trash resources.

        :param trash_resource_list: `dict` or `None`
        :param yadisk: :any:`Client`/:any:`AsyncClient` or `None`, `YaDisk` object

        :ivar sort: `str`, sort type
        :ivar items: `list`, list of resources (:any:`TrashResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
        :ivar path: `str`, path to the directory that contains the elements of the list
        :ivar total: `int`, number of elements in the list
    """

    items: Optional[List[TrashResourceObject]]  # type: ignore[assignment]

    def __init__(self,
                 trash_resource_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None):
        ResourceListObject.__init__(self, None, yadisk)
        self.set_field_type("items", typed_list(partial(TrashResourceObject, yadisk=yadisk)))
        self.import_fields(trash_resource_list)


class SyncTrashResourceListObject(TrashResourceListObject):
    """
        List of trash resources.

        :param trash_resource_list: `dict` or `None`
        :param yadisk: :any:`Client` or `None`, `YaDisk` object

        :ivar sort: `str`, sort type
        :ivar items: `list`, list of resources (:any:`SyncTrashResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
        :ivar path: `str`, path to the directory that contains the elements of the list
        :ivar total: `int`, number of elements in the list
    """

    items: Optional[List[SyncTrashResourceObject]]  # type: ignore[assignment]

    def __init__(self,
                 trash_resource_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None):
        TrashResourceListObject.__init__(self, None, yadisk)
        self.set_field_type("items", typed_list(partial(SyncTrashResourceObject, yadisk=yadisk)))
        self.import_fields(trash_resource_list)


class AsyncTrashResourceListObject(TrashResourceListObject):
    """
        List of trash resources.

        :param trash_resource_list: `dict` or `None`
        :param yadisk: :any:`AsyncClient` or `None`, `YaDisk` object

        :ivar sort: `str`, sort type
        :ivar items: `list`, list of resources (:any:`AsyncTrashResourceObject`)
        :ivar limit: `int`, maximum number of elements in the list
        :ivar offset: `int`, offset from the beginning of the list
        :ivar path: `str`, path to the directory that contains the elements of the list
        :ivar total: `int`, number of elements in the list
    """

    items: Optional[List[AsyncTrashResourceObject]]  # type: ignore[assignment]

    def __init__(self,
                 trash_resource_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None):
        TrashResourceListObject.__init__(self, None, yadisk)
        self.set_field_type("items", typed_list(partial(AsyncTrashResourceObject, yadisk=yadisk)))
        self.import_fields(trash_resource_list)


class PublicSettingsObject(YaDiskObject):
    """
        Public settings of a shared resource.

        :ivar available_until: `int`, timestamp indicating the expiration date of the link
        :ivar read_only: `bool`, whether the resource is read-only
        :ivar available_until_verbose: :any:`AvailableUntilVerboseObject`, verbose information about the expiration date
        :ivar password: `str`, password to access the resource
        :ivar password_verbose: :any:`PasswordVerboseObject`, verbose information about the password
        :ivar external_organization_id: `str`, external organization ID
        :ivar external_organization_id_verbose: :any:`ExternalOrganizationIdVerboseObject`,
            verbose information about the external organization ID
        :ivar accesses: `List[PublicSettingsAccessObject]`, list of access settings
    """

    available_until: Optional[int]
    read_only: Optional[bool]
    available_until_verbose: Optional["AvailableUntilVerboseObject"]
    password: Optional[str]
    password_verbose: Optional["PasswordVerboseObject"]
    external_organization_id: Optional[str]
    external_organization_id_verbose: Optional["ExternalOrganizationIdVerboseObject"]
    accesses: Optional[List["PublicAccessObject"]]

    def __init__(
        self,
        public_settings: Optional[Dict] = None,
        yadisk: Optional[Any] = None
    ) -> None:
        YaDiskObject.__init__(
            self,
            {
                "available_until": int_or_error,
                 "read_only": bool_or_error,
                 "available_until_verbose": AvailableUntilVerboseObject,
                 "password": str_or_error,
                 "password_verbose": PasswordVerboseObject,
                 "external_organization_id": str_or_error,
                 "external_organization_id_verbose": ExternalOrganizationIdVerboseObject,
                 "accesses": typed_list(PublicAccessObject)
            },
            yadisk
        )
        self.import_fields(public_settings)


class AvailableUntilVerboseObject(YaDiskObject):
    """
        Verbose information about the expiration date of a shared resource.

        :ivar enabled: `bool`, whether the expiration date is enabled
        :ivar value: `int`, timestamp of the expiration date
    """

    enabled: Optional[bool]
    value: Optional[int]

    def __init__(
        self,
        available_until_verbose: Optional[Dict] = None,
        yadisk: Optional[Any] = None
    ) -> None:
        YaDiskObject.__init__(
            self,
            {
                "enabled": bool_or_error,
                "value": int_or_error
            },
            yadisk
        )
        self.import_fields(available_until_verbose)


class PasswordVerboseObject(YaDiskObject):
    """
        Verbose information about the password of shared resource.

        :ivar enabled: `bool`, whether the password is enabled
        :ivar value: `str`, password value
    """

    enabled: Optional[bool]
    value: Optional[str]

    def __init__(
        self,
        password_verbose: Optional[Dict] = None,
        yadisk: Optional[Any] = None
    ) -> None:
        YaDiskObject.__init__(
            self,
            {
                "enabled": bool_or_error,
                "value": str_or_error
            },
            yadisk
        )
        self.import_fields(password_verbose)


class ExternalOrganizationIdVerboseObject(YaDiskObject):
    """
        Verbose information about the external organization ID of a shared resource.

        :ivar enabled: `bool`, whether the external organization ID is enabled
        :ivar value: `str`, external organization ID
    """

    enabled: Optional[bool]
    value: Optional[str]

    def __init__(
        self,
        external_organization_id_verbose: Optional[Dict] = None,
        yadisk: Optional[Any] = None
    ) -> None:
        YaDiskObject.__init__(
            self,
            {
                "enabled": bool_or_error,
                "value": str_or_error
            },
            yadisk
        )
        self.import_fields(external_organization_id_verbose)


class PublicAccessObject(YaDiskObject):
    """
        Access settings of a shared resource.

        :ivar macros: `List[Union[Literal["employees"], Literal["all"]]],`,
            specifies who has access to the shared resource, must contain only
            one element
        :ivar type: `str`, specifies the type of access, must be one of the following:

        - `macro`: access for all employees or all users
        - `user`: access for a specific user
        - `group`: access for a specific group
        - `department`: access for a specific department

        :ivar org_id: `int`, organization ID
        :ivar id: `str`, user, group or department ID
        :ivar rights: `List[str]`, specifies the access rights

        Valid access rights:

        - `write`: write access
        - `read`: read access
        - `read_without_download`: read access without download
        - `read_with_password`: read access with password
        - `read_with_password_without_download`: read access with password and without download
    """

    macros: Optional[List[Union[Literal["all", "employees"], str]]]
    type: Optional[Union[Literal["macro", "user", "group", "department"], str]]
    org_id: Optional[int]
    id: Optional[str]
    rights: Optional[List[
        Union[
            Literal[
                "read",
                "write",
                "read_without_download",
                "read_with_password",
                "read_with_password_without_download"
            ],
            str
        ]
    ]]

    def __init__(
        self,
        public_access: Optional[Dict] = None,
        yadisk: Optional[Any] = None
    ) -> None:
        YaDiskObject.__init__(
            self,
            {
                "macros": typed_list(str_or_error),
                "type": str_or_error,
                "org_id": int_or_error,
                "id": str_or_error,
                "group_ids": typed_list(int_or_error),
                "department_ids": typed_list(int_or_error),
                "rights": typed_list(str_or_error)
            },
            yadisk
        )
        self.import_fields(public_access)


class PublicAvailableSettingsObject(YaDiskObject):
    """
        Public settings of a shared resource for the current OAuth token owner.

        :ivar permissions: `List[str]`, list of available permissions
        :ivar address_access_sharing: `str`, specifies who has access to the
            shared resource, must be one of the following:

            - `all`: access for all users
            - `inner`: access for all employees

        :ivar use_sharing: `bool`, whether the resource can be shared
        :ivar macro_sharing: `str`, specifies who has access to the shared
            resource, must be one of the following:

            - `all`: access for all users
            - `inner`: access for all employees

        :ivar default: `List[PublicDefault]`, default public settings
    """

    permissions: Optional[List[str]]
    address_access_sharing: Optional[Union[Literal["all", "inner"], str]]
    use_sharing: Optional[bool]
    macro_sharing: Optional[Union[Literal["all", "inner"], str]]
    default: Optional[List["PublicDefaultObject"]]

    def __init__(
        self,
        public_available_settings: Optional[Dict] = None,
        yadisk: Optional[Any] = None
    ) -> None:
        YaDiskObject.__init__(
            self,
            {
                "permissions": typed_list(str_or_error),
                "address_access_sharing": str_or_error,
                "use_sharing": bool_or_error,
                "macro_sharing": str_or_error,
                "default": typed_list(PublicDefaultObject)
            },
            yadisk
        )
        self.import_fields(public_available_settings)


class PublicDefaultObject(YaDiskObject):
    """
        Access settings of a shared resource.

        :ivar macros: `List[Union[Literal["employees"], Literal["all"]]],`,
            specifies who has access to the shared resource, must contain only
            one element
        :ivar org_id: `int`, organization ID
        :ivar rights: `List[str]`, specifies the access rights

        Valid access rights:

        - `write`: write access
        - `read`: read access
        - `read_without_download`: read access without download
        - `read_with_password`: read access with password
        - `read_with_password_without_download`: read access with password and without download
    """

    macros: Optional[List[str]]
    org_id: Optional[int]
    rights: Optional[List[str]]

    def __init__(
        self,
        public_default: Optional[Dict] = None,
        yadisk: Optional[Any] = None
    ) -> None:
        YaDiskObject.__init__(
            self,
            {
                "macros": typed_list(str_or_error),
                "org_id": int_or_error,
                "rights": typed_list(str_or_error)
            },
            yadisk
        )
        self.import_fields(public_default)
