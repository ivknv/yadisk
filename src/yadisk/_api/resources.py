# -*- coding: utf-8 -*-
# Copyright © 2025 Ivan Konovalov

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

import typing
from ..types import PublicSettings
from .api_request import APIRequest
from ..objects import (
    PublicResourcesListObject, SyncPublicResourcesListObject, AsyncPublicResourcesListObject,
    TrashResourceObject, SyncTrashResourceObject, AsyncTrashResourceObject,
    FilesResourceListObject, SyncFilesResourceListObject, AsyncFilesResourceListObject,
    LastUploadedResourceListObject, SyncLastUploadedResourceListObject, AsyncLastUploadedResourceListObject,
    ResourceObject, SyncResourceObject, AsyncResourceObject, ResourceUploadLinkObject,
    PublicResourceObject, SyncPublicResourceObject, AsyncPublicResourceObject,
    OperationLinkObject, SyncOperationLinkObject, AsyncOperationLinkObject,
    ResourceLinkObject, SyncResourceLinkObject, AsyncResourceLinkObject, ResourceDownloadLinkObject,
    PublicSettingsObject, PublicAvailableSettingsObject
)

from .._common import is_operation_link, ensure_path_has_schema
from ..exceptions import InvalidResponseError

from .._typing_compat import Iterable, Dict, List
from typing import Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from ..types import AnySession, AnyClient, JSON

__all__ = [
    "CopyRequest",
    "DeleteRequest",
    "DeleteTrashRequest",
    "FilesRequest",
    "GetDownloadLinkRequest",
    "GetMetaRequest",
    "GetPublicAvailableSettingsRequest",
    "GetPublicDownloadLinkRequest",
    "GetPublicMetaRequest",
    "GetPublicResourcesRequest",
    "GetPublicSettingsRequest",
    "GetTrashRequest",
    "GetUploadLinkRequest",
    "LastUploadedRequest",
    "MkdirRequest",
    "MoveRequest",
    "PatchRequest",
    "PublishRequest",
    "RestoreTrashRequest",
    "SaveToDiskRequest",
    "UnpublishRequest",
    "UpdatePublicSettingsRequest",
    "UploadURLRequest",
]

Fields = Iterable[str]


def _substitute_keys(keys: Iterable[str], sub_map: Dict[str, str]) -> List[str]:
    return [".".join(sub_map.get(f, f) for f in k.split(".")) for k in keys]


class GetPublicResourcesRequest(APIRequest):
    """
        A request to get a list of public resources.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param offset: offset from the beginning of the list
        :param limit: maximum number of elements in the list
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param type: filter based on type of resources ("file" or "dir")
        :param fields: list of keys to be included in the response

        :returns: :any:`PublicResourcesListObject`
    """

    method = "GET"
    path = "/v1/disk/resources/public"

    def __init__(
        self,
        session:      "AnySession",
        offset:       int                     = 0,
        limit:        int                     = 20,
        preview_size: Optional[str]           = None,
        preview_crop: Optional[bool]          = None,
        type:         Optional[str]           = None,
        fields:       Optional[Iterable[str]] = None,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.params["offset"] = offset
        self.params["limit"] = limit

        if preview_size is not None:
            self.params["preview_size"] = preview_size

        if preview_crop is not None:
            self.params["preview_crop"] = "true" if preview_crop else "false"

        if type is not None:
            self.params["type"] = type

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> PublicResourcesListObject:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        if yadisk is None or yadisk.synchronous:
            return SyncPublicResourcesListObject(js, yadisk)
        else:
            return AsyncPublicResourcesListObject(js, yadisk)


class UnpublishRequest(APIRequest):
    """
        A request to make a public resource private.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param path: path to the resource to be unpublished
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceLinkObject`
    """

    method = "PUT"
    path = "/v1/disk/resources/unpublish"

    def __init__(
        self,
        session:  "AnySession",
        path:     str,
        fields:   Optional[Iterable[str]] = None,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.params["path"] = ensure_path_has_schema(path)

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> ResourceLinkObject:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        if yadisk is None or yadisk.synchronous:
            return SyncResourceLinkObject(js, yadisk)
        else:
            return AsyncResourceLinkObject(js, yadisk)


class GetDownloadLinkRequest(APIRequest):
    """
        A request to get a download link to a resource.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param path: path to the resource to be downloaded
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceDownloadLinkObject`
    """

    method = "GET"
    path = "/v1/disk/resources/download"

    def __init__(
        self,
        session:  "AnySession",
        path:     str,
        fields:   Optional[Iterable[str]] = None,
        **kwargs
    ):
        APIRequest.__init__(self, session, **kwargs)

        self.params["path"] = ensure_path_has_schema(path)

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> ResourceDownloadLinkObject:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        return ResourceDownloadLinkObject(js, yadisk)


class GetTrashRequest(APIRequest):
    """
        A request to get meta-information about a trash resource.

        :param path: path to the trash resource
        :param limit: number of children resources to be included in the response
        :param offset: number of children resources to be skipped in the response
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param sort: `str`, field to be used as a key to sort children resources
        :param fields: list of keys to be included in the response

        :returns: :any:`TrashResourceObject`
    """

    method = "GET"
    path = "/v1/disk/trash/resources"

    def __init__(
        self,
        session:      "AnySession",
        path:         str,
        offset:       int                     = 0,
        limit:        int                     = 20,
        sort:         Optional[str]           = None,
        preview_size: Optional[str]           = None,
        preview_crop: Optional[bool]          = None,
        fields:       Optional[Iterable[str]] = None,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.params["path"] = ensure_path_has_schema(path, "trash")
        self.params["offset"] = offset
        self.params["limit"] = limit

        if sort is not None:
            self.params["sort"] = sort

        if preview_size is not None:
            self.params["preview_size"] = preview_size

        if preview_crop is not None:
            self.params["preview_crop"] = "true" if preview_crop else "false"

        if fields is not None:
            sub_map = {"embedded": "_embedded"}

            self.params["fields"] = ",".join(_substitute_keys(fields, sub_map))

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> TrashResourceObject:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        if yadisk is None or yadisk.synchronous:
            return SyncTrashResourceObject(js, yadisk)
        else:
            return AsyncTrashResourceObject(js, yadisk)


class RestoreTrashRequest(APIRequest):
    """
        A request to restore trash.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param path: path to the trash resource to be restored
        :param dst_path: destination path
        :param force_async: forces the operation to be executed asynchronously
        :param overwrite: `bool`, determines whether the destination can be overwritten
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceLinkObject` or :any:`OperationLinkObject`
    """

    method = "PUT"
    path = "/v1/disk/trash/resources/restore"
    success_codes = {201, 202}

    def __init__(
        self,
        session:     "AnySession",
        path:        str,
        dst_path:    Optional[str]           = None,
        force_async: bool                    = False,
        overwrite:   bool                    = False,
        fields:      Optional[Iterable[str]] = None,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.params["path"] = ensure_path_has_schema(path, "trash")
        self.params["overwrite"] = "true" if overwrite else "false"
        self.params["force_async"] = "true" if force_async else "false"

        if dst_path is not None:
            self.params["name"] = dst_path

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> Union[OperationLinkObject, ResourceLinkObject]:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON", disable_retry=True)

        if is_operation_link(js.get("href", "")):
            if yadisk is None or yadisk.synchronous:
                return SyncOperationLinkObject(js, yadisk)
            else:
                return AsyncOperationLinkObject(js, yadisk)
        elif self.params.get("force_async") == "true":
            raise InvalidResponseError(
                "Yandex.Disk did not return an operation link, despite force_async=true",
                disable_retry=True
            )

        if yadisk is None or yadisk.synchronous:
            return SyncResourceLinkObject(js, yadisk)
        else:
            return AsyncResourceLinkObject(js, yadisk)


class DeleteTrashRequest(APIRequest):
    """
        A request to delete a trash resource.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param path: path to the trash resource to be deleted
        :param force_async: forces the operation to be executed asynchronously
        :param fields: list of keys to be included in the response

        :returns: :any:`OperationLinkObject` or `None`
    """

    method = "DELETE"
    path = "/v1/disk/trash/resources"
    success_codes = {202, 204}

    def __init__(
        self,
        session:     "AnySession",
        path:        Optional[str]           = None,
        force_async: bool                    = False,
        fields:      Optional[Iterable[str]] = None,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        if path is not None:
            self.params["path"] = ensure_path_has_schema(path, "trash")

        self.params["force_async"] = "true" if force_async else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> Optional[OperationLinkObject]:
        if js is not None:
            if not isinstance(js, dict):
                raise InvalidResponseError("Yandex.Disk returned invalid JSON", disable_retry=True)

            if yadisk is None or yadisk.synchronous:
                return SyncOperationLinkObject(js, yadisk)
            else:
                return AsyncOperationLinkObject(js, yadisk)
        elif self.params.get("force_async") == "true":
            raise InvalidResponseError(
                "Yandex.Disk did not return an operation link, despite force_async=true",
                disable_retry=True
            )

        return None


class LastUploadedRequest(APIRequest):
    """
        A request to get the list of latest uploaded files sorted by upload date.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param limit: maximum number of elements in the list
        :param media_type: type of files to include in the list
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param fields: list of keys to be included in the response

        :returns: :any:`LastUploadedResourceListObject`
    """

    method = "GET"
    path = "/v1/disk/resources/last-uploaded"

    def __init__(
        self,
        session: "AnySession",
        limit:        int                                 = 20,
        media_type:   Optional[Union[str, Iterable[str]]] = None,
        preview_size: Optional[str]                       = None,
        preview_crop: Optional[bool]                      = None,
        fields:       Optional[Iterable[str]]             = None,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.params["limit"] = limit

        if media_type is not None:
            if not isinstance(media_type, Iterable):
                raise TypeError("media_type should be a string or an iterable")

            if isinstance(media_type, str):
                self.params["media_type"] = media_type
            else:
                self.params["media_type"] = ",".join(media_type)

        if preview_size is not None:
            self.params["preview_size"] = preview_size

        if preview_crop is not None:
            self.params["preview_crop"] = "true" if preview_crop else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> LastUploadedResourceListObject:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        if yadisk is None or yadisk.synchronous:
            return SyncLastUploadedResourceListObject(js, yadisk)
        else:
            return AsyncLastUploadedResourceListObject(js, yadisk)


class CopyRequest(APIRequest):
    """
        A request to copy a file or a directory.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param src_path: source path
        :param dst_path: destination path
        :param overwrite: if `True` the destination path can be overwritten,
                          otherwise, an error will be raised
        :param force_async: forces the operation to be executed asynchronously
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceLinkObject` or :any:`OperationLinkObject`
    """

    method = "POST"
    path = "/v1/disk/resources/copy"
    success_codes = {201, 202}

    def __init__(
        self,
        session:     "AnySession",
        src_path:    str,
        dst_path:    str,
        overwrite:   bool             = False,
        force_async: bool             = False,
        fields:      Optional[Fields] = None,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.params["from"] = ensure_path_has_schema(src_path)
        self.params["path"] = ensure_path_has_schema(dst_path)
        self.params["overwrite"] = "true" if overwrite else "false"
        self.params["force_async"] = "true" if force_async else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> Union[OperationLinkObject, ResourceLinkObject]:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON", disable_retry=True)

        if is_operation_link(js.get("href", "")):
            if yadisk is None or yadisk.synchronous:
                return SyncOperationLinkObject(js, yadisk)
            else:
                return AsyncOperationLinkObject(js, yadisk)
        elif self.params.get("force_async") == "true":
            raise InvalidResponseError(
                "Yandex.Disk did not return an operation link, despite force_async=true",
                disable_retry=True
            )

        if yadisk is None or yadisk.synchronous:
            return SyncResourceLinkObject(js, yadisk)
        else:
            return AsyncResourceLinkObject(js, yadisk)


class GetMetaRequest(APIRequest):
    """
        A request to get meta-information about a resource.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param path: path to the resource
        :param limit: number of children resources to be included in the response
        :param offset: number of children resources to be skipped in the response
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param sort: `str`, field to be used as a key to sort children resources
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceObject`
    """

    method = "GET"
    path = "/v1/disk/resources"

    def __init__(
        self,
        session: "AnySession",
        path:         str,
        limit:        Optional[int]    = None,
        offset:       Optional[int]    = None,
        preview_size: Optional[str]    = None,
        preview_crop: Optional[bool]   = None,
        sort:         Optional[str]    = None,
        fields:       Optional[Fields] = None,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.params["path"] = ensure_path_has_schema(path)

        if limit is not None:
            self.params["limit"] = limit

        if offset is not None:
            self.params["offset"] = offset

        if preview_size is not None:
            self.params["preview_size"] = preview_size

        if preview_crop is not None:
            self.params["preview_crop"] = "true" if preview_crop else "false"

        if sort is not None:
            self.params["sort"] = sort

        if fields is not None:
            sub_map = {"embedded": "_embedded"}

            self.params["fields"] = ",".join(_substitute_keys(fields, sub_map))

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> ResourceObject:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        if yadisk is None or yadisk.synchronous:
            return SyncResourceObject(js, yadisk)
        else:
            return AsyncResourceObject(js, yadisk)


class GetUploadLinkRequest(APIRequest):
    """
        A request to get an upload link.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param path: path to be uploaded at
        :param overwrite: `bool`, determines whether to overwrite the destination
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceUploadLinkObject`
    """

    method = "GET"
    path = "/v1/disk/resources/upload"

    def __init__(
        self,
        session:   "AnySession",
        path:      str,
        overwrite: bool             = False,
        fields:    Optional[Fields] = None,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.params["path"] = ensure_path_has_schema(path)
        self.params["overwrite"] = "true" if overwrite else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> ResourceUploadLinkObject:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        return ResourceUploadLinkObject(js, yadisk)


class MkdirRequest(APIRequest):
    """
        A request to create a new directory.

        :param path: path to the directory to be created
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceLinkObject`
    """

    method = "PUT"
    path = "/v1/disk/resources"
    success_codes = {201}

    def __init__(
        self,
        session:  "AnySession",
        path:     str,
        fields:   Optional[Fields] = None,
        **kwargs
    ):
        APIRequest.__init__(self, session, **kwargs)

        self.params["path"] = ensure_path_has_schema(path)

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> ResourceLinkObject:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON", disable_retry=True)

        if yadisk is None or yadisk.synchronous:
            return SyncResourceLinkObject(js, yadisk)
        else:
            return AsyncResourceLinkObject(js, yadisk)


class PublishRequest(APIRequest):
    """
        A request to make a resource public.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param path: path to the resource to be published
        :param allow_address_access: `bool`, specifies the request format, i.e.
            with personal access settings (when set to `True`) or without
        :param public_settings: :any:`PublicSettings`, public access settings for the resource
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceLinkObject`
    """

    method = "PUT"
    path = "/v1/disk/resources/publish"
    content_type = "application/json"

    def __init__(
        self,
        session:              "AnySession",
        path:                 str,
        allow_address_access: bool = False,
        public_settings:      Optional[PublicSettings] = None,
        fields:               Optional[Fields] = None,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.params["path"] = ensure_path_has_schema(path)
        self.params["allow_address_access"] = "true" if allow_address_access else "false"
        self.data = {"public_settings": public_settings or {}}

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> ResourceLinkObject:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        if yadisk is None or yadisk.synchronous:
            return SyncResourceLinkObject(js, yadisk)
        else:
            return AsyncResourceLinkObject(js, yadisk)


class GetPublicSettingsRequest(APIRequest):
    """
        A request to get public settings of a resource.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param path: path to the resource
        :param allow_address_access: `bool`, specifies the request format, i.e.
            with personal access settings (when set to `True`) or without
        :param fields: list of keys to be included in the response

        :returns: :any:`PublicSettingsObject`
    """

    method = "GET"
    path = "/v1/disk/public/resources/public-settings"

    def __init__(
        self,
        session: "AnySession",
        path: str,
        allow_address_access: bool = False,
        fields: Optional[Fields] = None,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.params["path"] = ensure_path_has_schema(path)
        self.params["allow_address_access"] = "true" if allow_address_access else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> PublicSettingsObject:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        return PublicSettingsObject(js)


class GetPublicAvailableSettingsRequest(APIRequest):
    """
        A request to get public settings of a shared resource for the current OAuth token owner.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param path: path to the resource

        :returns: :any:`PublicAvailableSettingsObject`
    """

    method = "GET"
    path = "/v1/disk/public/resources/public-settings/available-settings"

    def __init__(
        self,
        session: "AnySession",
        path: str,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.params["path"] = ensure_path_has_schema(path)

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> PublicAvailableSettingsObject:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        return PublicAvailableSettingsObject(js)


class UpdatePublicSettingsRequest(APIRequest):
    """
        A request to update public settings of a shared resource.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param path: path to the resource
        :param public_settings: :any:`PublicSettings`, public access settings for the resource

        :returns: `None`
    """

    method = "PATCH"
    path = "/v1/disk/public/resources/public-settings"
    content_type = "application/json"

    def __init__(
        self,
        session: "AnySession",
        path: str,
        public_settings: PublicSettings,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.params["path"] = ensure_path_has_schema(path)
        self.data = typing.cast(Dict, public_settings)

    def process_json(self, js: "JSON", yadisk: Optional["AnyClient"] = None, **kwargs) -> None:
        return


class UploadURLRequest(APIRequest):
    """
        A request to upload a file from URL.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param url: source URL
        :param path: destination path
        :param disable_redirects: `bool`, forbid redirects
        :param fields: list of keys to be included in the response

        :returns: :any:`OperationLinkObject`
    """

    method = "POST"
    path = "/v1/disk/resources/upload"
    success_codes = {202}

    def __init__(
        self,
        session:           "AnySession",
        url:               str,
        path:              str,
        disable_redirects: bool             = False,
        fields:            Optional[Fields] = None,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.params["url"] = url
        self.params["path"] = ensure_path_has_schema(path)
        self.params["disable_redirects"] = "true" if disable_redirects else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> OperationLinkObject:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON", disable_retry=True)

        if yadisk is None or yadisk.synchronous:
            return SyncOperationLinkObject(js, yadisk)
        else:
            return AsyncOperationLinkObject(js, yadisk)


class DeleteRequest(APIRequest):
    """
        A request to delete a file or a directory.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param path: path to the resource to be removed
        :param permanently: if `True`, the resource will be removed permanently,
                            otherwise, it will be just moved to the trash
        :param force_async: forces the operation to be executed asynchronously
        :param md5: `str`, MD5 hash of the file to remove
        :param fields: list of keys to be included in the response

        :returns: :any:`OperationLinkObject` or `None`
    """

    method = "DELETE"
    path = "/v1/disk/resources"
    success_codes = {202, 204}

    def __init__(
        self,
        session:     "AnySession",
        path:        str,
        permanently: bool             = False,
        md5:         Optional[str]    = None,
        force_async: bool             = False,
        fields:      Optional[Fields] = None,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.params["path"] = ensure_path_has_schema(path)
        self.params["permanently"] = "true" if permanently else "false"
        self.params["force_async"] = "true" if force_async else "false"

        if md5 is not None:
            self.params["md5"] = md5

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> Optional[OperationLinkObject]:
        if isinstance(js, dict):
            if yadisk is None or yadisk.synchronous:
                return SyncOperationLinkObject(js, yadisk)
            else:
                return AsyncOperationLinkObject(js, yadisk)
        elif js is not None:
            raise InvalidResponseError("Yandex.Disk returned invalid JSON", disable_retry=True)
        elif self.params.get("force_async") == "true":
            raise InvalidResponseError(
                "Yandex.Disk did not return an operation link, despite force_async=true",
                disable_retry=True
            )

        return None


class SaveToDiskRequest(APIRequest):
    """
        A request to save a public resource to the disk.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param public_key: public key or public URL of the resource
        :param name: filename of the saved resource
        :param path: path to the copied resource in the public folder
        :param save_path: path to the destination directory (downloads directory by default)
        :param force_async: forces the operation to be executed asynchronously
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceLinkObject` or :any:`OperationLinkObject`
    """

    method = "POST"
    path = "/v1/disk/public/resources/save-to-disk"
    success_codes = {201, 202}

    def __init__(
        self,
        session:     "AnySession",
        public_key:  str,
        name:        Optional[str]    = None,
        path:        Optional[str]    = None,
        save_path:   Optional[str]    = None,
        force_async: bool             = False,
        fields:      Optional[Fields] = None,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.params["public_key"] = public_key

        if name is not None:
            self.params["name"] = name

        if path is not None:
            self.params["path"] = path

        if save_path is not None:
            self.params["save_path"] = ensure_path_has_schema(save_path)

        self.params["force_async"] = "true" if force_async else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> Union[OperationLinkObject, ResourceLinkObject]:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON", disable_retry=True)

        if is_operation_link(js.get("href", "")):
            if yadisk is None or yadisk.synchronous:
                return SyncOperationLinkObject(js, yadisk)
            else:
                return AsyncOperationLinkObject(js, yadisk)
        elif self.params.get("force_async") == "true":
            raise InvalidResponseError(
                "Yandex.Disk did not return an operation link, despite force_async=true",
                disable_retry=True
            )

        if yadisk is None or yadisk.synchronous:
            return SyncResourceLinkObject(js, yadisk)
        else:
            return AsyncResourceLinkObject(js, yadisk)


class GetPublicMetaRequest(APIRequest):
    """
        A request to get meta-information about a public resource.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param public_key: public key or public URL of the resource
        :param path: relative path to a resource in a public folder.
                     By specifying the key of the published folder in `public_key`,
                     you can request metainformation for any resource in the folder.
        :param offset: offset from the beginning of the list of nested resources
        :param limit: maximum number of nested elements to be included in the list
        :param sort: `str`, field to be used as a key to sort children resources
        :param preview_size: file preview size
        :param preview_crop: `bool`, allow preview crop
        :param fields: list of keys to be included in the response

        :returns: :any:`PublicResourceObject`
    """

    method = "GET"
    path = "/v1/disk/public/resources"

    def __init__(
        self,
        session:      "AnySession",
        public_key:   str,
        offset:       int              = 0,
        limit:        int              = 20,
        path:         Optional[str]    = None,
        sort:         Optional[str]    = None,
        preview_size: Optional[str]    = None,
        preview_crop: Optional[bool]   = None,
        fields:       Optional[Fields] = None,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.params["public_key"] = public_key
        self.params["offset"] = offset
        self.params["limit"] = limit

        if path is not None:
            self.params["path"] = path

        if sort is not None:
            self.params["sort"] = sort

        if preview_size is not None:
            self.params["preview_size"] = preview_size

        if preview_crop is not None:
            self.params["preview_crop"] = "true" if preview_crop else "false"

        if fields is not None:
            sub_map = {"embedded": "_embedded",
                       "view_count": "views_count"}

            self.params["fields"] = ",".join(_substitute_keys(fields, sub_map))

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> PublicResourceObject:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        if yadisk is None or yadisk.synchronous:
            return SyncPublicResourceObject(js, yadisk)
        else:
            return AsyncPublicResourceObject(js, yadisk)


class GetPublicDownloadLinkRequest(APIRequest):
    """
        A request to get a download link for a public resource.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param public_key: public key or public URL of the resource
        :param path: relative path to the resource within the public folder
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceDownloadLinkObject`
    """

    method = "GET"
    path = "/v1/disk/public/resources/download"

    def __init__(
        self,
        session:    "AnySession",
        public_key: str,
        path:       Optional[str]    = None,
        fields:     Optional[Fields] = None,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.params["public_key"] = public_key

        if path is not None:
            self.params["path"] = path

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> ResourceDownloadLinkObject:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        return ResourceDownloadLinkObject(js, yadisk)


class MoveRequest(APIRequest):
    """
        A request to move a resource.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param src_path: source path to be moved
        :param dst_path: destination path
        :param force_async: forces the operation to be executed asynchronously
        :param overwrite: `bool`, determines whether to overwrite the destination
        :param fields: list of keys to be included in the response

        :returns: :any:`OperationLinkObject` or :any:`ResourceLinkObject`
    """

    method = "POST"
    path = "/v1/disk/resources/move"
    success_codes = {201, 202}

    def __init__(
        self,
        session:      "AnySession",
        src_path:    str,
        dst_path:    str,
        force_async: bool             = False,
        overwrite:   bool             = False,
        fields:      Optional[Fields] = None,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.params["from"] = ensure_path_has_schema(src_path)
        self.params["path"] = ensure_path_has_schema(dst_path)
        self.params["overwrite"] = "true" if overwrite else "false"
        self.params["force_async"] = "true" if force_async else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> Union[OperationLinkObject, ResourceLinkObject]:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON", disable_retry=True)

        if is_operation_link(js.get("href", "")):
            if yadisk is None or yadisk.synchronous:
                return SyncOperationLinkObject(js, yadisk)
            else:
                return AsyncOperationLinkObject(js, yadisk)
        elif self.params.get("force_async") == "true":
            raise InvalidResponseError(
                "Yandex.Disk did not return an operation link, despite force_async=true",
                disable_retry=True
            )

        if yadisk is None or yadisk.synchronous:
            return SyncResourceLinkObject(js, yadisk)
        else:
            return AsyncResourceLinkObject(js, yadisk)


class FilesRequest(APIRequest):
    """
        A request to get a flat list of all files (that doesn't include directories).

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param offset: offset from the beginning of the list
        :param limit: number of list elements to be included
        :param media_type: type of files to include in the list
        :param sort: `str`, field to be used as a key to sort children resources
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param fields: list of keys to be included in the response

        :returns: :any:`FilesResourceListObject`
    """

    method = "GET"
    path = "/v1/disk/resources/files"

    def __init__(
        self,
        session:      "AnySession",
        offset:       int                                 = 0,
        limit:        int                                 = 20,
        media_type:   Optional[Union[str, Iterable[str]]] = None,
        preview_size: Optional[str]                       = None,
        preview_crop: Optional[bool]                      = None,
        sort:         Optional[str]                       = None,
        fields:       Optional[Fields]                    = None,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.params["offset"] = offset
        self.params["limit"] = limit

        if media_type is not None:
            if not isinstance(media_type, Iterable):
                raise TypeError("media_type should be a string or an iterable")

            if isinstance(media_type, str):
                self.params["media_type"] = media_type
            else:
                self.params["media_type"] = ",".join(media_type)

        if preview_size is not None:
            self.params["preview_size"] = preview_size

        if preview_crop is not None:
            self.params["preview_crop"] = "true" if preview_crop else "false"

        if sort is not None:
            self.params["sort"] = sort

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> FilesResourceListObject:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        if yadisk is None or yadisk.synchronous:
            return SyncFilesResourceListObject(js, yadisk)
        else:
            return AsyncFilesResourceListObject(js, yadisk)


class PatchRequest(APIRequest):
    """
        A request to update custom properties of a resource.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param path: path to the resource
        :param properties: `dict`, custom properties to update
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceObject`
    """

    method = "PATCH"
    path = "/v1/disk/resources"
    content_type = "application/json"

    def __init__(
        self,
        session:    "AnySession",
        path:       str,
        properties: dict,
        fields:     Optional[Fields] = None,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.params["path"] = ensure_path_has_schema(path)
        self.data = {"custom_properties": properties}

        if fields is not None:
            sub_map = {"embedded": "_embedded"}

            self.params["fields"] = ",".join(_substitute_keys(fields, sub_map))

    def process_json(
        self,
        js: "JSON",
        yadisk: Optional["AnyClient"] = None,
        **kwargs
    ) -> ResourceObject:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        if yadisk is None or yadisk.synchronous:
            return SyncResourceObject(js, yadisk)
        else:
            return AsyncResourceObject(js, yadisk)
