# -*- coding: utf-8 -*-

import functools
import threading
import weakref

import requests

from . import functions

__all__ = ["YaDisk"]

class YaDisk(object):
    """
        Implements access to Yandex.Disk REST API.

        :param id: application ID
        :param secret: application secret password
        :param token: application token

        :ivar id: `str`, application ID
        :ivar secret: `str`, application secret password
        :ivar token: `str`, application token
    """

    def __init__(self, id="", secret="", token=""):
        self.id = id
        self.secret = secret
        self.token = token

        @functools.lru_cache(maxsize=1024)
        def _get_session(token, tid):
            return self.make_session(token)

        self._get_session = _get_session

    def clear_session_cache(self):
        """Clears the session cache. Unused sessions will be closed."""

        self._get_session.cache_clear()

    def make_session(self, token=None):
        """
            Prepares :any:`requests.Session` object with headers needed for API.
            
            :param token: application token, equivalent to `self.token` if `None`
            :returns: :any:`requests.Session`
        """

        if token is None:
            token = self.token

        session = requests.Session()

        # Make sure the session is eventually closed
        weakref.finalize(session, session.close)

        if token:
            session.headers["Authorization"] = "OAuth " + token

        return session

    def get_session(self, token=None):
        """
            Like :any:`YaDisk.make_session` but wrapped in :any:`functools.lru_cache`.
            
            :returns: :any:`requests.Session`, different instances for different threads
        """

        if token is None:
            token = self.token

        return self._get_session(token, threading.get_ident())

    def get_auth_url(self, **kwargs):
        """
            Get authentication URL for the user to go to.

            :param type: response type ("code" to get the confirmation code or "token" to get the token automatically)
            :param device_id: unique device ID, must be between 6 and 50 characters
            :param device_name: device name, should not be longer than 100 characters
            :param display: indicates whether to use lightweight layout, values other than "popup" are ignored
            :param login_hint: username or email for the account the token is being requested for
            :param scope: list of permissions for the application
            :param optional_scope: list of optional permissions for the application
            :param force_confirm: if True, user will be required to confirm access to the account
                                  even if the user has already granted access for the application
            :param state: The state string, which Yandex.OAuth returns without any changes (<= 1024 characters)

            :returns: authentication URL
        """

        return functions.get_auth_url(self.id, **kwargs)

    def get_code_url(self, **kwargs):
        """
            Get the URL for the user to get the confirmation code.
            The confirmation code can later be used to get the token.

            :param device_id: unique device ID, must be between 6 and 50 characters
            :param device_name: device name, should not be longer than 100 characters
            :param display: indicates whether to use lightweight layout, values other than "popup" are ignored
            :param login_hint: username or email for the account the token is being requested for
            :param scope: list of permissions for the application
            :param optional_scope: list of optional permissions for the application
            :param force_confirm: if True, user will be required to confirm access to the account
                                  even if the user has already granted access for the application
            :param state: The state string, which Yandex.OAuth returns without any changes (<= 1024 characters)

            :returns: authentication URL
        """

        return functions.get_code_url(self.id, **kwargs)

    def get_token(self, code, **kwargs):
        """
            Get a new token.

            :param code: confirmation code
            :param device_id: unique device ID (between 6 and 50 characters)
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`TokenObject`
        """

        return functions.get_token(code, self.id, self.secret, **kwargs)

    def refresh_token(self, refresh_token, **kwargs):
        """
            Refresh an existing token.

            :param refresh_token: the refresh token that was received with the token
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`TokenObject`
        """

        return functions.refresh_token(refresh_token, self.id, self.secret,
                                       **kwargs)

    def revoke_token(self, token=None, **kwargs):
        """
            Revoke the token.

            :param token: token to revoke, equivalent to `self.token` if `None`
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`TokenRevokeStatusObject`
        """

        if token is None:
            token = self.token

        return functions.revoke_token(token, self.id, self.secret, **kwargs)

    def get_disk_info(self, **kwargs):
        """
            Get disk information.

            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`DiskInfoObject`
        """

        return functions.get_disk_info(self.get_session(), **kwargs)

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

        return functions.get_meta(self.get_session(), path, **kwargs)

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

        return functions.exists(self.get_session(), path, **kwargs)

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

        return functions.get_type(self.get_session(), path, **kwargs)

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

        return functions.is_file(self.get_session(), path, **kwargs)

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

        return functions.is_dir(self.get_session(), path, **kwargs)

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

        return functions.listdir(self.get_session(), path, **kwargs)

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

        return functions.get_upload_link(self.get_session(), path, **kwargs)

    def upload(self, path_or_file, dst_path, **kwargs):
        """
            Upload a file to disk.

            :param path_or_file: path or file-like object to be uploaded
            :param dst_path: destination path
            :param overwrite: if `True`, the resource will be overwritten if it already exists,
                              an error will be raised otherwise
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
        """

        functions.upload(self.get_session(), path_or_file, dst_path, **kwargs)

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

        return functions.get_download_link(self.get_session(), path, **kwargs)

    def download(self, src_path, path_or_file, **kwargs):
        """
            Download the file.

            :param src_path: source path
            :param path_or_file: destination path or file-like object
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
        """

        functions.download(self.get_session(), src_path, path_or_file, **kwargs)

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

            :returns: :any:`OperationLinkObject` if the operation is performed asynchronously, `None` otherwise
        """

        return functions.remove(self.get_session(), path, **kwargs)

    def mkdir(self, path, **kwargs):
        """
            Create a new directory.

            :param path: path to the directory to be created
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`LinkObject`
        """

        return functions.mkdir(self.get_session(), path, **kwargs)

    def check_token(self, token=None, **kwargs):
        """
            Check whether the token is valid.

            :param token: token to check, equivalent to `self.token` if `None`
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: `bool`
        """

        return functions.check_token(self.get_session(token), **kwargs)

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

        return functions.get_trash_meta(self.get_session(), path, **kwargs)

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

        return functions.trash_exists(self.get_session(), path, **kwargs)

    def get_operation_status(self, operation_id, **kwargs):
        """
            Get operation status.

            :param operation_id: ID of the operation or a link
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: `str`
        """

        return functions.get_operation_status(self.get_session(), operation_id,
                                              **kwargs)

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

            :returns: :any:`LinkObject` or :any:`OperationLinkObject`
        """

        return functions.copy(self.get_session(), src_path, dst_path, **kwargs)

    def restore_trash(self, path, dst_path=None, **kwargs):
        """
            Restore a trash resource.
            Returns a link to the newly created resource or a link to the asynchronous operation.

            :param path: path to the trash resource to restore
            :param dst_path: destination path
            :param overwrite: `bool`, determines whether the destination can be overwritten
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`LinkObject` or :any:`OperationLinkObject`
        """

        return functions.restore_trash(self.get_session(), path, dst_path, **kwargs)

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

            :returns: :any:`OperationLinkObject` or :any:`LinkObject`
        """

        return functions.move(self.get_session(), src_path, dst_path, **kwargs)

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

        return functions.remove_trash(self.get_session(), path, **kwargs)

    def publish(self, path, **kwargs):
        """
            Make a resource public.

            :param path: path to the resource to be published
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`LinkObject`, link to the resource
        """

        return functions.publish(self.get_session(), path, **kwargs)

    def unpublish(self, path, **kwargs):
        """
            Make a public resource private.

            :param path: path to the resource to be unpublished
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`LinkObject`, link to the resource
        """

        return functions.unpublish(self.get_session(), path, **kwargs)

    def save_to_disk(self, public_key, **kwargs):
        """
            Saves a public resource to the disk.
            Returns the link to the operation if it's performed asynchronously,
            or a link to the resource otherwise.

            :param public_key: public key or public URL of the resource
            :param name: filename of the saved resource
            :param path: path to the copied resource in the public folder
            :param save_path: path to the destination directory (downloads directory by default)
            :param force_async: forces the operation to be executed asynchronously
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`LinkObject` or :any:`OperationLinkObject`
        """

        return functions.save_to_disk(self.get_session(), public_key, **kwargs)

    def get_public_meta(self, public_key, **kwargs):
        """
            Get meta-information about a public resource.

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
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`PublicResourceObject`
        """

        return functions.get_public_meta(self.get_session(), public_key, **kwargs)

    def public_exists(self, public_key, **kwargs):
        """
            Check whether the public resource exists.

            :param public_key: public key or public URL of the resource
            :param path: relative path to the resource within the public folder
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: `bool`
        """

        return functions.public_exists(self.get_session(), public_key, **kwargs)

    def public_listdir(self, public_key, **kwargs):
        """
            Get contents of a public directory.

            :param public_key: public key or public URL of the resource
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

        return functions.public_listdir(self.get_session(), public_key, **kwargs)

    def get_public_type(self, public_key, **kwargs):
        """
            Get public resource type.

            :param public_key: public key or public URL of the resource
            :param path: relative path to the resource within the public folder
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: "file" or "dir"
        """

        return functions.get_public_type(self.get_session(), public_key, **kwargs)

    def is_public_dir(self, public_key, **kwargs):
        """
            Check whether `public_key` is a public directory.

            :param public_key: public key or public URL of the resource
            :param path: relative path to the resource within the public folder
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: `True` if `public_key` is a directory, `False` otherwise (even if it doesn't exist)
        """

        return functions.is_public_dir(self.get_session(), public_key, **kwargs)

    def is_public_file(self, public_key, **kwargs):
        """
            Check whether `public_key` is a public file.

            :param public_key: public key or public URL of the resource
            :param path: relative path to the resource within the public folder
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: `True` if `public_key` is a file, `False` otherwise (even if it doesn't exist)
        """

        return functions.is_public_file(self.get_session(), public_key, **kwargs)

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

        return functions.trash_listdir(self.get_session(), path, **kwargs)

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

        return functions.get_trash_type(self.get_session(), path, **kwargs)

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

        return functions.is_trash_dir(self.get_session(), path, **kwargs)

    def is_trash_file(self, path, **kwargs):
        """
            Check whether `path` is a trash file.

            :param path: path to the trash resource
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
        """

        return functions.is_trash_file(self.get_session(), path, **kwargs)

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

        return functions.get_public_resources(self.get_session(), **kwargs)

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

        return functions.patch(self.get_session(), path, properties, **kwargs)

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

        return functions.get_files(self.get_session(), **kwargs)

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

        return functions.get_last_uploaded(self.get_session(), **kwargs)

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

        return functions.upload_url(self.get_session(), url, path, **kwargs)

    def get_public_download_link(self, public_key, **kwargs):
        """
            Get a download link for a public resource.

            :param public_key: public key or public URL of the resource
            :param path: relative path to the resource within the public folder
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: `str`
        """

        return functions.get_public_download_link(self.get_session(),
                                                  public_key, **kwargs)

    def download_public(self, public_key, file_or_path, **kwargs):
        """
            Download the public resource.

            :param public_key: public key or public URL of the resource
            :param file_or_path: destination path or file-like object
            :param path: relative path to the resource within the public folder
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds
        """

        functions.download_public(self.get_session(), public_key, file_or_path,
                                  **kwargs)
