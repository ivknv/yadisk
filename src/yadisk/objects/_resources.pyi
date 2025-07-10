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

from ._yadisk_object import YaDiskObject
from ._link_object import LinkObject
from ._disk import UserPublicInfoObject

from typing import Any, Literal, overload, Union, Protocol, Optional

from .._typing_compat import (
    Generator, Dict, List, AsyncGenerator, Iterable, Tuple, Type
)

from ..types import (
    AsyncFileOrPath, AsyncFileOrPathDestination, FileOrPath,
    FileOrPathDestination, Headers, TimeoutParameter, PublicSettings
)

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
    private_resource: Optional[str]
    public_resource: Optional[str]

    def __init__(self,
                 comment_ids: Optional[Dict] = None,
                 yadisk: Optional[Any] = None) -> None:
        ...


class EXIFObject(YaDiskObject):
    date_time: Optional[datetime.datetime]
    gps_longitude: Optional[float]
    gps_latitude:  Optional[float]

    def __init__(
        self,
        exif: Optional[Dict] = None,
        yadisk: Optional[Any] = None
    ) -> None:
        ...

class FilesResourceListObject(YaDiskObject):
    items: Optional[List["ResourceObject"]]
    limit: Optional[int]
    offset: Optional[int]

    def __init__(self,
                 files_resource_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None) -> None:
        ...


class SyncFilesResourceListObject(FilesResourceListObject):
    items: Optional[List["SyncResourceObject"]]  # type: ignore[assignment]

    def __init__(self,
                 files_resource_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None) -> None:
        ...

class AsyncFilesResourceListObject(FilesResourceListObject):
    items: Optional[List["AsyncResourceObject"]]  # type: ignore[assignment]

    def __init__(self,
                 files_resource_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None) -> None:
        ...


class LastUploadedResourceListObject(YaDiskObject):
    items: Optional[List["ResourceObject"]]
    limit: Optional[int]

    def __init__(self,
                 last_uploaded_resources_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None) -> None:
        ...


class SyncLastUploadedResourceListObject(LastUploadedResourceListObject):
    items: Optional[List["SyncResourceObject"]]  # type: ignore[assignment]

    def __init__(self,
                 last_uploaded_resources_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None) -> None:
        ...


class AsyncLastUploadedResourceListObject(LastUploadedResourceListObject):
    items: Optional[List["AsyncResourceObject"]]  # type: ignore[assignment]

    def __init__(self,
                 last_uploaded_resources_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None) -> None:
        ...


class PublicResourcesListObject(YaDiskObject):
    items: Optional[List["PublicResourceObject"]]
    type: Optional[str]
    limit: Optional[int]
    offset: Optional[int]

    def __init__(self,
                 public_resources_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None) -> None:
        ...


class SyncPublicResourcesListObject(PublicResourcesListObject):
    items: Optional[List["SyncPublicResourceObject"]]  # type: ignore[assignment]

    def __init__(self,
                 public_resources_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None) -> None:
        ...


class AsyncPublicResourcesListObject(PublicResourcesListObject):
    items: Optional[List["AsyncPublicResourceObject"]]  # type: ignore[assignment]

    def __init__(self,
                 public_resources_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None) -> None:
        ...


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
    def get_meta(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        sort: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> "SyncResourceObject":
        ...

    def get_public_meta(
        self: ResourceProtocol,
        *,
        path: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        sort: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> "SyncPublicResourceObject":
        ...

    def exists(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    def get_type(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> str:
        ...

    def is_dir(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    def is_file(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    def listdir(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        max_items: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        sort: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Generator[SyncResourceObject, None, None]:
        ...

    def public_listdir(
        self: ResourceProtocol,
        *,
        path: Optional[str] = None,
        max_items: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        sort: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Generator[SyncPublicResourceObject, None, None]:
        ...

    def get_upload_link(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        overwrite: bool = False,
        spoof_user_agent: bool = True,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs) -> str:
        ...

    def get_upload_link_object(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        overwrite: bool = False,
        fields: Optional[Iterable[str]] = None,
        spoof_user_agent: bool = True,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> ResourceUploadLinkObject:
        ...

    def upload(
        self: ResourceProtocol,
        path_or_file: FileOrPath,
        relative_path: Optional[str] = None,
        /,
        *,
        overwrite: bool = False,
        spoof_user_agent: bool = True,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> "SyncResourceLinkObject":
        ...

    def upload_url(
        self: ResourceProtocol,
        url: str,
        relative_path: Optional[str] = None,
        /,
        *,
        disable_redirects: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> "OperationLinkObject":
        ...

    def get_download_link(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> str:
        ...

    @overload
    def download(
        self: ResourceProtocol,
        dst_path_or_file: FileOrPathDestination,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> "SyncResourceLinkObject":
        ...

    @overload
    def download(
        self: ResourceProtocol,
        relative_path: Optional[str],
        dst_path_or_file: FileOrPathDestination,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> "SyncResourceLinkObject":
        ...

    @overload
    def patch(
        self: ResourceProtocol,
        properties: Dict,
        *,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> "SyncResourceObject":
        ...

    @overload
    def patch(
        self: ResourceProtocol,
        relative_path: Union[str, None],
        properties: Dict,
        *,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> "SyncResourceObject":
        ...

    def publish(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        allow_address_access: bool = False,
        public_settings: Optional[PublicSettings] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> "SyncResourceLinkObject":
        ...

    def unpublish(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> "SyncResourceLinkObject":
        ...

    def get_public_settings(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        allow_address_access: bool = False,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> "PublicSettingsObject":
        ...

    def get_public_available_settings(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> "PublicSettingsObject":
        ...

    @overload
    def update_public_settings(
        self: ResourceProtocol,
        relative_path: Optional[str],
        public_settings: PublicSettings,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> "PublicSettingsObject":
        ...

    @overload
    def update_public_settings(
        self: ResourceProtocol,
        public_settings: PublicSettings,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> "PublicSettingsObject":
        ...

    def mkdir(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncResourceLinkObject:
        ...

    def makedirs(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncResourceLinkObject:
        ...

    @overload
    def remove(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncOperationLinkObject:
        ...

    @overload
    def remove(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Optional[SyncOperationLinkObject]:
        ...

    @overload
    def move(
        self: ResourceProtocol,
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncOperationLinkObject:
        ...

    @overload
    def move(
        self: ResourceProtocol,
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Union[SyncResourceLinkObject, SyncOperationLinkObject]:
        ...

    @overload
    def move(
        self: ResourceProtocol,
        relative_path: Optional[str],
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncOperationLinkObject:
        ...

    @overload
    def move(
        self: ResourceProtocol,
        relative_path: Optional[str],
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Union[SyncResourceLinkObject, SyncOperationLinkObject]:
        ...

    @overload
    def rename(
        self: ResourceProtocol,
        new_name: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncOperationLinkObject:
        ...

    @overload
    def rename(
        self: ResourceProtocol,
        new_name: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Union[SyncResourceLinkObject, SyncOperationLinkObject]:
        ...

    @overload
    def rename(
        self: ResourceProtocol,
        relative_path: Optional[str],
        new_name: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncOperationLinkObject:
        ...

    @overload
    def rename(
        self: ResourceProtocol,
        relative_path: Optional[str],
        new_name: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Union[SyncResourceLinkObject, SyncOperationLinkObject]:
        ...

    @overload
    def copy(
        self: ResourceProtocol,
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncOperationLinkObject:
        ...

    @overload
    def copy(
        self: ResourceProtocol,
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Union[SyncResourceLinkObject, SyncOperationLinkObject]:
        ...

    @overload
    def copy(
        self: ResourceProtocol,
        relative_path: Optional[str],
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncOperationLinkObject:
        ...

    @overload
    def copy(
        self: ResourceProtocol,
        relative_path: Optional[str],
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Union[SyncResourceLinkObject, SyncOperationLinkObject]:
        ...


class AsyncResourceObjectMethodsMixin:
    async def get_meta(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        sort: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "AsyncResourceObject":
        ...

    async def get_public_meta(
        self: ResourceProtocol,
        *,
        path: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        sort: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "AsyncPublicResourceObject":
        ...

    async def exists(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    async def get_type(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        ...

    async def is_dir(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    async def is_file(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    async def listdir(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        max_items: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        sort: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncGenerator[AsyncResourceObject, None]:
        # This line here is needed so that the type checker knows that this is
        # an async generator, rather than a simple async function
        yield AsyncResourceObject()

    async def public_listdir(
        self: ResourceProtocol,
        *,
        path: Optional[str] = None,
        max_items: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        sort: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncGenerator[AsyncPublicResourceObject, None]:
        # This line here is needed so that the type checker knows that this is
        # an async generator, rather than a simple async function
        yield AsyncPublicResourceObject()

    async def get_upload_link(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        overwrite: bool = False,
        spoof_user_agent: bool = True,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        ...

    async def get_upload_link_object(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        overwrite: bool = False,
        fields: Optional[Iterable[str]] = None,
        spoof_user_agent: bool = True,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> ResourceUploadLinkObject:
        ...

    async def upload(
        self: ResourceProtocol,
        path_or_file: AsyncFileOrPath,
        relative_path: Optional[str] = None,
        /,
        *,
        overwrite: bool = False,
        spoof_user_agent: bool = True,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "AsyncResourceLinkObject":
        ...

    async def upload_url(
        self: ResourceProtocol,
        url: str,
        relative_path: Optional[str] = None,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        disable_redirects: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "AsyncOperationLinkObject":
        ...

    async def get_download_link(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        ...

    @overload
    async def download(
        self: ResourceProtocol,
        dst_path_or_file: AsyncFileOrPathDestination,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "AsyncResourceLinkObject":
        ...

    @overload
    async def download(
        self: ResourceProtocol,
        relative_path: Optional[str],
        dst_path_or_file: AsyncFileOrPathDestination,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "AsyncResourceLinkObject":
        ...

    @overload
    async def patch(
        self: ResourceProtocol,
        properties: Dict,
        *,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "AsyncResourceObject":
        ...

    @overload
    async def patch(
        self: ResourceProtocol,
        relative_path: Union[str, None],
        properties: dict,
        *,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "AsyncResourceObject":
        ...

    async def publish(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        allow_address_access: bool = False,
        public_settings: Optional[PublicSettings] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "AsyncResourceLinkObject":
        ...

    async def unpublish(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "AsyncResourceLinkObject":
        ...

    async def get_public_settings(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        allow_address_access: bool = False,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "PublicSettingsObject":
        ...

    async def get_public_available_settings(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "PublicSettingsObject":
        ...

    @overload
    async def update_public_settings(
        self: ResourceProtocol,
        relative_path: Optional[str],
        public_settings: PublicSettings,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "PublicSettingsObject":
        ...

    @overload
    async def update_public_settings(
        self: ResourceProtocol,
        public_settings: PublicSettings,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "PublicSettingsObject":
        ...

    async def mkdir(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "AsyncResourceLinkObject":
        ...

    async def makedirs(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "AsyncResourceLinkObject":
        ...

    @overload
    async def remove(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncOperationLinkObject:
        ...

    @overload
    async def remove(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Optional[AsyncOperationLinkObject]:
        ...

    @overload
    async def move(
        self: ResourceProtocol,
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncOperationLinkObject:
        ...

    @overload
    async def move(
        self: ResourceProtocol,
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[AsyncResourceLinkObject, AsyncOperationLinkObject]:
        ...

    @overload
    async def move(
        self: ResourceProtocol,
        relative_path: Optional[str],
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncOperationLinkObject:
        ...

    @overload
    async def move(
        self: ResourceProtocol,
        relative_path: Optional[str],
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[AsyncResourceLinkObject, AsyncOperationLinkObject]:
        ...

    @overload
    async def rename(
        self: ResourceProtocol,
        new_name: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncOperationLinkObject:
        ...

    @overload
    async def rename(
        self: ResourceProtocol,
        new_name: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[AsyncResourceLinkObject, AsyncOperationLinkObject]:
        ...

    @overload
    async def rename(
        self: ResourceProtocol,
        relative_path: Optional[str],
        new_name: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncOperationLinkObject:
        ...

    @overload
    async def rename(
        self: ResourceProtocol,
        relative_path: Optional[str],
        new_name: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[AsyncResourceLinkObject, AsyncOperationLinkObject]:
        ...

    @overload
    async def copy(
        self: ResourceProtocol,
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncOperationLinkObject:
        ...

    @overload
    async def copy(
        self: ResourceProtocol,
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[AsyncResourceLinkObject, AsyncOperationLinkObject]:
        ...

    @overload
    async def copy(
        self: ResourceProtocol,
        relative_path: Optional[str],
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncOperationLinkObject:
        ...

    @overload
    async def copy(
        self: ResourceProtocol,
        relative_path: Optional[str],
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[AsyncResourceLinkObject, AsyncOperationLinkObject]:
        ...


class ResourceObject(YaDiskObject):
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

    def __init__(self, resource: Optional[Dict] = None, yadisk: Optional[Any] = None) -> None:
        ...


class SyncResourceObject(ResourceObject, ResourceObjectMethodsMixin):
    embedded: Optional["SyncResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]
    _embedded: Optional["SyncResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(self, resource: Optional[Dict] = None, yadisk: Optional[Any] = None) -> None:
        ...


class AsyncResourceObject(ResourceObject, AsyncResourceObjectMethodsMixin):
    embedded: Optional["AsyncResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]
    _embedded: Optional["AsyncResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(self, resource: Optional[Dict] = None, yadisk: Optional[Any] = None) -> None:
        ...


class ResourceLinkObject(LinkObject):
    type: Optional[str]
    public_key: Optional[str]
    public_url: Optional[str]
    file: Optional[str]

    path: Optional[str]

    def __init__(self, link: Optional[Dict] = None, yadisk: Optional[Any] = None) -> None:
        ...

    @classmethod
    def from_path(cls, path: Optional[str], yadisk: Optional[Any] = None):
        ...


class SyncResourceLinkObject(ResourceLinkObject, ResourceObjectMethodsMixin):
    ...


class AsyncResourceLinkObject(ResourceLinkObject, AsyncResourceObjectMethodsMixin):
    ...


class PublicResourceLinkObject(LinkObject):
    type: Optional[str]
    file: Optional[str]

    path: Optional[str]
    public_key: Optional[str]
    public_url: Optional[str]

    def __init__(self, link: Optional[Dict] = None, yadisk: Optional[Any] = None) -> None:
        ...

    @classmethod
    def from_public_key(cls, public_key: Optional[str], yadisk: Optional[Any] = None):
        ...

class SyncPublicResourceLinkObject(PublicResourceLinkObject, ResourceObjectMethodsMixin):
    ...


class AsyncPublicResourceLinkObject(PublicResourceLinkObject, AsyncResourceObjectMethodsMixin):
    ...


class ResourceListObject(YaDiskObject):
    sort: Optional[str]
    items: Optional[List[ResourceObject]]
    limit: Optional[int]
    offset: Optional[int]
    path: Optional[str]
    total: Optional[int]

    def __init__(self, resource_list: Optional[Dict] = None, yadisk: Optional[Any] = None) -> None:
        ...


class SyncResourceListObject(ResourceListObject):
    items: Optional[List[SyncResourceObject]]  # type: ignore[assignment]

    def __init__(self, resource_list: Optional[Dict] = None, yadisk: Optional[Any] = None) -> None:
        ...


class AsyncResourceListObject(ResourceListObject):
    items: Optional[List[AsyncResourceObject]]  # type: ignore[assignment]

    def __init__(self, resource_list: Optional[Dict] = None, yadisk: Optional[Any] = None) -> None:
        ...


class ResourceUploadLinkObject(LinkObject):
    operation_id: Optional[str]

    def __init__(self,
                 resource_upload_link: Optional[Dict] = None,
                 yadisk: Optional[Any] = None) -> None:
        ...


class ResourceDownloadLinkObject(LinkObject):
    ...


class ShareInfoObject(YaDiskObject):
    is_root: Optional[bool]
    is_owned: Optional[bool]
    rights: Optional[str]

    def __init__(self, share_info: Optional[Dict] = None, yadisk: Optional[Any] = None) -> None:
        ...


class PublicResourceObject(ResourceObject):
    views_count: Optional[int]
    view_count: Optional[int]
    embedded: Optional["PublicResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]
    _embedded: Optional["PublicResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]
    owner: Optional[UserPublicInfoObject]

    def __init__(self, public_resource: Optional[Dict] = None, yadisk: Optional[Any] = None) -> None:
        ...


class SyncPublicResourceObject(PublicResourceObject, ResourceObjectMethodsMixin):
    embedded: Optional["SyncPublicResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]
    _embedded: Optional["SyncPublicResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(self, public_resource: Optional[Dict] = None, yadisk: Optional[Any] = None) -> None:
        ...


class AsyncPublicResourceObject(PublicResourceObject, AsyncResourceObjectMethodsMixin):
    embedded: Optional["AsyncPublicResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]
    _embedded: Optional["AsyncPublicResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(self, public_resource: Optional[Dict] = None, yadisk: Optional[Any] = None) -> None:
        ...


class PublicResourceListObject(ResourceListObject):
    public_key: Optional[str]
    items: Optional[List[PublicResourceObject]]  # type: ignore[assignment]

    def __init__(self,
                 public_resource_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None) -> None:
        ...


class SyncPublicResourceListObject(PublicResourceListObject):
    items: Optional[List[SyncPublicResourceObject]]  # type: ignore[assignment]

    def __init__(self, public_resource_list: Optional[Dict] = None, yadisk: Optional[Any] = None) -> None:
        ...


class AsyncPublicResourceListObject(PublicResourceListObject):
    items: Optional[List[AsyncPublicResourceObject]]  # type: ignore[assignment]

    def __init__(self, public_resource_list: Optional[Dict] = None, yadisk: Optional[Any] = None) -> None:
        ...


class TrashResourceObject(ResourceObject):
    embedded: Optional["TrashResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]
    _embedded: Optional["TrashResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]
    origin_path: Optional[str]
    deleted: Optional["datetime.datetime"]

    def __init__(self,
                 trash_resource: Optional[Dict] = None,
                 yadisk: Optional[Any] = None) -> None:
        ...


class SyncTrashResourceObject(TrashResourceObject):
    embedded: Optional["SyncTrashResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]
    _embedded: Optional["SyncTrashResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(self,
                 trash_resource: Optional[Dict] = None,
                 yadisk: Optional[Any] = None) -> None:
        ...

    def get_meta(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        sort: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> "SyncTrashResourceObject":
        ...

    def exists(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    def get_type(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> str:
        ...

    def is_dir(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    def is_file(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    def listdir(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        max_items: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        sort: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Generator[SyncTrashResourceObject, None, None]:
        ...

    @overload
    def remove(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncOperationLinkObject:
        ...

    @overload
    def remove(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Optional[SyncOperationLinkObject]:
        ...

    @overload
    def restore(
        self: ResourceProtocol,
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncOperationLinkObject:
        ...

    @overload
    def restore(
        self: ResourceProtocol,
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Union[SyncResourceLinkObject, SyncOperationLinkObject]:
        ...

    @overload
    def restore(
        self: ResourceProtocol,
        relative_path: Optional[str],
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> SyncOperationLinkObject:
        ...

    @overload
    def restore(
        self: ResourceProtocol,
        relative_path: Optional[str],
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        requests_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        curl_options: Optional[Dict[int, Any]] = None,
        **kwargs
    ) -> Union[SyncResourceLinkObject, SyncOperationLinkObject]:
        ...


class AsyncTrashResourceObject(TrashResourceObject):
    embedded: Optional["AsyncTrashResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]
    _embedded: Optional["AsyncTrashResourceListObject"]  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(self,
                 trash_resource: Optional[Dict] = None,
                 yadisk: Optional[Any] = None) -> None:
        ...

    async def get_meta(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        sort: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> "AsyncTrashResourceObject":
        ...

    async def exists(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    async def get_type(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        ...

    async def is_dir(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    async def is_file(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        ...

    async def listdir(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        max_items: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        preview_size: Optional[str] = None,
        preview_crop: Optional[bool] = None,
        sort: Optional[str] = None,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncGenerator[AsyncTrashResourceObject, None]:
        # This line here is needed so that the type checker knows that this is
        # an async generator, rather than a simple async function
        yield AsyncTrashResourceObject()

    @overload
    async def remove(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncOperationLinkObject:
        ...

    @overload
    async def remove(
        self: ResourceProtocol,
        relative_path: Optional[str] = None,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Optional[AsyncOperationLinkObject]:
        ...

    @overload
    async def restore(
        self: ResourceProtocol,
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncOperationLinkObject:
        ...

    @overload
    async def restore(
        self: ResourceProtocol,
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[AsyncResourceLinkObject, AsyncOperationLinkObject]:
        ...

    @overload
    async def restore(
        self: ResourceProtocol,
        relative_path: Optional[str],
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: Literal[True],
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncOperationLinkObject:
        ...

    @overload
    async def restore(
        self: ResourceProtocol,
        relative_path: Optional[str],
        dst_path: str,
        /,
        *,
        wait: bool = True,
        poll_interval: float = 1.0,
        poll_timeout: Optional[float] = None,
        overwrite: bool = False,
        force_async: bool = False,
        fields: Optional[Iterable[str]] = None,
        headers: Optional[Headers] = None,
        timeout: TimeoutParameter = ...,
        n_retries: Optional[int] = None,
        retry_interval: Optional[float] = None,
        retry_on: Tuple[Type[Exception], ...] = tuple(),
        aiohttp_args: Optional[Dict[str, Any]] = None,
        httpx_args: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Union[AsyncResourceLinkObject, AsyncOperationLinkObject]:
        ...


class TrashResourceListObject(ResourceListObject):
    items: Optional[List[TrashResourceObject]]  # type: ignore[assignment]

    def __init__(self,
                 trash_resource_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None) -> None:
        ...


class SyncTrashResourceListObject(TrashResourceListObject):
    items: Optional[List[SyncTrashResourceObject]]  # type: ignore[assignment]

    def __init__(self,
                 trash_resource_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None) -> None:
        ...


class AsyncTrashResourceListObject(TrashResourceListObject):
    items: Optional[List[AsyncTrashResourceObject]]  # type: ignore[assignment]

    def __init__(self,
                 trash_resource_list: Optional[Dict] = None,
                 yadisk: Optional[Any] = None) -> None:
        ...


class PublicSettingsObject(YaDiskObject):
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
        ...


class AvailableUntilVerboseObject(YaDiskObject):
    enabled: Optional[bool]
    value: Optional[int]

    def __init__(
        self,
        available_until_verbose: Optional[Dict] = None,
        yadisk: Optional[Any] = None
    ) -> None:
        ...


class PasswordVerboseObject(YaDiskObject):
    enabled: Optional[bool]
    value: Optional[str]

    def __init__(
        self,
        password_verbose: Optional[Dict] = None,
        yadisk: Optional[Any] = None
    ) -> None:
        ...


class ExternalOrganizationIdVerboseObject(YaDiskObject):
    enabled: Optional[bool]
    value: Optional[str]

    def __init__(
        self,
        external_organization_id_verbose: Optional[Dict] = None,
        yadisk: Optional[Any] = None
    ) -> None:
        ...


class PublicAccessObject(YaDiskObject):
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
        ...


class PublicAvailableSettingsObject(YaDiskObject):
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
        ...


class PublicDefaultObject(YaDiskObject):
    macros: Optional[List[str]]
    org_id: Optional[int]
    rights: Optional[List[str]]

    def __init__(
        self,
        public_default: Optional[Dict] = None,
        yadisk: Optional[Any] = None
    ) -> None:
        ...
