# -*- coding: utf-8 -*-

import json

from .api_request import APIRequest
from ..objects import PublicResourcesListObject, TrashResourceObject
from ..objects import FilesResourceListObject, LastUploadedResourceListObject
from ..objects import ResourceObject, ResourceUploadLinkObject, PublicResourceObject
from ..objects import OperationLinkObject, ResourceLinkObject, ResourceDownloadLinkObject
from ..common import is_operation_link, ensure_path_has_schema
from ..exceptions import InvalidResponseError

from ..compat import Iterable, Dict, List
from typing import Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    import requests
    from ..yadisk import YaDisk

__all__ = ["GetPublicResourcesRequest", "UnpublishRequest", "GetDownloadLinkRequest",
           "GetTrashRequest", "RestoreTrashRequest", "DeleteTrashRequest",
           "LastUploadedRequest", "CopyRequest", "GetMetaRequest", "GetUploadLinkRequest",
           "MkdirRequest", "PublishRequest", "UploadURLRequest", "DeleteRequest",
           "SaveToDiskRequest", "GetPublicMetaRequest", "GetPublicDownloadLinkRequest",
           "MoveRequest", "FilesRequest", "PatchRequest"]

Fields = Iterable[str]

def _substitute_keys(keys: Iterable[str], sub_map: Dict[str, str]) -> List[str]:
    return [".".join(sub_map.get(f, f) for f in k.split(".")) for k in keys]

class GetPublicResourcesRequest(APIRequest):
    """
        A request to get a list of public resources.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param offset: offset from the beginning of the list
        :param limit: maximum number of elements in the list
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param type: filter based on type of resources ("file" or "dir")
        :param fields: list of keys to be included in the response

        :returns: :any:`PublicResourcesListObject`
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources/public"
    method = "GET"

    def __init__(self,
                 session: "requests.Session",
                 offset: int = 0,
                 limit: int = 20,
                 preview_size: Optional[str] = None,
                 preview_crop: Optional[bool] = None,
                 type: Optional[str] = None,
                 fields: Optional[Iterable[str]] = None, **kwargs):
        APIRequest.__init__(self, session, {"offset":       offset,
                                            "limit":        limit,
                                            "preview_size": preview_size,
                                            "preview_crop": preview_crop,
                                            "type":         type,
                                            "fields":       fields}, **kwargs)

    def process_args(self,
                     offset: int,
                     limit: int,
                     preview_size: Optional[str],
                     preview_crop: Optional[bool],
                     type: Optional[str],
                     fields: Optional[Iterable[str]]) -> None:
        self.params["offset"] = offset
        self.params["limit"] = limit

        if preview_size is not None:
            self.params["preview_size"] = preview_size

        if preview_crop is not None:
            self.params["preview_crop"] = preview_crop

        if type is not None:
            self.params["type"] = type

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self,
                     js: Optional[dict],
                     yadisk: Optional["YaDisk"] = None) -> PublicResourcesListObject:
        if js is None:
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        return PublicResourcesListObject(js, yadisk)

class UnpublishRequest(APIRequest):
    """
        A request to make a public resource private.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the resource to be unpublished
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceLinkObject`
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources/unpublish"
    method = "PUT"

    def __init__(self,
                 session: "requests.Session",
                 path: str,
                 fields: Optional[Iterable[str]] = None, **kwargs):
        APIRequest.__init__(self, session, {"path":   path,
                                            "fields": fields}, **kwargs)

    def process_args(self, path: str, fields: Optional[Iterable[str]]) -> None:
        self.params["path"] = ensure_path_has_schema(path)

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self,
                     js: Optional[dict],
                     yadisk: Optional["YaDisk"] = None) -> ResourceLinkObject:
        if js is None:
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        return ResourceLinkObject(js, yadisk)

class GetDownloadLinkRequest(APIRequest):
    """
        A request to get a download link to a resource.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the resource to be downloaded
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceDownloadLinkObject`
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources/download"
    method = "GET"

    def __init__(self,
                 session: "requests.Session",
                 path: str,
                 fields: Optional[Iterable[str]] = None, **kwargs):
        APIRequest.__init__(
            self, session, {"path": path, "fields": fields}, **kwargs)

    def process_args(self, path: str, fields: Optional[Iterable[str]]) -> None:
        self.params["path"] = ensure_path_has_schema(path)

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self,
                     js: Optional[dict],
                     yadisk: Optional["YaDisk"] = None) -> ResourceDownloadLinkObject:
        if js is None:
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

    url = "https://cloud-api.yandex.net/v1/disk/trash/resources"
    method = "GET"

    def __init__(self,
                 session: "requests.Session",
                 path: str,
                 offset: int = 0,
                 limit: int = 20,
                 sort: Optional[str] = None,
                 preview_size: Optional[str] = None,
                 preview_crop: Optional[bool] = None,
                 fields: Optional[Iterable[str]] = None, **kwargs):
        APIRequest.__init__(self, session, {"path":         path,
                                            "offset":       offset,
                                            "limit":        limit,
                                            "sort":         sort,
                                            "preview_size": preview_size,
                                            "preview_crop": preview_crop,
                                            "fields":       fields}, **kwargs)

    def process_args(self,
                     path: str,
                     offset: int,
                     limit: int,
                     sort: Optional[str],
                     preview_size: Optional[str],
                     preview_crop: Optional[bool],
                     fields: Optional[Iterable[str]]) -> None:
        self.params["path"] = ensure_path_has_schema(path, "trash")
        self.params["offset"] = offset
        self.params["limit"] = limit

        if sort is not None:
            self.params["sort"] = sort

        if preview_size is not None:
            self.params["preview_size"] = preview_size

        if preview_crop is not None:
            self.params["preview_crop"] = preview_crop

        if fields is not None:
            sub_map = {"embedded": "_embedded"}

            self.params["fields"] = ",".join(_substitute_keys(fields, sub_map))

    def process_json(self,
                     js: Optional[dict],
                     yadisk: Optional["YaDisk"] = None) -> TrashResourceObject:
        if js is None:
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        return TrashResourceObject(js, yadisk)

class RestoreTrashRequest(APIRequest):
    """
        A request to restore trash.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the trash resource to be restored
        :param dst_path: destination path
        :param force_async: forces the operation to be executed asynchronously
        :param overwrite: `bool`, determines whether the destination can be overwritten
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceLinkObject` or :any:`OperationLinkObject`
    """

    url = "https://cloud-api.yandex.net/v1/disk/trash/resources/restore"
    method = "PUT"
    success_codes = {201, 202}

    def __init__(self,
                 session: "requests.Session",
                 path: str,
                 dst_path: Optional[str] = None,
                 force_async: bool = False,
                 overwrite: bool = False,
                 fields: Optional[Iterable[str]] = None, **kwargs):
        APIRequest.__init__(self, session, {"path":        path,
                                            "dst_path":    dst_path,
                                            "overwrite":   overwrite,
                                            "force_async": force_async,
                                            "fields":      fields}, **kwargs)

    def process_args(self,
                     path: str,
                     dst_path: Optional[str],
                     force_async: bool,
                     overwrite: bool,
                     fields: Optional[Iterable[str]]) -> None:
        self.params["path"] = ensure_path_has_schema(path, "trash")
        self.params["overwrite"] = "true" if overwrite else "false"
        self.params["force_async"] = "true" if force_async else "false"

        if dst_path is not None:
            self.params["name"] = dst_path

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self,
                     js: Optional[dict],
                     yadisk: Optional["YaDisk"] = None) -> Union[OperationLinkObject, ResourceLinkObject]:
        if js is None:
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        if is_operation_link(js.get("href", "")):
            return OperationLinkObject(js, yadisk)

        return ResourceLinkObject(js, yadisk)

class DeleteTrashRequest(APIRequest):
    """
        A request to delete a trash resource.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the trash resource to be deleted
        :param force_async: forces the operation to be executed asynchronously
        :param fields: list of keys to be included in the response

        :returns: :any:`OperationLinkObject` or `None`
    """

    url = "https://cloud-api.yandex.net/v1/disk/trash/resources"
    method = "DELETE"
    success_codes = {202, 204}

    def __init__(self,
                 session: "requests.Session",
                 path: Optional[str] = None,
                 force_async: bool = False,
                 fields: Optional[Iterable[str]] = None, **kwargs):
        APIRequest.__init__(self, session, {"path":        path,
                                            "force_async": force_async,
                                            "fields":      fields}, **kwargs)

    def process_args(self,
                     path: Optional[str],
                     force_async: bool,
                     fields: Optional[Iterable[str]]) -> None:
        if path is not None:
            self.params["path"] = ensure_path_has_schema(path, "trash")

        self.params["force_async"] = "true" if force_async else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self,
                     js: Optional[dict],
                     yadisk: Optional["YaDisk"] = None) -> Optional[OperationLinkObject]:
        if js is not None:
            return OperationLinkObject(js, yadisk)

class LastUploadedRequest(APIRequest):
    """
        A request to get the list of latest uploaded files sorted by upload date.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param limit: maximum number of elements in the list
        :param media_type: type of files to include in the list
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param fields: list of keys to be included in the response

        :returns: :any:`LastUploadedResourceListObject`
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources/last-uploaded"
    method = "GET"

    def __init__(self,
                 session: "requests.Session",
                 limit: int = 20,
                 media_type: Optional[Union[str, Iterable[str]]] = None,
                 preview_size: Optional[str] = None,
                 preview_crop: Optional[bool] = None,
                 fields: Optional[Iterable[str]] = None, **kwargs):
        APIRequest.__init__(self, session, {"limit":        limit,
                                            "media_type":   media_type,
                                            "preview_size": preview_size,
                                            "preview_crop": preview_crop,
                                            "fields":       fields}, **kwargs)

    def process_args(self,
                     limit: int,
                     media_type: Optional[str],
                     preview_size: Optional[str],
                     preview_crop: Optional[bool],
                     fields: Optional[Iterable[str]]) -> None:
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
            self.params["preview_crop"] = preview_crop

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self,
                     js: Optional[dict],
                     yadisk: Optional["YaDisk"] = None) -> LastUploadedResourceListObject:
        if js is None:
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")
        return LastUploadedResourceListObject(js, yadisk)

class CopyRequest(APIRequest):
    """
        A request to copy a file or a directory.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param src_path: source path
        :param dst_path: destination path
        :param overwrite: if `True` the destination path can be overwritten,
                          otherwise, an error will be raised
        :param force_async: forces the operation to be executed asynchronously
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceLinkObject` or :any:`OperationLinkObject`
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources/copy"
    method = "POST"
    success_codes = {201, 202}

    def __init__(self,
                 session: "requests.Session",
                 src_path: str,
                 dst_path: str,
                 overwrite: bool = False,
                 force_async: bool = False,
                 fields: Optional[Fields] = None, **kwargs):
        APIRequest.__init__(self, session, {"src_path":    src_path,
                                            "dst_path":    dst_path,
                                            "overwrite":   overwrite,
                                            "force_async": force_async,
                                            "fields":      fields}, **kwargs)

    def process_args(self,
                     src_path: str,
                     dst_path: str,
                     overwrite: bool,
                     force_async: bool,
                     fields: Optional[Fields]) -> None:
        self.params["from"] = ensure_path_has_schema(src_path)
        self.params["path"] = ensure_path_has_schema(dst_path)
        self.params["overwrite"] = "true" if overwrite else "false"
        self.params["force_async"] = "true" if force_async else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self,
                     js: Optional[dict],
                     yadisk: Optional["YaDisk"] = None) -> Union[OperationLinkObject, ResourceLinkObject]:
        if js is None:
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        if is_operation_link(js.get("href", "")):
            return OperationLinkObject(js, yadisk)

        return ResourceLinkObject(js, yadisk)

class GetMetaRequest(APIRequest):
    """
        A request to get meta-information about a resource.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the resource
        :param limit: number of children resources to be included in the response
        :param offset: number of children resources to be skipped in the response
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param sort: `str`, field to be used as a key to sort children resources
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceObject`
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources"
    method = "GET"

    def __init__(self,
                 session: "requests.Session",
                 path: str,
                 limit: Optional[int] = None,
                 offset: Optional[int] = None,
                 preview_size: Optional[str] = None,
                 preview_crop: Optional[bool] = None,
                 sort: Optional[str] = None,
                 fields: Optional[Fields] = None, **kwargs):
        APIRequest.__init__(self, session,
                            {"path":         path,
                             "limit":        limit,
                             "offset":       offset,
                             "preview_size": preview_size,
                             "preview_crop": preview_crop,
                             "sort":         sort,
                             "fields":       fields}, **kwargs)

    def process_args(self,
                     path: str,
                     limit: Optional[int],
                     offset: Optional[int],
                     preview_size: Optional[str],
                     preview_crop: Optional[bool],
                     sort: Optional[str],
                     fields: Optional[Fields]) -> None:
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

    def process_json(self,
                     js: Optional[dict],
                     yadisk: Optional["YaDisk"] = None) -> ResourceObject:
        if js is None:
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        return ResourceObject(js, yadisk)

class GetUploadLinkRequest(APIRequest):
    """
        A request to get an upload link.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to be uploaded at
        :param overwrite: `bool`, determines whether to overwrite the destination
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceUploadLinkObject`
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    method = "GET"

    def __init__(self,
                 session: "requests.Session",
                 path: str,
                 overwrite: bool = False,
                 fields: Optional[Fields] = None, **kwargs):
        APIRequest.__init__(self, session, {"path":      path,
                                            "overwrite": overwrite,
                                            "fields":    fields}, **kwargs)

    def process_args(self, path: str, overwrite: bool, fields: Optional[Fields]) -> None:
        self.params["path"] = ensure_path_has_schema(path)
        self.params["overwrite"] = "true" if overwrite else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self,
                     js: Optional[dict],
                     yadisk: Optional["YaDisk"] = None) -> ResourceUploadLinkObject:
        if js is None:
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        return ResourceUploadLinkObject(js, yadisk)

class MkdirRequest(APIRequest):
    """
        A request to create a new directory.

        :param path: path to the directory to be created
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceLinkObject`
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources"
    method = "PUT"
    success_codes = {201}

    def __init__(self,
                 session: "requests.Session",
                 path: str,
                 fields: Optional[Fields] = None, **kwargs):
        APIRequest.__init__(self, session, {"path": path, "fields": fields},
                            **kwargs)

    def process_args(self, path: str, fields: Optional[Fields]) -> None:
        self.params["path"] = ensure_path_has_schema(path)

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self,
                     js: Optional[dict],
                     yadisk: Optional["YaDisk"] = None) -> ResourceLinkObject:
        if js is None:
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        return ResourceLinkObject(js, yadisk)

class PublishRequest(APIRequest):
    """
        A request to make a resource public.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the resource to be published
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceLinkObject`
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources/publish"
    method = "PUT"

    def __init__(self,
                 session: "requests.Session",
                 path: str,
                 fields: Optional[Fields] = None, **kwargs):
        APIRequest.__init__(self, session, {"path":   path,
                                            "fields": fields}, **kwargs)

    def process_args(self, path: str, fields: Optional[Fields]) -> None:
        self.params["path"] = ensure_path_has_schema(path)

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self,
                     js: Optional[dict],
                     yadisk: Optional["YaDisk"] = None) -> ResourceLinkObject:
        if js is None:
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        return ResourceLinkObject(js, yadisk)

class UploadURLRequest(APIRequest):
    """
        A request to upload a file from URL.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param url: source URL
        :param path: destination path
        :param disable_redirects: `bool`, forbid redirects
        :param fields: list of keys to be included in the response

        :returns: :any:`OperationLinkObject`
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    method = "POST"
    success_codes = {202}

    def __init__(self,
                 session: "requests.Session",
                 url: str,
                 path: str,
                 disable_redirects: bool = False,
                 fields: Optional[Fields] = None, **kwargs):
        APIRequest.__init__(self, session, {"url":               url,
                                            "path":              path,
                                            "disable_redirects": disable_redirects,
                                            "fields":            fields}, **kwargs)

    def process_args(self,
                     url: str,
                     path: str,
                     disable_redirects: bool,
                     fields: Optional[Fields]) -> None:
        self.params["url"] = url
        self.params["path"] = ensure_path_has_schema(path)
        self.params["disable_redirects"] = "true" if disable_redirects else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self,
                     js: Optional[dict],
                     yadisk: Optional["YaDisk"] = None) -> OperationLinkObject:
        if js is None:
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        return OperationLinkObject(js, yadisk)

class DeleteRequest(APIRequest):
    """
        A request to delete a file or a directory.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the resource to be removed
        :param permanently: if `True`, the resource will be removed permanently,
                            otherwise, it will be just moved to the trash
        :param force_async: forces the operation to be executed asynchronously
        :param md5: `str`, MD5 hash of the file to remove
        :param fields: list of keys to be included in the response

        :returns: :any:`OperationLinkObject` or `None`
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources"
    method = "DELETE"
    success_codes = {202, 204}

    def __init__(self,
                 session: "requests.Session",
                 path: str,
                 permanently: bool = False,
                 md5: Optional[str] = None,
                 force_async: bool = False,
                 fields: Optional[Fields] = None, **kwargs):
        APIRequest.__init__(self, session, {"path":        path,
                                            "permanently": permanently,
                                            "md5":         md5,
                                            "force_async": force_async,
                                            "fields":      fields}, **kwargs)

    def process_args(self,
                     path: str,
                     permanently: bool,
                     md5: Optional[str],
                     force_async: bool,
                     fields: Optional[Fields]) -> None:
        self.params["path"] = ensure_path_has_schema(path)
        self.params["permanently"] = "true" if permanently else "false"
        self.params["force_async"] = "true" if force_async else "false"

        if md5 is not None:
            self.params["md5"] = md5

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self,
                     js: Optional[dict],
                     yadisk: Optional["YaDisk"] = None) -> Optional[OperationLinkObject]:
        if js is not None:
            return OperationLinkObject(js, yadisk)

class SaveToDiskRequest(APIRequest):
    """
        A request to save a public resource to the disk.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param public_key: public key or public URL of the resource
        :param name: filename of the saved resource
        :param path: path to the copied resource in the public folder
        :param save_path: path to the destination directory (downloads directory by default)
        :param force_async: forces the operation to be executed asynchronously
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceLinkObject` or :any:`OperationLinkObject`
    """

    url = "https://cloud-api.yandex.net/v1/disk/public/resources/save-to-disk"
    method = "POST"
    success_codes = {201, 202}

    def __init__(self,
                 session: "requests.Session",
                 public_key: str,
                 name: Optional[str] = None,
                 path: Optional[str] = None,
                 save_path: Optional[str] = None,
                 force_async: bool = False,
                 fields: Optional[Fields] = None, **kwargs):
        APIRequest.__init__(self, session, {"public_key":  public_key,
                                            "name":        name,
                                            "path":        path,
                                            "save_path":   save_path,
                                            "force_async": force_async,
                                            "fields":      fields}, **kwargs)

    def process_args(self,
                     public_key: str,
                     name: Optional[str],
                     path: Optional[str],
                     save_path: Optional[str],
                     force_async: bool,
                     fields: Optional[Fields]) -> None:
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

    def process_json(self,
                     js: Optional[dict],
                     yadisk: Optional["YaDisk"] = None) -> Union[OperationLinkObject, ResourceLinkObject]:
        if js is None:
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        if is_operation_link(js.get("href", "")):
            return OperationLinkObject(js, yadisk)

        return ResourceLinkObject(js, yadisk)

class GetPublicMetaRequest(APIRequest):
    """
        A request to get meta-information about a public resource.

        :param session: an instance of :any:`requests.Session` with prepared headers
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

    url = "https://cloud-api.yandex.net/v1/disk/public/resources"
    method = "GET"

    def __init__(self,
                 session: "requests.Session",
                 public_key: str,
                 offset: int = 0,
                 limit: int = 20,
                 path: Optional[str] = None,
                 sort: Optional[str] = None,
                 preview_size: Optional[str] = None,
                 preview_crop: Optional[bool] = None,
                 fields: Optional[Fields] = None, **kwargs):
        APIRequest.__init__(self, session, {"public_key":   public_key,
                                            "offset":       offset,
                                            "limit":        limit,
                                            "path":         path,
                                            "sort":         sort,
                                            "preview_size": preview_size,
                                            "preview_crop": preview_crop,
                                            "fields":       fields}, **kwargs)

    def process_args(self,
                     public_key: str,
                     offset: int,
                     limit: int,
                     path: Optional[str],
                     sort: Optional[str],
                     preview_size: Optional[str],
                     preview_crop: Optional[bool],
                     fields: Optional[Fields]) -> None:
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
            self.params["preview_crop"] = preview_crop

        if fields is not None:
            sub_map = {"embedded": "_embedded",
                       "view_count": "views_count"}

            self.params["fields"] = ",".join(_substitute_keys(fields, sub_map))

    def process_json(self,
                     js: Optional[dict],
                     yadisk: Optional["YaDisk"] = None) -> PublicResourceObject:
        if js is None:
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        return PublicResourceObject(js, yadisk)

class GetPublicDownloadLinkRequest(APIRequest):
    """
        A request to get a download link for a public resource.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param public_key: public key or public URL of the resource
        :param path: relative path to the resource within the public folder
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceDownloadLinkObject`
    """

    url = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
    method = "GET"

    def __init__(self,
                 session: "requests.Session",
                 public_key: str,
                 path: Optional[str] = None,
                 fields: Optional[Fields] = None, **kwargs):
        APIRequest.__init__(self, session, {"public_key": public_key,
                                            "path":       path,
                                            "fields":     fields}, **kwargs)

    def process_args(self,
                     public_key: str,
                     path: Optional[str],
                     fields: Optional[Fields]) -> None:
        self.params["public_key"] = public_key

        if path is not None:
            self.params["path"] = path;

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self,
                     js: Optional[dict],
                     yadisk: Optional["YaDisk"] = None) -> ResourceDownloadLinkObject:
        if js is None:
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        return ResourceDownloadLinkObject(js, yadisk)

class MoveRequest(APIRequest):
    """
        A request to move a resource.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param src_path: source path to be moved
        :param dst_path: destination path
        :param force_async: forces the operation to be executed asynchronously
        :param overwrite: `bool`, determines whether to overwrite the destination
        :param fields: list of keys to be included in the response

        :returns: :any:`OperationLinkObject` or :any:`ResourceLinkObject`
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources/move"
    method = "POST"
    success_codes = {201, 202}

    def __init__(self,
                 session: "requests.Session",
                 src_path: str,
                 dst_path: str,
                 force_async: bool = False,
                 overwrite: bool = False,
                 fields: Optional[Fields] = None, **kwargs):
        APIRequest.__init__(self, session, {"src_path":    src_path,
                                            "dst_path":    dst_path,
                                            "force_async": force_async,
                                            "overwrite":   overwrite,
                                            "fields":      fields}, **kwargs)

    def process_args(self,
                     src_path: str,
                     dst_path: str,
                     force_async: bool,
                     overwrite: bool,
                     fields: Optional[Fields]) -> None:
        self.params["from"] = ensure_path_has_schema(src_path)
        self.params["path"] = ensure_path_has_schema(dst_path)
        self.params["overwrite"] = "true" if overwrite else "false"
        self.params["force_async"] = "true" if force_async else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self,
                     js: Optional[dict],
                     yadisk: Optional["YaDisk"] = None) -> Union[OperationLinkObject, ResourceLinkObject]:
        if js is None:
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        if is_operation_link(js.get("href", "")):
            return OperationLinkObject(js, yadisk)

        return ResourceLinkObject(js, yadisk)

class FilesRequest(APIRequest):
    """
        A request to get a flat list of all files (that doesn't include directories).

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param offset: offset from the beginning of the list
        :param limit: number of list elements to be included
        :param media_type: type of files to include in the list
        :param sort: `str`, field to be used as a key to sort children resources
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param fields: list of keys to be included in the response

        :returns: :any:`FilesResourceListObject`
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources/files"
    method = "GET"

    def __init__(self,
                 session: "requests.Session",
                 offset: int = 0,
                 limit: int = 20,
                 media_type: Optional[Union[str, Iterable[str]]] = None,
                 preview_size: Optional[str] = None,
                 preview_crop: Optional[bool] = None,
                 sort: Optional[str] = None,
                 fields: Optional[Fields] = None, **kwargs):
        APIRequest.__init__(self, session, {"offset":       offset,
                                            "limit":        limit,
                                            "media_type":   media_type,
                                            "sort":         sort,
                                            "preview_size": preview_size,
                                            "preview_crop": preview_crop,
                                            "fields":       fields}, **kwargs)

    def process_args(self,
                     offset: int,
                     limit: int,
                     media_type: Optional[Union[str, Iterable[str]]],
                     sort: Optional[str],
                     preview_size: Optional[str],
                     preview_crop: Optional[bool],
                     fields: Optional[Fields]) -> None:
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
            self.params["preview_crop"] = preview_crop

        if sort is not None:
            self.params["sort"] = sort

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self,
                     js: Optional[dict],
                     yadisk: Optional["YaDisk"] = None) -> FilesResourceListObject:
        if js is None:
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        return FilesResourceListObject(js, yadisk)

class PatchRequest(APIRequest):
    """
        A request to update custom properties of a resource.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the resource
        :param properties: `dict`, custom properties to update
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceObject`
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources"
    method = "PATCH"
    content_type = "application/json"

    def __init__(self,
                 session: "requests.Session",
                 path: str,
                 properties: dict,
                 fields: Optional[Fields] = None, **kwargs):
        APIRequest.__init__(self, session, {"path":       path,
                                            "properties": properties,
                                            "fields":     fields}, **kwargs)
    def prepare(self, *args, **kwargs) -> None:
        APIRequest.prepare(self, *args, **kwargs)

        assert self.request is not None

        self.request.body = self.data["body"]
        self.request.headers["Content-Length"] = str(len(self.request.body))

    def process_args(self, path: str, properties: dict, fields: Optional[Fields]) -> None:
        self.params["path"] = ensure_path_has_schema(path)
        self.data["body"] = json.dumps({"custom_properties": properties}).encode("utf8")

        if fields is not None:
            sub_map = {"embedded": "_embedded"}

            self.params["fields"] = ",".join(_substitute_keys(fields, sub_map))

    def process_json(self,
                     js: Optional[dict],
                     yadisk: Optional["YaDisk"] = None) -> ResourceObject:
        if js is None:
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        return ResourceObject(js, yadisk)
