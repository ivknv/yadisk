#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

import requests

from ..api import CopyRequest, GetDownloadLinkRequest, GetMetaRequest, APIRequest
from ..api import GetUploadLinkRequest, MkdirRequest, DeleteRequest, GetTrashRequest
from ..api import RestoreTrashRequest, MoveRequest, DeleteTrashRequest
from ..api import PublishRequest, UnpublishRequest, SaveToDiskRequest, GetPublicMetaRequest
from ..api import GetPublicResourcesRequest, PatchRequest, FilesRequest
from ..api import LastUploadedRequest, UploadURLRequest, GetPublicDownloadLinkRequest
from ..exceptions import DiskNotFoundError

from .. import settings

__all__ = ["copy", "download", "exists", "get_download_link", "get_meta", "get_type",
           "get_upload_link", "is_dir", "is_file", "listdir", "mkdir", "remove",
           "upload", "get_trash_meta", "trash_exists", "restore_trash", "move",
           "remove_trash", "publish", "unpublish", "save_to_disk", "get_public_meta",
           "public_exists", "public_listdir", "get_public_type", "is_public_dir",
           "is_public_file", "trash_listdir", "get_trash_type", "is_trash_dir",
           "is_trash_file", "get_public_resources", "patch", "get_files",
           "get_last_uploaded", "upload_url", "get_public_download_link", "download_public"]

def copy(session, src_path, dst_path, *args, **kwargs):
    """
        Copy `src_path` to `dst_path`.
        If the operation is performed asynchronously, returns the link to the operation,
        otherwise, returns the link to the newly created resource.

        :param session: an instance of `requests.Session` with prepared headers
        :param src_path: source path
        :param dst_path: destination path
        :param overwrite: if `True` the destination path can be overwritten,
                          otherwise, an error will be raised
        :param fields: list of keys to be included in the response

        :returns: `LinkObject` or `OperationLinkObject`
    """

    request = CopyRequest(session, src_path, dst_path, *args, **kwargs)

    request.send()

    return request.process()

def download(session, src_path, file_or_path, *args, **kwargs):
    """
        Download the file.

        :param session: an instance of `requests.Session` with prepared headers
        :param src_path: source path
        :param path_or_file: destination path or file-like object

        :returns: `True` if the download succeeded, `False` otherwise
    """

    link = get_download_link(session, src_path, *args, **kwargs)

    n_retries = kwargs.get("n_retries") or settings.DEFAULT_N_RETRIES

    if isinstance(file_or_path, (str, bytes)):
        file = open(file_or_path, "wb")
        close_file = True
    else:
        file = file_or_path
        close_file = False

    file_position = file.tell()

    try:
        for i in range(n_retries + 1):
            file.seek(file_position)

            try:
                response = requests.get(link, data=file, *args, **kwargs)

                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)

            except requests.exceptions.RequestException as e:
                if i == n_retries:
                    raise e

                continue

            if response.status_code in APIRequest.retry_codes:
                continue

            break
    finally:
        if close_file:
            file.close()

    return response.status_code == 200

def _exists(get_meta_function, *args, **kwargs):
    try:
        get_meta_function(*args, limit=0, **kwargs)

        return True
    except DiskNotFoundError:
        return False

def exists(session, path, *args, **kwargs):
    """
        Check whether `path` exists.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the resource

        :returns: `bool`
    """

    return _exists(get_meta, session, path, *args, **kwargs)

def get_download_link(session, path, *args, **kwargs):
    """
        Get a download link for a file (or a directory).

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the resource
        :param fields: list of keys to be included in the response

        :returns: `str`
    """

    request = GetDownloadLinkRequest(session, path, *args, **kwargs)
    request.send()

    return request.process().href

def get_meta(session, *args, **kwargs):
    """
        Get meta information about a file/directory.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the resource
        :param limit: number of children resources to be included in the response
        :param offset: number of children resources to be skipped in the response
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param fields: list of keys to be included in the response

        :returns: `ResourceObject`
    """

    request = GetMetaRequest(session, *args, **kwargs)
    request.send()

    return request.process()

def _get_type(get_meta_function, session, *args, **kwargs):
    return get_meta_function(session, *args, limit=0, **kwargs).type

def get_type(session, path, *args, **kwargs):
    """
        Get resource type.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the resource

        :returns: "file" or "dir"
    """

    return _get_type(get_meta, session, path, *args, **kwargs)

def get_upload_link(session, path, *args, **kwargs):
    """
        Get a link to upload the file using the PUT request.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: destination path
        :param overwrite: `bool`, determines whether to overwrite the destination
        :param fields: list of keys to be included in the response

        :returns: `str`
    """

    request = GetUploadLinkRequest(session, path, *args, **kwargs)
    request.send()

    return request.process().href

def is_dir(session, path, *args, **kwargs):
    """
        Check whether `path` is a directory.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the resource

        :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
    """

    try:
        return get_type(session, path, *args, **kwargs) == "dir"
    except DiskNotFoundError:
        return False

def is_file(session, path, *args, **kwargs):
    """
        Check whether `path` is a file.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the resource

        :returns: `True` if `path` is a file, `False` otherwise (even if it doesn't exist)
    """

    try:
        return get_type(session, path, *args, **kwargs) == "file"
    except DiskNotFoundError:
        return False

def _listdir(get_meta_function, session, path, *args, **kwargs):
    kwargs = dict(kwargs)
    kwargs.setdefault("limit", 10000)

    result = get_meta_function(session, path, *args, **kwargs)

    if result.type == "file":
        raise NotADirectoryError("%r is a file" % (path,))

    for child in result.embedded.items:
        yield child

    limit = result.embedded.limit
    offset = result.embedded.offset
    total = result.embedded.total

    while offset + limit < total:
        offset += limit
        kwargs["offset"] = offset
        result = get_meta_function(session, path, *args, **kwargs)

        for child in result.embedded.items:
            yield child

        limit = result.embedded.limit
        total = result.embedded.total

def listdir(session, path, *args, **kwargs):
    """
        Get contents of `path`.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the directory
        :param limit: number of children resources to be included in the response
        :param offset: number of children resources to be skipped in the response
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param fields: list of keys to be included in the response

        :returns: generator of `ResourceObject`
    """

    return _listdir(get_meta, session, path, *args, **kwargs)

def mkdir(session, path, *args, **kwargs):
    """
        Create a new directory.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the directory to be created
        :param fields: list of keys to be included in the response

        :returns: `LinkObject`
    """

    request = MkdirRequest(session, path, *args, **kwargs)

    request.send()

    return request.process()

def remove(session, path, *args, **kwargs):
    """
        Remove the resource.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the resource to be removed
        :param permanently: if `True`, the resource will be removed permanently,
                            otherwise, it will be just moved to the trash
        :param fields: list of keys to be included in the response

        :returns: `LinkObject` if the operation is performed asynchronously, `None` otherwise
    """

    request = DeleteRequest(session, path, *args, **kwargs)

    request.send()

    return request.process()

def upload(session, file_or_path, dst_path, overwrite=False, fields=None,
           timeout=None, retry_interval=None, *args, **kwargs):
    """
        Upload a file to disk.

        :param session: an instance of `requests.Session` with prepared headers
        :param path_or_file: path or file-like object to be uploaded
        :param dst_path: destination path
        :param overwrite: if `True`, the resource will be overwritten if it already exists,
                          an error will be raised otherwise
        :param fields: list of keys to be included in the response

        :returns: `True` if the upload succeeded, `False` otherwise
    """

    timeout = timeout or settings.DEFAULT_UPLOAD_TIMEOUT

    retry_interval = retry_interval or settings.DEFAULT_UPLOAD_RETRY_INTERVAL

    link = get_upload_link(session, dst_path, overwrite=overwrite, fields=fields,
                           timeout=timeout, retry_interval=retry_interval, *args, **kwargs)

    n_retries = kwargs.get("n_retries") or settings.DEFAULT_N_RETRIES

    if isinstance(file_or_path, (str, bytes)):
        file = open(file_or_path, "rb")
        close_file = True
    else:
        file = file_or_path
        close_file = False

    file_position = file.tell()

    try:
        for i in range(n_retries + 1):
            file.seek(file_position)

            if i > 0:
                time.sleep(retry_interval)

            try:
                response = requests.put(link, data=file, stream=True, timeout=timeout, *args, **kwargs)
            except requests.exceptions.RequestException as e:
                if i == n_retries:
                    raise e

                continue

            if response.status_code in APIRequest.retry_codes:
                continue

            break
    finally:
        if close_file:
            file.close()

    return response.status_code == 201

def get_trash_meta(session, path, *args, **kwargs):
    """
        Get meta information about a trash resource.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the trash resource
        :param limit: number of children resources to be included in the response
        :param offset: number of children resources to be skipped in the response
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param fields: list of keys to be included in the response

        :returns: `TrashResourceObject`
    """

    request = GetTrashRequest(session, path, *args, **kwargs)

    request.send()

    return request.process()

def trash_exists(session, path, *args, **kwargs):
    """
        Check whether the trash resource at `path` exists.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the trash resource

        :returns: `bool`
    """

    return _exists(get_trash_meta, session, path, *args, **kwargs)

def restore_trash(session, path, *args, **kwargs):
    """
        Restore a trash resource.
        Returns a link to the newly created resource or a link to the asynchronous operation.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the trash resource to be restored
        :param dst_path: destination path
        :param overwrite: `bool`, determines whether the destination can be overwritten
        :param fields: list of keys to be included in the response

        :returns: `LinkObject` or `OperationLinkObject`
    """

    request = RestoreTrashRequest(session, path, *args, **kwargs)
    request.send()

    return request.process()

def move(session, src_path, dst_path, *args, **kwargs):
    """
        Move `src_path` to `dst_path`.

        :param session: an instance of `requests.Session` with prepared headers
        :param src_path: source path to be moved
        :param dst_path: destination path
        :param overwrite: `bool`, determines whether to overwrite the destination
        :param fields: list of keys to be included in the response

        :returns: `LinkObject`
    """

    request = MoveRequest(session, src_path, dst_path, *args, **kwargs)
    request.send()

    return request.process()

def remove_trash(session, path, *args, **kwargs):
    """
        Remove a trash resource.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the trash resource to be deleted
        :param fields: list of keys to be included in the response

        :returns: `OperationLinkObject` if the operation is performed asynchronously, `None` otherwise
    """

    request = DeleteTrashRequest(session, path, *args, **kwargs)
    request.send()

    return request.process()

def publish(session, path, *args, **kwargs):
    """
        Make a resource public.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the resource to be published
        :param fields: list of keys to be included in the response

        :returns: `LinkObject`, link to the resource
    """

    request = PublishRequest(session, path, *args, **kwargs)
    request.send()

    return request.process()

def unpublish(session, path, *args, **kwargs):
    """
        Make a public resource private.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the resource to be unpublished
        :param fields: list of keys to be included in the response

        :returns: `LinkObject`
    """

    request = UnpublishRequest(session, path, *args, **kwargs)
    request.send()

    return request.process()

def save_to_disk(session, public_key, *args, **kwargs):
    """
        Saves a public resource to the disk.
        Returns the link to the operation if it's performed asynchronously,
        or a link to the resource otherwise.

        :param session: an instance of `requests.Session` with prepared headers
        :param public_key: public key or public URL of the resource
        :param name: filename of the saved resource
        :param save_path: path to the destination directory (downloads directory by default)
        :param fields: list of keys to be included in the response

        :returns: `LinkObject` or `OperationLinkObject`
    """

    request = SaveToDiskRequest(session, public_key, *args, **kwargs)
    request.send()

    return request.process()

def get_public_meta(session, public_key, *args, **kwargs):
    """
        Get meta-information about a public resource.

        :param session: an instance of `requests.Session` with prepared headers
        :param public_key: public key or public URL of the resource
        :param offset: offset from the beginning of the list of nested resources
        :param limit: maximum number of nested elements to be included in the list
        :param sort: key to sort by
        :param preview_size: file preview size
        :param preview_crop: `bool`, allow preview crop
        :param fields: list of keys to be included in the response

        :returns: `PublicResourceObject`
    """

    request = GetPublicMetaRequest(session, public_key, *args, **kwargs)
    request.send()

    return request.process()

def public_exists(session, public_key, *args, **kwargs):
    """
        Check whether the public resource exists.

        :param session: an instance of `requests.Session` with prepared headers
        :param public_key: public key or public URL of the resource

        :returns: `bool`
    """

    return _exists(get_public_meta, session, public_key, *args, **kwargs)

def public_listdir(session, public_key, *args, **kwargs):
    """
        Get contents of a public directory.

        :param session: an instance of `requests.Session` with prepared headers
        :param public_key: public key or public URL of the resource
        :param limit: number of children resources to be included in the response
        :param offset: number of children resources to be skipped in the response
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param fields: list of keys to be included in the response

        :returns: generator of `PublicResourceObject`
    """

    return _listdir(get_public_meta, session, public_key, *args, **kwargs)

def get_public_type(session, public_key, *args, **kwargs):
    """
        Get public resource type.

        :param session: an instance of `requests.Session` with prepared headers
        :param public_key: public key or public URL of the resource

        :returns: "file" or "dir"
    """

    return _get_type(get_public_meta, session, public_key, *args, **kwargs)

def is_public_dir(session, public_key, *args, **kwargs):
    """
        Check whether `public_key` is a public directory.

        :param session: an instance of `requests.Session` with prepared headers
        :param public_key: public key or public URL of the resource

        :returns: `True` if `public_key` is a directory, `False` otherwise (even if it doesn't exist)
    """

    try:
        return get_public_type(session, public_key, *args, **kwargs) == "dir"
    except DiskNotFoundError:
        return False

def is_public_file(session, public_key, *args, **kwargs):
    """
        Check whether `public_key` is a public file.

        :param session: an instance of `requests.Session` with prepared headers
        :param public_key: public key or public URL of the resource

        :returns: `True` if `public_key` is a file, `False` otherwise (even if it doesn't exist)
    """

    try:
        return get_public_type(session, public_key, *args, **kwargs) == "file"
    except DiskNotFoundError:
        return False

def trash_listdir(session, path, *args, **kwargs):
    """
        Get contents of a trash resource.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the directory in the trash bin
        :param limit: number of children resources to be included in the response
        :param offset: number of children resources to be skipped in the response
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param fields: list of keys to be included in the response

        :returns: generator of `TrashResourceObject`
    """

    return _listdir(get_trash_meta, session, path, *args, **kwargs)

def get_trash_type(session, path, *args, **kwargs):
    """
        Get trash resource type.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the trash resource

        :returns: "file" or "dir"
    """

    return _get_type(get_trash_meta, session, path, *args, **kwargs)

def is_trash_dir(session, path, *args, **kwargs):
    """
        Check whether `path` is a trash directory.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the trash resource

        :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
    """

    try:
        return get_trash_type(session, path, *args, **kwargs) == "dir"
    except DiskNotFoundError:
        return False

def is_trash_file(session, path, *args, **kwargs):
    """
        Check whether `path` is a trash file.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the trash resource

        :returns: `True` if `path` is a file, `False` otherwise (even if it doesn't exist)
    """

    try:
        return get_trash_type(session, path, *args, **kwargs) == "file"
    except DiskNotFoundError:
        return False

def get_public_resources(session, *args, **kwargs):
    """
        Get a list of public resources.

        :param session: an instance of `requests.Session` with prepared headers
        :param offset: offset from the beginning of the list
        :param limit: maximum number of elements in the list
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param type: filter based on type of resources ("file" or "dir")
        :param fields: list of keys to be included in the response

        :returns: `PublicResourcesList`
    """

    request = GetPublicResourcesRequest(session, *args, **kwargs)
    request.send()

    return request.process()

def patch(session, path, properties, *args, **kwargs):
    """
        Update custom properties of a resource.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the resource
        :param properties: `dict`, custom properties to update
        :param fields: list of keys to be included in the response

        :returns: `ResourceObject`
    """

    request = PatchRequest(session, path, properties, *args, **kwargs)
    request.send()

    return request.process()

def get_files(session, *args, **kwargs):
    """
        Get a flat list of all files (that doesn't include directories).

        :param session: an instance of `requests.Session` with prepared headers
        :param offset: offset from the beginning of the list
        :param limit: number of list elements to be included
        :param media_type: type of files to include in the list
        :param sort: sort type

        :returns: generator of `ResourceObject`
    """

    if kwargs.get("limit") is not None:
        request = FilesRequest(session, *args, **kwargs)
        request.send()

        for i in request.process().items:
            yield i

        return

    kwargs = dict(kwargs)

    kwargs.setdefault("offset", 0)
    kwargs["limit"] = 1000

    while True:
        counter = 0
        for i in get_files(session, *args, **kwargs):
            counter += 1
            yield i

        if counter < kwargs["limit"]:
            break

        kwargs["offset"] += kwargs["limit"]

def get_last_uploaded(session, *args, **kwargs):
    """
        Get the list of latest uploaded files sorted by upload date.

        :param session: an instance of `requests.Session` with prepared headers
        :param limit: maximum number of elements in the list
        :param media_type: type of files to include in the list
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param fields: list of keys to be included in the response

        :returns: generator of `LastUploadedResourceListObject`
    """

    request = LastUploadedRequest(session, *args, **kwargs)
    request.send()

    for i in request.process().items:
        yield i

def upload_url(session, url, path, *args, **kwargs):
    """
        Upload a file from URL.

        :param session: an instance of `requests.Session` with prepared headers
        :param url: source URL
        :param path: destination path
        :param disable_redirects: `bool`, forbid redirects
        :param fields: list of keys to be included in the response

        :returns: `OperationLinkObject`, link to the asynchronous operation
    """

    request = UploadURLRequest(session, url, path, *args, **kwargs)
    request.send()

    return request.process()

def get_public_download_link(session, public_key, *args, **kwargs):
    """
        Get a download link for a public resource.

        :param session: an instance of `requests.Session` with prepared headers
        :param public_key: public key or public URL of the resource
        :param fields: list of keys to be included in the response

        :returns: `str`
    """

    request = GetPublicDownloadLinkRequest(session, public_key, *args, **kwargs)
    request.send()

    return request.process().href

def download_public(session, public_key, file_or_path, *args, **kwargs):
    """
        Download the public resource.

        :param session: an instance of `requests.Session` with prepared headers
        :param public_key: public key or public URL of the resource
        :param path_or_file: destination path or file-like object

        :returns: `True` if the download succeeded, `False` otherwise
    """

    link = get_public_download_link(session, public_key, *args, **kwargs)

    n_retries = kwargs.get("n_retries", APIRequest.n_retries)

    if isinstance(file_or_path, (str, bytes)):
        file = open(file_or_path, "wb")
        close_file = True
    else:
        file = file_or_path
        close_file = False

    file_position = file.tell()

    try:
        for i in range(n_retries + 1):
            file.seek(file_position)

            try:
                response = requests.get(link, data=file, *args, **kwargs)

                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)

            except requests.exceptions.RequestException as e:
                if i == n_retries:
                    raise e

                continue

            if response.status_code in APIRequest.retry_codes:
                continue

            break
    finally:
        if close_file:
            file.close()

    return response.status_code == 200
