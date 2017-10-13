#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

import requests

from ..api import CopyRequest, GetDownloadLinkRequest, GetMetaRequest, APIRequest
from ..api import GetUploadLinkRequest, MkdirRequest, DeleteRequest, GetTrashRequest
from ..api import RestoreTrashRequest, MoveRequest, DeleteTrashRequest
from ..exceptions import DiskNotFoundError

__all__ = ["copy", "download", "exists", "get_download_link", "get_meta", "get_type",
           "get_upload_link", "is_dir", "is_file", "listdir", "mkdir", "remove",
           "upload", "get_trash_meta", "trash_exists", "restore_trash", "move",
           "remove_trash"]

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

        :returns: `LinkObject`
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

def exists(session, path, *args, **kwargs):
    """
        Check whether `path` exists.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the resource

        :returns: `bool`
    """

    try:
        get_meta(session, path, *args, **kwargs)

        return True
    except DiskNotFoundError:
        return False

def get_download_link(session, path, *args, **kwargs):
    """
        Get a download link for a file (or a directory).

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the resource
        :param fields: list of keys to be included in the response

        :returns: `LinkObject`
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
        :param preview_crop: cut the preview to the size specified in the `preview_size`
        :param fields: list of keys to be included in the response

        :returns: `ResourceObject`
    """

    request = GetMetaRequest(session, *args, **kwargs)
    request.send()

    return request.process()

def get_type(session, path, *args, **kwargs):
    """
        Get resource type.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the resource

        :returns: "file" or "dir"
    """

    return get_meta(session, path, *args, **kwargs).type

def get_upload_link(session, path, *args, **kwargs):
    """
        Get a link to upload the file to.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: destination path
        :param overwrite: `bool`, determines whether to overwrite the destination
        :param fields: list of keys to be included in the response

        :returns: `LinkObject`
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

def listdir(session, path, *args, **kwargs):
    """
        Get contents of `path`.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the directory

        :returns: generator of `ResourceObject`s.
    """

    result = get_meta(session, path, *args, **kwargs)

    if result.type == "file":
        raise NotADirectoryError("%r is a file" % (path,))

    for child in result.embedded.items:
        yield child

    offset = result.embedded.offset
    limit = result.embedded.limit
    total = result.embedded.total

    while offset + limit < total:
        result = get_meta(session, path, *args, offset=offset, limit=limit, **kwargs)

        for child in result.embedded.items:
            yield child

        offset += limit
        limit = result.embedded.limit
        total = result.embedded.total

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

def upload(session, file_or_path, dst_path, overwrite=False, fields=None, *args, **kwargs):
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

    link = get_upload_link(session, dst_path, overwrite=overwrite, fields=fields, *args, **kwargs)

    kwargs = dict(kwargs)
    kwargs.setdefault("timeout", (APIRequest.timeout[0], 60))
    n_retries = kwargs.get("n_retries", APIRequest.n_retries)
    retry_interval = kwargs.get("retry_interval", 3.0)

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
                response = requests.put(link, data=file, stream=True, *args, **kwargs)
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
        :param preview_crop: cut the preview to the size specified in the `preview_size`
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

    try:
        get_trash_meta(session, path, *args, **kwargs)
        return True
    except DiskNotFoundError:
        return False

def restore_trash(session, path, *args, **kwargs):
    """
        Restore a trash resource.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the trash resource to be restored
        :param dst_path: destination path
        :param overwrite: `bool`, determines whether the destination can be overwritten
        :param fields: list of keys to be included in the response

        :returns: `LinkObject`
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

        :returns: `LinkObject` if the operation is performed asynchronously, `None` otherwise
    """

    request = DeleteTrashRequest(session, path, *args, **kwargs)
    request.send()

    return request.process()
