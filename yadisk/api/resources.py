#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections
import json

from .APIRequest import APIRequest
from ..objects import LinkObject, PublicResourcesListObject, TrashResourceObject
from ..objects import FilesResourceListObject, LastUploadedResourceListObject
from ..objects import ResourceObject, ResourceUploadLinkObject

__all__ = ["GetPublicResourcesRequest", "UnpublishRequest", "GetDownloadLinkRequest",
           "GetTrashRequest", "RestoreTrashRequest", "DeleteTrashRequest",
           "LastUploadedRequest", "CopyRequest", "GetMetaRequest", "GetUploadLinkRequest",
           "MkdirRequest", "PublishRequest", "UploadURLRequest", "DeleteRequest",
           "SaveToDiskRequest", "GetPublicMetaRequest", "GetPublicDownloadLinkRequest",
           "MoveRequest", "FilesRequest", "PatchRequest"]

class GetPublicResourcesRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/resources/public"
    method = "GET"

    def __init__(self, session, offset=0, limit=20, preview_size=None,
                 preview_crop=None, type=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"offset":       offset,
                                            "limit":        limit,
                                            "preview_size": preview_size,
                                            "preview_crop": preview_crop,
                                            "type":         type}, *args, **kwargs)

    def process_args(self, offset, limit, preview_size, preview_crop, type):
        self.params["offset"] = offset
        self.params["limit"] = limit

        if preview_size is not None:
            self.params["preview_size"] = preview_size

        if preview_crop is not None:
            self.params["preview_crop"] = preview_crop

        if type is not None:
            self.params["type"] = type

    def process_json(self, js):
        return PublicResourcesListObject(js)

class UnpublishRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/resources/unpublish"
    method = "PUT"

    def __init__(self, session, path, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"path":   path,
                                            "fields": fields}, *args, **kwargs)

    def process_args(self, path, fields):
        self.params["path"] = path

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return LinkObject(js)

class GetDownloadLinkRequest(APIRequest):
    """
        A request to get a download link to a resource.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the resource to be downloaded
        :param fields: list of keys to be included in the response
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources/download"
    method = "GET"

    def __init__(self, session, path, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"path": path, "fields": fields},
                            *args, **kwargs)

    def process_args(self, path, fields):
        self.params["path"] = path

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return LinkObject(js)

class GetTrashRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/trash/resources"
    method = "GET"

    def __init__(self, session, path=None, offset=0, limit=20, sort=None,
                 preview_size=None, preview_crop=None, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"path":         path,
                                            "offset":       offset,
                                            "limit":        limit,
                                            "sort":         sort,
                                            "preview_size": preview_size,
                                            "preview_crop": preview_crop,
                                            "fields":       fields}, *args, **kwargs)

    def process_args(self, path, offset, limit, sort, preview_size, preview_crop, fields):
        self.params["path"] = path
        self.params["offset"] = offset
        self.params["limit"] = limit

        if sort is not None:
            self.params["sort"] = sort

        if preview_size is not None:
            self.params["preview_size"] = preview_size

        if preview_crop is not None:
            self.params["preview_crop"] = preview_crop

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return TrashResourceObject(js)

class RestoreTrashRequest(APIRequest):
    """
        A request to restore trash.

        :param session: an instance of `requests.Session` with prepared headers
        :param dst_path: destination
        :param path: path to the trash resource to be restored
        :param overwrite: `bool`, determines whether the destination can be overwritten
        :param fields: list of keys to be included in the response
    """

    url = "https://cloud-api.yandex.net/v1/disk/trash/resources/restore"
    method = "PUT"
    success_codes = {201, 202}

    def __init__(self, session, path, dst_path=None, overwrite=False, fields=None,
                 *args, **kwargs):
        APIRequest.__init__(self, session, {"path":      path,
                                            "dst_path":  dst_path,
                                            "overwrite": overwrite,
                                            "fields":    fields}, *args, **kwargs)

    def process_args(self, path, dst_path, overwrite, fields):
        self.params["path"] = path
        self.params["overwrite"] = "true" if overwrite else "false"

        if dst_path is not None:
            self.params["name"] = dst_path

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return LinkObject(js)

class DeleteTrashRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/trash/resources"
    method = "DELETE"
    success_codes = {202, 204}

    def __init__(self, session, path=None, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"path":   path,
                                            "fields": fields}, *args, **kwargs)

    def process_args(self, path, fields):
        if path is not None:
            self.params["path"] = path

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return LinkObject(js)

class LastUploadedRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/resources/last-uploaded"
    method = "GET"

    def __init__(self, session, limit=20, media_type=None, preview_size=None,
                 preview_crop=None, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"limit":        limit,
                                            "media_type":   media_type,
                                            "preview_size": preview_size,
                                            "preview_crop": preview_crop,
                                            "fields":       fields}, *args, **kwargs)

    def process_args(self, limit, media_type, preview_size, preview_crop, fields):
        self.params["limit"] = limit

        if media_type is not None:
            if not isinstance(media_type, collections.Iterable):
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

    def process_json(self, js):
        return LastUploadedResourceListObject(js)

class CopyRequest(APIRequest):
    """
        A request to copy a file or a directory.

        :param session: an instance of `requests.Session` with prepared headers
        :param src_path: source path
        :param dst_path: destination path
        :param overwrite: if `True` the destination path can be overwritten,
                          otherwise, an error will be raised
        :param fields: list of keys to be included in the response
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources/copy"
    method = "POST"
    success_codes = {201, 202}

    def __init__(self, session, src_path, dst_path, overwrite=False,
                 fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"src_path":  src_path,
                                            "dst_path":  dst_path,
                                            "overwrite": overwrite,
                                            "fields":    fields}, *args, **kwargs)

    def process_args(self, src_path, dst_path, overwrite, fields):
        self.params["from"] = src_path
        self.params["path"] = dst_path
        self.params["overwrite"] = "true" if overwrite else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return LinkObject(js)

class GetMetaRequest(APIRequest):
    """
        A request to get meta-information about a resource.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the resource
        :param limit: number of children resources to be included in the response
        :param offset: number of children resources to be skipped in the response
        :param preview_size: size of the file preview
        :param preview_crop: cut the preview to the size specified in the `preview_size`
        :param fields: list of keys to be included in the response
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources"
    method = "GET"

    def __init__(self, session, path, limit=None, offset=None,
                 preview_size=None, preview_crop=None, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session,
                            {"path":         path,
                             "limit":        limit,
                             "offset":       offset,
                             "preview_size": preview_size,
                             "preview_crop": preview_crop,
                             "fields":       fields}, *args, **kwargs)

    def process_args(self, path, limit, offset, preview_size, preview_crop, fields):
        self.params["path"] = path

        if limit is not None:
            self.params["limit"] = limit

        if offset is not None:
            self.params["offset"] = offset

        if preview_size is not None:
            self.params["preview_size"] = preview_size

        if preview_crop is not None:
            self.params["preview_crop"] = "true" if preview_crop else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return ResourceObject(js)

class GetUploadLinkRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    method = "GET"

    def __init__(self, session, path, overwrite=False, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"path":      path,
                                            "overwrite": overwrite,
                                            "fields":    fields}, *args, **kwargs)

    def process_args(self, path, overwrite, fields):
        self.params["path"] = path
        self.params["overwrite"] = "true" if overwrite else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return ResourceUploadLinkObject(js)

class MkdirRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    method = "PUT"
    success_codes = {201}

    def __init__(self, session, path, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"path": path, "fields": fields},
                            *args, **kwargs)

    def process_args(self, path, fields):
        self.params["path"] = path

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return LinkObject(js)

class PublishRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/resources/publish"
    method = "PUT"

    def __init__(self, session, path, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"path":   path,
                                            "fields": fields}, *args, **kwargs)

    def process_args(self, path, fields):
        self.params["path"] = path

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return LinkObject(js)

class UploadURLRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    method = "POST"
    success_codes = {202}

    def __init__(self, session, path, url, disable_redirects=False, fields=None,
                 *args, **kwargs):
        APIRequest.__init__(self, session, {"path":              path,
                                            "url":               url,
                                            "disable_redirects": disable_redirects,
                                            "fields":            fields}, *args, **kwargs)

    def process_args(self, path, url, disable_redirects, fields):
        self.params["path"] = path
        self.params["url"] = url
        self.params["disable_redirects"] = "true" if disable_redirects else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return LinkObject(js)

class DeleteRequest(APIRequest):
    """
        A request to delete a file or a directory.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the resource to be removed
        :param permanently: if `True`, the resource will be removed permanently,
                            otherwise, it will be just moved to the trash
        :param fields: list of keys to be included in the response
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources"
    method = "DELETE"
    success_codes = {202, 204}

    def __init__(self, session, path, permanently=False, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"path":        path,
                                            "permanently": permanently,
                                            "fields":      fields}, *args, **kwargs)

    def process_args(self, path, permanently, fields):
        self.params["path"] = path
        self.params["permanently"] = "true" if permanently else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        if js is not None:
            return LinkObject(js)

class SaveToDiskRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/public/resources/save-to-disk"
    method = "POST"
    success_codes = {201, 202}

    def __init__(self, session, public_key, name=None, path=None,
                 save_path=None, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"public_key": public_key,
                                            "name":       name,
                                            "path":       path,
                                            "save_path":  save_path,
                                            "fields":     fields}, *args, **kwargs)

    def process_args(self, public_key, name, path, save_path, fields):
        self.params["public_key"] = public_key
        
        if name is not None:
            self.params["name"] = name

        if path is not None:
            self.params["path"] = path

        if save_path is not None:
            self.params["save_path"] = save_path

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return LinkObject(js)

class GetPublicMetaRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/public/resources"
    method = "GET"

    def __init__(self, session, public_key, offset=0, limit=20, path=None,
                 sort=None, preview_size=None, preview_crop=None, fields=None,
                 *args, **kwargs):
        APIRequest.__init__(self, session, {"public_key":   public_key,
                                            "offset":       offset,
                                            "limit":        limit,
                                            "path":         path,
                                            "sort":         sort,
                                            "preview_size": preview_size,
                                            "preview_crop": preview_crop,
                                            "fields":       fields}, *args, **kwargs)

    def process_args(self, public_key, offset, limit, path,
                     sort, preview_size, preview_crop, fields):
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
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return LinkObject(js)

class GetPublicDownloadLinkRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
    method = "GET"

    def __init__(self, session, public_key, path=None, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"public_key":   public_key,
                                            "path":         path,
                                            "fields":       fields}, *args, **kwargs)

    def process_args(self, public_key, path, fields):
        self.params["public_key"] = public_key
        
        if path is not None:
            self.params["path"] = path

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return LinkObject(js)

class MoveRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/move"
    method = "POST"
    success_codes = {201, 202}

    def __init__(self, session, src_path, dst_path, overwrite=False, fields=None,
                 *args, **kwargs):
        APIRequest.__init__(self, session, {"src_path":  src_path,
                                            "dst_path":  dst_path,
                                            "overwrite": overwrite,
                                            "fields":    fields}, *args, **kwargs)

    def process_args(self, src_path, dst_path, overwrite, fields):
        self.params["from"] = src_path
        self.params["path"] = dst_path
        self.params["overwrite"] = "true" if overwrite else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return LinkObject(js)

class FilesRequest(APIRequest):
    """
        A request to get a flat list of all files (that doesn't include directories).

        :param session: an instance of `requests.Session` with prepared headers
        :param offset: offset from the beginning of the list
        :param limit: number of list elements to be included
        :param media_type: type of files to include in the list
        :param sort: sort type
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources/files"
    method = "GET"

    def __init__(self, session, offset=0, limit=20, media_type=None,
                 preview_size=None, preview_crop=None, sort=None, fields=None,
                 *args, **kwargs):
        APIRequest.__init__(self, session, {"offset":       offset,
                                            "limit":        limit,
                                            "media_type":   media_type,
                                            "sort":         sort,
                                            "preview_size": preview_size,
                                            "preview_crop": preview_crop,
                                            "fields":       fields}, *args, **kwargs)

    def process_args(self, offset, limit, media_type, sort, preview_size, preview_crop, fields):
        self.params["offset"] = offset
        self.params["limit"] = limit

        if media_type is not None:
            if not isinstance(media_type, collections.Iterable):
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

    def process_json(self, js):
        return FilesResourceListObject(js)

class PatchRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    method = "PATCH"

    def __init__(self, session, path, body, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"path":   path,
                                            "body":   body,
                                            "fields": fields}, *args, **kwargs)

    def process_args(self, path, body, fields):
        self.params["path"] = path
        self.params["body"] = json.dumps(body)

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return ResourceObject(js)
