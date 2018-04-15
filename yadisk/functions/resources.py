#!/usr/bin/env python
# -*- coding: utf-8 -*-

import contextlib

from ..api import CopyRequest, GetDownloadLinkRequest, GetMetaRequest
from ..api import GetUploadLinkRequest, MkdirRequest, DeleteRequest, GetTrashRequest
from ..api import RestoreTrashRequest, MoveRequest, DeleteTrashRequest
from ..api import PublishRequest, UnpublishRequest, SaveToDiskRequest, GetPublicMetaRequest
from ..api import GetPublicResourcesRequest, PatchRequest, FilesRequest
from ..api import LastUploadedRequest, UploadURLRequest, GetPublicDownloadLinkRequest
from ..exceptions import WrongResourceTypeError, PathNotFoundError
from ..utils import auto_retry, get_exception

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

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param src_path: source path
        :param dst_path: destination path
        :param overwrite: if `True` the destination path can be overwritten,
                          otherwise, an error will be raised
        :param force_async: forces the operation to be executed asynchronously
        :param fields: list of keys to be included in the response

        :returns: :any:`LinkObject` or :any:`OperationLinkObject`
    """

    request = CopyRequest(session, src_path, dst_path, *args, **kwargs)

    request.send()

    return request.process()

def download(session, src_path, file_or_path, *args, **kwargs):
    """
        Download the file.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param src_path: source path
        :param path_or_file: destination path or file-like object
    """

    kwargs = dict(kwargs)

    n_retries = kwargs.get("n_retries")

    if n_retries is None:
        n_retries = settings.DEFAULT_N_RETRIES

    retry_interval = kwargs.get("retry_interval")

    if retry_interval is None:
        retry_interval = settings.DEFAULT_RETRY_INTERVAL

    timeout = kwargs.get("timeout")

    if timeout is None:
        timeout = settings.DEFAULT_TIMEOUT

    kwargs["timeout"] = timeout

    file = None
    close_file = False

    try:
        if isinstance(file_or_path, (str, bytes)):
            close_file = True
            file = open(file_or_path, "wb")
        else:
            close_file = False
            file = file_or_path

        file_position = file.tell()

        def attempt():
            temp_kwargs = dict(kwargs)
            temp_kwargs["n_retries"] = 0
            temp_kwargs["retry_interval"] = 0.0
            link = get_download_link(session, src_path, *args, **temp_kwargs)

            # session.get() doesn't accept these parameters
            for k in ("n_retries", "retry_interval", "fields"):
                temp_kwargs.pop(k, None)

            temp_kwargs.setdefault("stream", True)

            # Disable keep-alive by default, since the download server is random
            try:
                temp_kwargs["headers"].setdefault("Connection", "close")
            except KeyError:
                temp_kwargs["headers"] = {"Connection": "close"}

            file.seek(file_position)

            with contextlib.closing(session.get(link, data=file, **temp_kwargs)) as response:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)

                if response.status_code != 200:
                    raise get_exception(response)

        auto_retry(attempt, n_retries, retry_interval)
    finally:
        if close_file and file is not None:
            file.close()

def _exists(get_meta_function, *args, **kwargs):
    try:
        get_meta_function(*args, limit=0, **kwargs)

        return True
    except PathNotFoundError:
        return False

def exists(session, path, *args, **kwargs):
    """
        Check whether `path` exists.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the resource

        :returns: `bool`
    """

    return _exists(get_meta, session, path, *args, **kwargs)

def get_download_link(session, path, *args, **kwargs):
    """
        Get a download link for a file (or a directory).

        :param session: an instance of :any:`requests.Session` with prepared headers
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

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the resource
        :param limit: number of children resources to be included in the response
        :param offset: number of children resources to be skipped in the response
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceObject`
    """

    request = GetMetaRequest(session, *args, **kwargs)
    request.send()

    return request.process()

def _get_type(get_meta_function, session, *args, **kwargs):
    return get_meta_function(session, *args, limit=0, **kwargs).type

def get_type(session, path, *args, **kwargs):
    """
        Get resource type.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the resource

        :returns: "file" or "dir"
    """

    return _get_type(get_meta, session, path, *args, **kwargs)

def get_upload_link(session, path, *args, **kwargs):
    """
        Get a link to upload the file using the PUT request.

        :param session: an instance of :any:`requests.Session` with prepared headers
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

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the resource

        :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
    """

    try:
        return get_type(session, path, *args, **kwargs) == "dir"
    except PathNotFoundError:
        return False

def is_file(session, path, *args, **kwargs):
    """
        Check whether `path` is a file.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the resource

        :returns: `True` if `path` is a file, `False` otherwise (even if it doesn't exist)
    """

    try:
        return get_type(session, path, *args, **kwargs) == "file"
    except PathNotFoundError:
        return False

def _listdir(get_meta_function, session, path, *args, **kwargs):
    kwargs = dict(kwargs)
    kwargs.setdefault("limit", 10000)

    result = get_meta_function(session, path, *args, **kwargs)

    if result.type == "file":
        raise WrongResourceTypeError("%r is a file" % (path,))

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

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the directory
        :param limit: number of children resources to be included in the response
        :param offset: number of children resources to be skipped in the response
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param fields: list of keys to be included in the response

        :returns: generator of :any:`ResourceObject`
    """

    return _listdir(get_meta, session, path, *args, **kwargs)

def mkdir(session, path, *args, **kwargs):
    """
        Create a new directory.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the directory to be created
        :param fields: list of keys to be included in the response

        :returns: :any:`LinkObject`
    """

    request = MkdirRequest(session, path, *args, **kwargs)

    request.send()

    return request.process()

def remove(session, path, *args, **kwargs):
    """
        Remove the resource.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the resource to be removed
        :param permanently: if `True`, the resource will be removed permanently,
                            otherwise, it will be just moved to the trash
        :param force_async: forces the operation to be executed asynchronously
        :param fields: list of keys to be included in the response

        :returns: :any:`LinkObject` if the operation is performed asynchronously, `None` otherwise
    """

    request = DeleteRequest(session, path, *args, **kwargs)

    request.send()

    return request.process()

def upload(session, file_or_path, dst_path, *args, **kwargs):
    """
        Upload a file to disk.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path_or_file: path or file-like object to be uploaded
        :param dst_path: destination path
        :param overwrite: if `True`, the resource will be overwritten if it already exists,
                          an error will be raised otherwise
    """

    kwargs = dict(kwargs)

    timeout = kwargs.get("timeout")

    if timeout is None:
        timeout = settings.DEFAULT_UPLOAD_TIMEOUT

    retry_interval = kwargs.get("retry_interval")

    if retry_interval is None:
        retry_interval = settings.DEFAULT_UPLOAD_RETRY_INTERVAL

    n_retries = kwargs.get("n_retries")

    if n_retries is None:
        n_retries = settings.DEFAULT_N_RETRIES

    kwargs["timeout"] = timeout

    file = None
    close_file = False

    try:
        if isinstance(file_or_path, (str, bytes)):
            close_file = True
            file = open(file_or_path, "rb")
        else:
            close_file = False
            file = file_or_path

        file_position = file.tell()

        def attempt():
            temp_kwargs = dict(kwargs)
            temp_kwargs["n_retries"] = 0
            temp_kwargs["retry_interval"] = 0.0

            link = get_upload_link(session, dst_path, *args, **temp_kwargs)

            # session.put() doesn't accept these parameters
            for k in ("n_retries", "retry_interval", "overwrite", "fields"):
                temp_kwargs.pop(k, None)

            temp_kwargs.setdefault("stream", True)

            # Disable keep-alive by default, since the upload server is random
            try:
                temp_kwargs["headers"].setdefault("Connection", "close")
            except KeyError:
                temp_kwargs["headers"] = {"Connection": "close"}

            file.seek(file_position)

            with contextlib.closing(session.put(link, data=file, **temp_kwargs)) as response:
                if response.status_code != 201:
                    raise get_exception(response)

        auto_retry(attempt, n_retries, retry_interval)
    finally:
        if close_file and file is not None:
            file.close()

def get_trash_meta(session, path, *args, **kwargs):
    """
        Get meta information about a trash resource.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the trash resource
        :param limit: number of children resources to be included in the response
        :param offset: number of children resources to be skipped in the response
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param fields: list of keys to be included in the response

        :returns: :any:`TrashResourceObject`
    """

    request = GetTrashRequest(session, path, *args, **kwargs)

    request.send()

    return request.process()

def trash_exists(session, path, *args, **kwargs):
    """
        Check whether the trash resource at `path` exists.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the trash resource

        :returns: `bool`
    """

    return _exists(get_trash_meta, session, path, *args, **kwargs)

def restore_trash(session, path, *args, **kwargs):
    """
        Restore a trash resource.
        Returns a link to the newly created resource or a link to the asynchronous operation.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the trash resource to be restored
        :param dst_path: destination path
        :param overwrite: `bool`, determines whether the destination can be overwritten
        :param force_async: forces the operation to be executed asynchronously
        :param fields: list of keys to be included in the response

        :returns: :any:`LinkObject` or :any:`OperationLinkObject`
    """

    request = RestoreTrashRequest(session, path, *args, **kwargs)
    request.send()

    return request.process()

def move(session, src_path, dst_path, *args, **kwargs):
    """
        Move `src_path` to `dst_path`.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param src_path: source path to be moved
        :param dst_path: destination path
        :param overwrite: `bool`, determines whether to overwrite the destination
        :param force_async: forces the operation to be executed asynchronously
        :param fields: list of keys to be included in the response

        :returns: :any:`LinkObject` or :any:`OperationLinkObject`
    """

    request = MoveRequest(session, src_path, dst_path, *args, **kwargs)
    request.send()

    return request.process()

def remove_trash(session, path, *args, **kwargs):
    """
        Remove a trash resource.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the trash resource to be deleted
        :param force_async: forces the operation to be executed asynchronously
        :param fields: list of keys to be included in the response

        :returns: :any:`OperationLinkObject` if the operation is performed asynchronously, `None` otherwise
    """

    request = DeleteTrashRequest(session, path, *args, **kwargs)
    request.send()

    return request.process()

def publish(session, path, *args, **kwargs):
    """
        Make a resource public.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the resource to be published
        :param fields: list of keys to be included in the response

        :returns: :any:`LinkObject`, link to the resource
    """

    request = PublishRequest(session, path, *args, **kwargs)
    request.send()

    return request.process()

def unpublish(session, path, *args, **kwargs):
    """
        Make a public resource private.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the resource to be unpublished
        :param fields: list of keys to be included in the response

        :returns: :any:`LinkObject`
    """

    request = UnpublishRequest(session, path, *args, **kwargs)
    request.send()

    return request.process()

def save_to_disk(session, public_key, *args, **kwargs):
    """
        Saves a public resource to the disk.
        Returns the link to the operation if it's performed asynchronously,
        or a link to the resource otherwise.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param public_key: public key or public URL of the resource
        :param name: filename of the saved resource
        :param save_path: path to the destination directory (downloads directory by default)
        :param force_async: forces the operation to be executed asynchronously
        :param fields: list of keys to be included in the response

        :returns: :any:`LinkObject` or :any:`OperationLinkObject`
    """

    request = SaveToDiskRequest(session, public_key, *args, **kwargs)
    request.send()

    return request.process()

def get_public_meta(session, public_key, *args, **kwargs):
    """
        Get meta-information about a public resource.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param public_key: public key or public URL of the resource
        :param offset: offset from the beginning of the list of nested resources
        :param limit: maximum number of nested elements to be included in the list
        :param sort: key to sort by
        :param preview_size: file preview size
        :param preview_crop: `bool`, allow preview crop
        :param fields: list of keys to be included in the response

        :returns: :any:`PublicResourceObject`
    """

    request = GetPublicMetaRequest(session, public_key, *args, **kwargs)
    request.send()

    return request.process()

def public_exists(session, public_key, *args, **kwargs):
    """
        Check whether the public resource exists.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param public_key: public key or public URL of the resource

        :returns: `bool`
    """

    return _exists(get_public_meta, session, public_key, *args, **kwargs)

def public_listdir(session, public_key, *args, **kwargs):
    """
        Get contents of a public directory.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param public_key: public key or public URL of the resource
        :param limit: number of children resources to be included in the response
        :param offset: number of children resources to be skipped in the response
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param fields: list of keys to be included in the response

        :returns: generator of :any:`PublicResourceObject`
    """

    return _listdir(get_public_meta, session, public_key, *args, **kwargs)

def get_public_type(session, public_key, *args, **kwargs):
    """
        Get public resource type.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param public_key: public key or public URL of the resource

        :returns: "file" or "dir"
    """

    return _get_type(get_public_meta, session, public_key, *args, **kwargs)

def is_public_dir(session, public_key, *args, **kwargs):
    """
        Check whether `public_key` is a public directory.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param public_key: public key or public URL of the resource

        :returns: `True` if `public_key` is a directory, `False` otherwise (even if it doesn't exist)
    """

    try:
        return get_public_type(session, public_key, *args, **kwargs) == "dir"
    except PathNotFoundError:
        return False

def is_public_file(session, public_key, *args, **kwargs):
    """
        Check whether `public_key` is a public file.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param public_key: public key or public URL of the resource

        :returns: `True` if `public_key` is a file, `False` otherwise (even if it doesn't exist)
    """

    try:
        return get_public_type(session, public_key, *args, **kwargs) == "file"
    except PathNotFoundError:
        return False

def trash_listdir(session, path, *args, **kwargs):
    """
        Get contents of a trash resource.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the directory in the trash bin
        :param limit: number of children resources to be included in the response
        :param offset: number of children resources to be skipped in the response
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param fields: list of keys to be included in the response

        :returns: generator of :any:`TrashResourceObject`
    """

    return _listdir(get_trash_meta, session, path, *args, **kwargs)

def get_trash_type(session, path, *args, **kwargs):
    """
        Get trash resource type.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the trash resource

        :returns: "file" or "dir"
    """

    return _get_type(get_trash_meta, session, path, *args, **kwargs)

def is_trash_dir(session, path, *args, **kwargs):
    """
        Check whether `path` is a trash directory.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the trash resource

        :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
    """

    try:
        return get_trash_type(session, path, *args, **kwargs) == "dir"
    except PathNotFoundError:
        return False

def is_trash_file(session, path, *args, **kwargs):
    """
        Check whether `path` is a trash file.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the trash resource

        :returns: `True` if `path` is a file, `False` otherwise (even if it doesn't exist)
    """

    try:
        return get_trash_type(session, path, *args, **kwargs) == "file"
    except PathNotFoundError:
        return False

def get_public_resources(session, *args, **kwargs):
    """
        Get a list of public resources.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param offset: offset from the beginning of the list
        :param limit: maximum number of elements in the list
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param type: filter based on type of resources ("file" or "dir")
        :param fields: list of keys to be included in the response

        :returns: :any:`PublicResourcesListObject`
    """

    request = GetPublicResourcesRequest(session, *args, **kwargs)
    request.send()

    return request.process()

def patch(session, path, properties, *args, **kwargs):
    """
        Update custom properties of a resource.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param path: path to the resource
        :param properties: `dict`, custom properties to update
        :param fields: list of keys to be included in the response

        :returns: :any:`ResourceObject`
    """

    request = PatchRequest(session, path, properties, *args, **kwargs)
    request.send()

    return request.process()

def get_files(session, *args, **kwargs):
    """
        Get a flat list of all files (that doesn't include directories).

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param offset: offset from the beginning of the list
        :param limit: number of list elements to be included
        :param media_type: type of files to include in the list
        :param sort: sort type

        :returns: generator of :any:`ResourceObject`
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

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param limit: maximum number of elements in the list
        :param media_type: type of files to include in the list
        :param preview_size: size of the file preview
        :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
        :param fields: list of keys to be included in the response

        :returns: generator of :any:`LastUploadedResourceListObject`
    """

    request = LastUploadedRequest(session, *args, **kwargs)
    request.send()

    for i in request.process().items:
        yield i

def upload_url(session, url, path, *args, **kwargs):
    """
        Upload a file from URL.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param url: source URL
        :param path: destination path
        :param disable_redirects: `bool`, forbid redirects
        :param fields: list of keys to be included in the response

        :returns: :any:`OperationLinkObject`, link to the asynchronous operation
    """

    request = UploadURLRequest(session, url, path, *args, **kwargs)
    request.send()

    return request.process()

def get_public_download_link(session, public_key, *args, **kwargs):
    """
        Get a download link for a public resource.

        :param session: an instance of :any:`requests.Session` with prepared headers
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

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param public_key: public key or public URL of the resource
        :param path_or_file: destination path or file-like object
    """

    n_retries = kwargs.pop("n_retries", None)

    if n_retries is None:
        n_retries = settings.DEFAULT_N_RETRIES

    retry_interval = kwargs.pop("retry_interval", None)

    if retry_interval is None:
        retry_interval = settings.DEFAULT_RETRY_INTERVAL

    file = None
    close_file = False

    try:
        if isinstance(file_or_path, (str, bytes)):
            close_file = True
            file = open(file_or_path, "wb")
        else:
            close_file = False
            file = file_or_path

        file_position = file.tell()

        def attempt():
            temp_kwargs = dict(kwargs)
            temp_kwargs["n_retries"] = 0
            temp_kwargs["retry_interval"] = 0.0

            link = get_public_download_link(session, public_key, *args, **temp_kwargs)

            temp_kwargs.pop("n_retries", None)
            temp_kwargs.pop("retry_interval", None)

            timeout = temp_kwargs.get("timeout")

            if timeout is None:
                timeout = settings.DEFAULT_TIMEOUT

            temp_kwargs["timeout"] = timeout
            temp_kwargs.setdefault("stream", True)

            # Disable keep-alive by default, since the download server is random
            try:
                temp_kwargs["headers"].setdefault("Connection", "close")
            except KeyError:
                temp_kwargs["headers"] = {"Connection": "close"}

            file.seek(file_position)

            with contextlib.closing(session.get(link, data=file, **temp_kwargs)) as response:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)

                if response.status_code != 200:
                    raise get_exception(response)

        auto_retry(attempt, n_retries, retry_interval)
    finally:
        if close_file and file is not None:
            file.close()
