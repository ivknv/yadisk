# -*- coding: utf-8 -*-

import contextlib

from .api import CopyRequest, GetDownloadLinkRequest, GetMetaRequest
from .api import GetUploadLinkRequest, MkdirRequest, DeleteRequest, GetTrashRequest
from .api import RestoreTrashRequest, MoveRequest, DeleteTrashRequest
from .api import PublishRequest, UnpublishRequest, SaveToDiskRequest, GetPublicMetaRequest
from .api import GetPublicResourcesRequest, PatchRequest, FilesRequest
from .api import LastUploadedRequest, UploadURLRequest, GetPublicDownloadLinkRequest
from .exceptions import WrongResourceTypeError, PathNotFoundError
from .utils import auto_retry, get_exception
from .objects import ResourceLinkObject, PublicResourceLinkObject

from . import settings

__all__ = ["ResourceMethodsMixin"]

def _exists(get_meta_function, *args, **kwargs):
    kwargs = dict(kwargs)
    kwargs["limit"] = 0

    try:
        get_meta_function(*args, **kwargs)

        return True
    except PathNotFoundError:
        return False

def _get_type(get_meta_function, *args, **kwargs):
    kwargs = dict(kwargs)
    kwargs["limit"] = 0

    return get_meta_function(*args, **kwargs).type

def _listdir(get_meta_function, path, kwargs):
    # kwargs is passed this way to avoid a TypeError sometimes (see issue https://github.com/ivknv/yadisk/issues/7)
    kwargs = dict(kwargs)
    kwargs.setdefault("limit", 10000)

    if kwargs.get("fields") is None:
        kwargs["fields"] = []

    kwargs["fields"] = ["embedded.items.%s" % (k,) for k in kwargs["fields"]]

    # Fields that are absolutely necessary
    NECESSARY_FIELDS = ["type",
                        "embedded",
                        "embedded.offset",
                        "embedded.limit",
                        "embedded.total",
                        "embedded.items"]

    kwargs["fields"].extend(NECESSARY_FIELDS)

    result = get_meta_function(path, **kwargs)

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
        result = get_meta_function(path, **kwargs)

        for child in result.embedded.items:
            yield child

        limit = result.embedded.limit
        total = result.embedded.total

class ResourceMethodsMixin:
    def get_meta(self, path, **kwargs):
        """
            Get meta information about a file/directory.

            :param path: path to the resource
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

            :returns: :any:`ResourceObject`
        """

        request = GetMetaRequest(self.get_session(), path, **kwargs)
        request.send()

        return request.process(yadisk=self)

    def exists(self, path, **kwargs):
        """
            Check whether `path` exists.

            :param path: path to the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: `bool`
        """

        return _exists(self.get_meta, path, **kwargs)

    def get_type(self, path, **kwargs):
        """
            Get resource type.

            :param path: path to the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: "file" or "dir"
        """

        return _get_type(self.get_meta, path, **kwargs)

    def is_file(self, path, **kwargs):
        """
            Check whether `path` is a file.

            :param path: path to the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: `True` if `path` is a file, `False` otherwise (even if it doesn't exist)
        """

        try:
            return self.get_type(path, **kwargs) == "file"
        except PathNotFoundError:
            return False

    def is_dir(self, path, **kwargs):
        """
            Check whether `path` is a directory.

            :param path: path to the resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
        """

        try:
            return self.get_type(path, **kwargs) == "dir"
        except PathNotFoundError:
            return False

    def listdir(self, path, **kwargs):
        """
            Get contents of `path`.

            :param path: path to the directory
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: generator of :any:`ResourceObject`
        """

        return _listdir(self.get_meta, path, kwargs)

    def get_upload_link(self, path, **kwargs):
        """
            Get a link to upload the file using the PUT request.

            :param path: destination path
            :param overwrite: `bool`, determines whether to overwrite the destination
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: `str`
        """

        request = GetUploadLinkRequest(self.get_session(), path, **kwargs)
        request.send()

        return request.process().href

    def _upload(self, get_upload_link_function, file_or_path, dst_path, **kwargs):
        kwargs = dict(kwargs)

        try:
            timeout = kwargs["timeout"]
        except KeyError:
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

        session = self.get_session()

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

                link = get_upload_link_function(dst_path, **temp_kwargs)

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

    def upload(self, file_or_path, dst_path, **kwargs):
        """
            Upload a file to disk.

            :param file_or_path: path or file-like object to be uploaded
            :param dst_path: destination path
            :param overwrite: if `True`, the resource will be overwritten if it already exists,
                              an error will be raised otherwise
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`ResourceLinkObject`, link to the destination resource
        """

        self._upload(self.get_upload_link, file_or_path, dst_path, **kwargs)

        return ResourceLinkObject.from_path(dst_path, yadisk=self)

    def upload_by_link(self, file_or_path, link, **kwargs):
        """
            Upload a file to disk using an upload link.

            :param file_or_path: path or file-like object to be uploaded
            :param link: upload link
            :param overwrite: if `True`, the resource will be overwritten if it already exists,
                              an error will be raised otherwise
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
        """

        self._upload(lambda *args, **kwargs: link, file_or_path, dst_path, **kwargs)

    def get_download_link(self, path, **kwargs):
        """
            Get a download link for a file (or a directory).

            :param path: path to the resource
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: `str`
        """

        request = GetDownloadLinkRequest(self.get_session(), path, **kwargs)
        request.send()

        return request.process().href

    def _download(self, get_download_link_function, src_path, file_or_path, **kwargs):
        kwargs = dict(kwargs)

        n_retries = kwargs.get("n_retries")

        if n_retries is None:
            n_retries = settings.DEFAULT_N_RETRIES

        retry_interval = kwargs.get("retry_interval")

        if retry_interval is None:
            retry_interval = settings.DEFAULT_RETRY_INTERVAL

        try:
            timeout = kwargs["timeout"]
        except KeyError:
            timeout = settings.DEFAULT_TIMEOUT

        kwargs["timeout"] = timeout

        file = None
        close_file = False

        session = self.get_session()

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
                link = get_download_link_function(src_path, **temp_kwargs)

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

                with contextlib.closing(session.get(link, **temp_kwargs)) as response:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            file.write(chunk)

                    if response.status_code != 200:
                        raise get_exception(response)

            auto_retry(attempt, n_retries, retry_interval)
        finally:
            if close_file and file is not None:
                file.close()

    def download(self, src_path, file_or_path, **kwargs):
        """
            Download the file.

            :param src_path: source path
            :param file_or_path: destination path or file-like object
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`ResourceLinkObject`, link to the source resource
        """

        self._download(self.get_download_link, src_path, file_or_path, **kwargs)

        return ResourceLinkObject.from_path(src_path, yadisk=self)

    def download_by_link(self, link, file_or_path, **kwargs):
        """
            Download the file from the link.

            :param link: download link
            :param file_or_path: destination path or file-like object
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
        """

        self._download(lambda *args, **kwargs: link, None, file_or_path, **kwargs)

    def remove(self, path, **kwargs):
        """
            Remove the resource.

            :param path: path to the resource to be removed
            :param permanently: if `True`, the resource will be removed permanently,
                                otherwise, it will be just moved to the trash
            :param md5: `str`, MD5 hash of the file to remove
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`LinkObject` if the operation is performed asynchronously, `None` otherwise
        """

        request = DeleteRequest(self.get_session(), path, **kwargs)

        request.send()

        return request.process(yadisk=self)

    def mkdir(self, path, **kwargs):
        """
            Create a new directory.

            :param path: path to the directory to be created
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`ResourceLinkObject`
        """

        request = MkdirRequest(self.get_session(), path, **kwargs)
        request.send()

        return request.process(yadisk=self)

    def get_trash_meta(self, path, **kwargs):
        """
            Get meta information about a trash resource.

            :param path: path to the trash resource
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

            :returns: :any:`TrashResourceObject`
        """

        request = GetTrashRequest(self.get_session(), path, **kwargs)
        request.send()

        return request.process(yadisk=self)

    def trash_exists(self, path, **kwargs):
        """
            Check whether the trash resource at `path` exists.

            :param path: path to the trash resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: `bool`
        """

        return _exists(self.get_trash_meta, path, **kwargs)

    def copy(self, src_path, dst_path, **kwargs):
        """
            Copy `src_path` to `dst_path`.
            If the operation is performed asynchronously, returns the link to the operation,
            otherwise, returns the link to the newly created resource.

            :param src_path: source path
            :param dst_path: destination path
            :param overwrite: if `True` the destination path can be overwritten,
                              otherwise, an error will be raised
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`ResourceLinkObject` or :any:`OperationLinkObject`
        """

        request = CopyRequest(self.get_session(), src_path, dst_path, **kwargs)
        request.send()

        return request.process(yadisk=self)

    def restore_trash(self, path, dst_path=None, **kwargs):
        """
            Restore a trash resource.
            Returns a link to the newly created resource or a link to the asynchronous operation.

            :param path: path to the trash resource to be restored
            :param dst_path: destination path
            :param overwrite: `bool`, determines whether the destination can be overwritten
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`ResourceLinkObject` or :any:`OperationLinkObject`
        """

        kwargs = dict(kwargs)
        kwargs["dst_path"] = dst_path

        request = RestoreTrashRequest(self.get_session(), path, **kwargs)
        request.send()

        return request.process(yadisk=self)

    def move(self, src_path, dst_path, **kwargs):
        """
            Move `src_path` to `dst_path`.

            :param src_path: source path to be moved
            :param dst_path: destination path
            :param overwrite: `bool`, determines whether to overwrite the destination
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`ResourceLinkObject` or :any:`OperationLinkObject`
        """

        request = MoveRequest(self.get_session(), src_path, dst_path, **kwargs)
        request.send()

        return request.process(yadisk=self)

    def remove_trash(self, path, **kwargs):
        """
            Remove a trash resource.

            :param path: path to the trash resource to be deleted
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`OperationLinkObject` if the operation is performed asynchronously, `None` otherwise
        """

        request = DeleteTrashRequest(self.get_session(), path, **kwargs)
        request.send()

        return request.process(yadisk=self)

    def publish(self, path, **kwargs):
        """
            Make a resource public.

            :param path: path to the resource to be published
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`ResourceLinkObject`, link to the resource
        """

        request = PublishRequest(self.get_session(), path, **kwargs)
        request.send()

        return request.process(yadisk=self)

    def unpublish(self, path, **kwargs):
        """
            Make a public resource private.

            :param path: path to the resource to be unpublished
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`ResourceLinkObject`
        """

        request = UnpublishRequest(self.get_session(), path, **kwargs)
        request.send()

        return request.process(yadisk=self)

    def save_to_disk(self, public_key, **kwargs):
        """
            Saves a public resource to the disk.
            Returns the link to the operation if it's performed asynchronously,
            or a link to the resource otherwise.

            :param public_key: public key or public URL of the public resource
            :param name: filename of the saved resource
            :param path: path to the copied resource in the public folder
            :param save_path: path to the destination directory (downloads directory by default)
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`ResourceLinkObject` or :any:`OperationLinkObject`
        """

        request = SaveToDiskRequest(self.get_session(), public_key, **kwargs)
        request.send()

        return request.process(yadisk=self)

    def get_public_meta(self, public_key, **kwargs):
        """
            Get meta-information about a public resource.

            :param public_key: public key or public URL of the public resource
            :param path: relative path to a resource in a public folder.
                         By specifying the key of the published folder in `public_key`,
                         you can request metainformation for any resource in the folder.
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

            :returns: :any:`PublicResourceObject`
        """

        request = GetPublicMetaRequest(self.get_session(), public_key, **kwargs)
        request.send()

        return request.process(yadisk=self)

    def public_exists(self, public_key, **kwargs):
        """
            Check whether the public resource exists.

            :param public_key: public key or public URL of the public resource
            :param path: relative path to the resource within the public folder
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: `bool`
        """

        return _exists(self.get_public_meta, public_key, **kwargs)

    def public_listdir(self, public_key, **kwargs):
        """
            Get contents of a public directory.

            :param public_key: public key or public URL of the public resource
            :param path: relative path to the resource in the public folder.
                         By specifying the key of the published folder in `public_key`,
                         you can request contents of any nested folder.
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: generator of :any:`PublicResourceObject`
        """

        return _listdir(self.get_public_meta, public_key, kwargs)

    def get_public_type(self, public_key, **kwargs):
        """
            Get public resource type.

            :param public_key: public key or public URL of the public resource
            :param path: relative path to the resource within the public folder
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: "file" or "dir"
        """

        return _get_type(self.get_public_meta, public_key, **kwargs)

    def is_public_dir(self, public_key, **kwargs):
        """
            Check whether the public resource is a public directory.

            :param public_key: public key or public URL of the public resource
            :param path: relative path to the resource within the public folder
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: `True` if `public_key` is a directory, `False` otherwise (even if it doesn't exist)
        """

        try:
            return self.get_public_type(public_key, **kwargs) == "dir"
        except PathNotFoundError:
            return False

    def is_public_file(self, public_key, **kwargs):
        """
            Check whether the public resource is a public file.

            :param public_key: public key or public URL of the public resource
            :param path: relative path to the resource within the public folder
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: `True` if `public_key` is a file, `False` otherwise (even if it doesn't exist)
        """

        try:
            return self.get_public_type(public_key, **kwargs) == "file"
        except PathNotFoundError:
            return False

    def trash_listdir(self, path, **kwargs):
        """
            Get contents of a trash resource.

            :param path: path to the directory in the trash bin
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: generator of :any:`TrashResourceObject`
        """

        return _listdir(self.get_trash_meta, path, kwargs)

    def get_trash_type(self, path, **kwargs):
        """
            Get trash resource type.

            :param path: path to the trash resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: "file" or "dir"
        """

        return _get_type(self.get_trash_meta, path, **kwargs)

    def is_trash_dir(self, path, **kwargs):
        """
            Check whether `path` is a trash directory.

            :param path: path to the trash resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
        """

        try:
            return self.get_trash_type(path, **kwargs) == "dir"
        except PathNotFoundError:
            return False

    def is_trash_file(self, path, **kwargs):
        """
            Check whether `path` is a trash file.

            :param path: path to the trash resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: `True` if `path` is a file, `False` otherwise (even if it doesn't exist)
        """

        try:
            return self.get_trash_type(path, **kwargs) == "file"
        except PathNotFoundError:
            return False

    def get_public_resources(self, **kwargs):
        """
            Get a list of public resources.

            :param offset: offset from the beginning of the list
            :param limit: maximum number of elements in the list
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param type: filter based on type of resources ("file" or "dir")
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`PublicResourcesListObject`
        """

        request = GetPublicResourcesRequest(self.get_session(), **kwargs)
        request.send()

        return request.process(yadisk=self)

    def patch(self, path, properties, **kwargs):
        """
            Update custom properties of a resource.

            :param path: path to the resource
            :param properties: `dict`, custom properties to update
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`ResourceObject`
        """

        request = PatchRequest(self.get_session(), path, properties, **kwargs)
        request.send()

        return request.process(yadisk=self)

    def get_files(self, **kwargs):
        """
            Get a flat list of all files (that doesn't include directories).

            :param offset: offset from the beginning of the list
            :param limit: number of list elements to be included
            :param media_type: type of files to include in the list
            :param sort: `str`, field to be used as a key to sort children resources
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: generator of :any:`ResourceObject`
        """

        if kwargs.get("limit") is not None:
            request = FilesRequest(self.get_session(), **kwargs)
            request.send()

            for i in request.process(yadisk=self).items:
                yield i

            return

        kwargs = dict(kwargs)

        kwargs.setdefault("offset", 0)
        kwargs["limit"] = 1000

        while True:
            counter = 0
            for i in self.get_files(**kwargs):
                counter += 1
                yield i

            if counter < kwargs["limit"]:
                break

            kwargs["offset"] += kwargs["limit"]

    def get_last_uploaded(self, **kwargs):
        """
            Get the list of latest uploaded files sorted by upload date.

            :param limit: maximum number of elements in the list
            :param media_type: type of files to include in the list
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: generator of :any:`LastUploadedResourceListObject`
        """

        request = LastUploadedRequest(self.get_session(), **kwargs)
        request.send()

        for i in request.process(yadisk=self).items:
            yield i

    def upload_url(self, url, path, **kwargs):
        """
            Upload a file from URL.

            :param url: source URL
            :param path: destination path
            :param disable_redirects: `bool`, forbid redirects
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`OperationLinkObject`, link to the asynchronous operation
        """

        request = UploadURLRequest(self.get_session(), url, path, **kwargs)
        request.send()

        return request.process(yadisk=self)

    def get_public_download_link(self, public_key, **kwargs):
        """
            Get a download link for a public resource.

            :param public_key: public key or public URL of the public resource
            :param path: relative path to the resource within the public folder
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: `str`
        """

        request = GetPublicDownloadLinkRequest(self.get_session(), public_key, **kwargs)
        request.send()

        return request.process().href

    def download_public(self, public_key, file_or_path, **kwargs):
        """
            Download the public resource.

            :param public_key: public key or public URL of the public resource
            :param file_or_path: destination path or file-like object
            :param path: relative path to the resource within the public folder
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
        """

        self._download(
            lambda *args, **kwargs: self.get_public_download_link(public_key),
            None, file_or_path, **kwargs)

        return PublicResourceLinkObject.from_public_key(public_key, yadisk=self)
