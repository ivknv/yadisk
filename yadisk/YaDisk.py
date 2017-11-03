#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

from . import functions

__all__ = ["YaDisk"]

class YaDisk(object):
    """
        Implements access to Yandex.Disk REST API

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

    def make_session(self, token=None):
        """
            Prepares `requests.Session` object with headers needed for API.
            
            :param token: application token, equivalent to `self.token` if `None`
            :returns: `requests.Session`
        """

        if token is None:
            token = self.token

        session = requests.Session()

        if token:
            session.headers["Authorization"] = "OAuth " + token

        return session

    def get_auth_url(self, *args, **kwargs):
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

        return functions.get_auth_url(self.id, *args, **kwargs)

    def get_code_url(self, *args, **kwargs):
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

        return functions.get_code_url(self.id, *args, **kwargs)

    def get_token(self, code, *args, **kwargs):
        """
            Get a new token.

            :param code: confirmation code
            :param device_id: unique device ID (between 6 and 50 characters)

            :returns: `TokenObject`
        """

        return functions.get_token(code, self.id, self.secret, *args, **kwargs)

    def refresh_token(self, refresh_token, *args, **kwargs):
        """
            Refresh an existing token.

            :param refresh_token: the refresh token that was receieved with the token

            :returns: `TokenObject`
        """

        return functions.refresh_token(self.make_session(), refresh_token, self.id, self.secret, *args, **kwargs)

    def revoke_token(self, token=None, *args, **kwargs):
        """
            Revoke the token.

            :param token: token to revoke, equivalent to `self.token` if `None`

            :returns: `TokenRevokeStatusObject`
        """

        if token is None:
            token = self.token

        return functions.revoke_token(token, self.id, self.secret, *args, **kwargs)

    def get_disk_info(self, *args, **kwargs):
        """
            Get disk information.

            :param fields: list of keys to be included in the response

            :returns: `DiskInfoObject`
        """

        return functions.get_disk_info(self.make_session(), *args, **kwargs)

    def get_meta(self, path, *args, **kwargs):
        """
            Get meta information about a file/directory.

            :param path: path to the resource
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response

            :returns: `ResourceObject`
        """

        return functions.get_meta(self.make_session(), path, *args, **kwargs)

    def exists(self, path, *args, **kwargs):
        """
            Check whether `path` exists.

            :param path: path to the resource

            :returns: `bool`
        """

        return functions.exists(self.make_session(), path, *args, **kwargs)

    def get_type(self, path, *args, **kwargs):
        """
            Get resource type.

            :param path: path to the resource

            :returns: "file" or "dir"
        """

        return functions.get_type(self.make_session(), path, *args, **kwargs)

    def is_file(self, path, *args, **kwargs):
        """
            Check whether `path` is a file.

            :param path: path to the resource

            :returns: `True` if `path` is a file, `False` otherwise (even if it doesn't exist)
        """

        return functions.is_file(self.make_session(), path, *args, **kwargs)

    def is_dir(self, path, *args, **kwargs):
        """
            Check whether `path` is a directory.

            :param path: path to the resource

            :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
        """

        return functions.is_dir(self.make_session(), path, *args, **kwargs)

    def listdir(self, path, *args, **kwargs):
        """
            Get contents of `path`.

            :param path: path to the directory
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response

            :returns: generator of `ResourceObject`
        """

        return functions.listdir(self.make_session(), path, *args, **kwargs)

    def get_upload_link(self, path, *args, **kwargs):
        """
            Get a link to upload the file using the PUT request.

            :param path: destination path
            :param overwrite: `bool`, determines whether to overwrite the destination
            :param fields: list of keys to be included in the response

            :returns: `str`
        """

        return functions.get_upload_link(self.make_session(), path, *args, **kwargs)

    def upload(self, path_or_file, dst_path, *args, **kwargs):
        """
            Upload a file to disk.

            :param path_or_file: path or file-like object to be uploaded
            :param dst_path: destination path
            :param overwrite: if `True`, the resource will be overwritten if it already exists,
                              an error will be raised otherwise
            :param fields: list of keys to be included in the response

            :returns: `True` if the upload succeeded, `False` otherwise
        """

        return functions.upload(self.make_session(), path_or_file, dst_path, *args, **kwargs)

    def get_download_link(self, path, *args, **kwargs):
        """
            Get a download link for a file (or a directory).

            :param path: path to the resource
            :param fields: list of keys to be included in the response

            :returns: `str`
        """

        return functions.get_download_link(self.make_session(), path, *args, **kwargs)

    def download(self, src_path, path_or_file, *args, **kwargs):
        """
            Download the file.

            :param src_path: source path
            :param path_or_file: destination path or file-like object

            :returns: `True` if the download succeeded, `False` otherwise
        """

        return functions.download(self.make_session(), src_path, path_or_file, *args, **kwargs)

    def remove(self, path, *args, **kwargs):
        """
            Remove the resource.

            :param path: path to the resource to be removed
            :param permanently: if `True`, the resource will be removed permanently,
                                otherwise, it will be just moved to the trash
            :param fields: list of keys to be included in the response

            :returns: `OperationLinkObject` if the operation is performed asynchronously, `None` otherwise
        """

        return functions.remove(self.make_session(), path, *args, **kwargs)

    def mkdir(self, path, *args, **kwargs):
        """
            Create a new directory.

            :param path: path to the directory to be created
            :param fields: list of keys to be included in the response

            :returns: `LinkObject`
        """

        return functions.mkdir(self.make_session(), path, *args, **kwargs)

    def check_token(self, token=None, *args, **kwargs):
        """
            Check whether the token is valid.

            :param token: token to check, equivalent to `self.token` if `None`

            :returns: `bool`
        """

        return functions.check_token(self.make_session(token), *args, **kwargs)

    def get_trash_meta(self, path, *args, **kwargs):
        """
            Get meta information about a trash resource.

            :param path: path to the trash resource
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response

            :returns: `TrashResourceObject`
        """

        return functions.get_trash_meta(self.make_session(), path, *args, **kwargs)

    def trash_exists(self, path, *args, **kwargs):
        """
            Check whether the trash resource at `path` exists.

            :param path: path to the trash resource

            :returns: `bool`
        """

        return functions.trash_exists(self.make_session(), path, *args, **kwargs)

    def get_operation_status(self, operation_id, *args, **kwargs):
        """
            Get operation status.

            :param operation_id: ID of the operation or a link
            :param fields: list of keys to be included in the response

            :returns: `str`
        """

        return functions.get_operation_status(self.make_session(), operation_id, *args, **kwargs)

    def copy(self, src_path, dst_path, *args, **kwargs):
        """
            Copy `src_path` to `dst_path`.
            If the operation is performed asynchronously, returns the link to the operation,
            otherwise, returns the link to the newly created resource.

            :param src_path: source path
            :param dst_path: destination path
            :param overwrite: if `True` the destination path can be overwritten,
                              otherwise, an error will be raised
            :param fields: list of keys to be included in the response

            :returns: `LinkObject` or `OperationLinkObject`
        """

        return functions.copy(self.make_session(), src_path, dst_path, *args, **kwargs)

    def restore_trash(self, path, *args, **kwargs):
        """
            Restore a trash resource.
            Returns a link to the newly created resource or a link to the asynchronous operation.

            :param path: path to the trash resource to restore
            :param dst_path: destination path
            :param overwrite: `bool`, determines whether the destination can be overwritten
            :param fields: list of keys to be included in the response

            :returns: `LinkObject` or `OperationLinkObject`
        """

        return functions.restore_trash(self.make_session(), path, *args, **kwargs)

    def move(self, src_path, dst_path, *args, **kwargs):
        """
            Move `src_path` to `dst_path`.

            :param src_path: source path to be moved
            :param dst_path: destination path
            :param overwrite: `bool`, determines whether to overwrite the destination
            :param fields: list of keys to be included in the response

            :returns: `LinkObject`
        """

        return functions.move(self.make_session(), src_path, dst_path, *args, **kwargs)

    def remove_trash(self, path, *args, **kwargs):
        """
            Remove a trash resource.

            :param path: path to the trash resource to be deleted
            :param fields: list of keys to be included in the response

            :returns: `OperationLinkObject` if the operation is performed asynchronously, `None` otherwise
        """

        return functions.remove_trash(self.make_session(), path, *args, **kwargs)

    def publish(self, path, *args, **kwargs):
        """
            Make a resource public.

            :param path: path to the resource to be published
            :param fields: list of keys to be included in the response

            :returns: `LinkObject`, link to the resource
        """

        return functions.publish(self.make_session(), path, *args, **kwargs)

    def unpublish(self, path, *args, **kwargs):
        """
            Make a public resource private.

            :param path: path to the resource to be unpublished
            :param fields: list of keys to be included in the response

            :returns: `LinkObject`, link to the resource
        """

        return functions.unpublish(self.make_session(), path, *args, **kwargs)

    def save_to_disk(self, public_key, *args, **kwargs):
        """
            Saves a public resource to the disk.
            Returns the link to the operation if it's performed asynchronously,
            or a link to the resource otherwise.

            :param public_key: public key or public URL of the resource
            :param name: filename of the saved resource
            :param save_path: path to the destination directory (downloads directory by default)
            :param fields: list of keys to be included in the response

            :returns: `LinkObject` or `OperationLinkObject`
        """

        return functions.save_to_disk(self.make_session(), public_key, *args, **kwargs)

    def get_public_meta(self, public_key, *args, **kwargs):
        """
            Get meta-information about a public resource.

            :param public_key: public key or public URL of the resource
            :param offset: offset from the beginning of the list of nested resources
            :param limit: maximum number of nested elements to be included in the list
            :param sort: key to sort by
            :param preview_size: file preview size
            :param preview_crop: `bool`, allow preview crop
            :param fields: list of keys to be included in the response

            :returns: `PublicResourceObject`
        """

        return functions.get_public_meta(self.make_session(), public_key, *args, **kwargs)

    def public_exists(self, public_key, *args, **kwargs):
        """
            Check whether the public resource exists.

            :param public_key: public key or public URL of the resource

            :returns: `bool`
        """

        return functions.public_exists(self.make_session(), public_key, *args, **kwargs)

    def public_listdir(self, public_key, *args, **kwargs):
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

        return functions.public_listdir(self.make_session(), public_key, *args, **kwargs)

    def get_public_type(self, public_key, *args, **kwargs):
        """
            Get public resource type.

            :param public_key: public key or public URL of the resource

            :returns: "file" or "dir"
        """

        return functions.get_public_type(self.make_session(), public_key, *args, **kwargs)

    def is_public_dir(self, public_key, *args, **kwargs):
        """
            Check whether `public_key` is a public directory.

            :param session: an instance of `requests.Session` with prepared headers
            :param public_key: public key or public URL of the resource

            :returns: `True` if `public_key` is a directory, `False` otherwise (even if it doesn't exist)
        """

        return functions.is_public_dir(self.make_session(), public_key, *args, **kwargs)

    def is_public_file(self, public_key, *args, **kwargs):
        """
            Check whether `public_key` is a public file.

            :param public_key: public key or public URL of the resource

            :returns: `True` if `public_key` is a file, `False` otherwise (even if it doesn't exist)
        """

        return functions.is_public_file(self.make_session(), public_key, *args, **kwargs)

    def trash_listdir(self, path, *args, **kwargs):
        """
            Get contents of a trash resource.

            :param path: path to the directory in the trash bin
            :param limit: number of children resources to be included in the response
            :param offset: number of children resources to be skipped in the response
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response

            :returns: generator of `TrashResourceObject`
        """

        return functions.trash_listdir(self.make_session(), path, *args, **kwargs)

    def get_trash_type(self, path, *args, **kwargs):
        """
            Get trash resource type.

            :param path: path to the trash resource

            :returns: "file" or "dir"
        """

        return functions.get_trash_type(self.make_session(), path, *args, **kwargs)

    def is_trash_dir(self, path, *args, **kwargs):
        """
            Check whether `path` is a trash directory.

            :param path: path to the trash resource

            :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
        """

        return functions.is_trash_dir(self.make_session(), path, *args, **kwargs)

    def is_trash_file(self, path, *args, **kwargs):
        """
            Check whether `path` is a trash file.

            :param path: path to the trash resource

            :returns: `True` if `path` is a directory, `False` otherwise (even if it doesn't exist)
        """

        return functions.is_trash_file(self.make_session(), path, *args, **kwargs)

    def get_public_resources(self, *args, **kwargs):
        """
            Get a list of public resources.

            :param offset: offset from the beginning of the list
            :param limit: maximum number of elements in the list
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param type: filter based on type of resources ("file" or "dir")
            :param fields: list of keys to be included in the response
        """

        return functions.get_public_resources(self.make_session(), *args, **kwargs)

    def patch(self, path, properties, *args, **kwargs):
        """
            Update custom properties of a resource.

            :param path: path to the resource
            :param properties: `dict`, custom properties to update
            :param fields: list of keys to be included in the response

            :returns: `ResourceObject`
        """

        return functions.patch(self.make_session(), path, properties, *args, **kwargs)

    def get_files(self, *args, **kwargs):
        """
            Get a flat list of all files (that doesn't include directories).

            :param offset: offset from the beginning of the list
            :param limit: number of list elements to be included
            :param media_type: type of files to include in the list
            :param sort: sort type

            :returns: generator of `ResourceObject`
        """

        return functions.get_files(self.make_session(), *args, **kwargs)

    def get_last_uploaded(self, *args, **kwargs):
        """
            Get the list of latest uploaded files sorted by upload date.

            :param limit: maximum number of elements in the list
            :param media_type: type of files to include in the list
            :param preview_size: size of the file preview
            :param preview_crop: `bool`, cut the preview to the size specified in the `preview_size`
            :param fields: list of keys to be included in the response

            :returns: generator of `LastUploadedResourceListObject`
        """

        return functions.get_last_uploaded(self.make_session(), *args, **kwargs)

    def upload_url(self, url, path, *args, **kwargs):
        """
            Upload a file from URL.

            :param url: source URL
            :param path: destination path
            :param disable_redirects: `bool`, forbid redirects
            :param fields: list of keys to be included in the response

            :returns: `OperationLinkObject`, link to the asynchronous operation
        """

        return functions.upload_url(self.make_session(), url, path, *args, **kwargs)

    def get_public_download_link(self, public_key, *args, **kwargs):
        """
            Get a download link for a public resource.

            :param public_key: public key or public URL of the resource
            :param fields: list of keys to be included in the response

            :returns: `str`
        """

        return functions.get_public_download_link(self.make_session(), public_key, *args, **kwargs)

    def download_public(self, public_key, file_or_path, *args, **kwargs):
        """
            Download the public resource.

            :param public_key: public key or public URL of the resource
            :param path_or_file: destination path or file-like object

            :returns: `True` if the download succeeded, `False` otherwise
        """

        return functions.download_public(self.make_session(), public_key, file_or_path, *args, **kwargs)
