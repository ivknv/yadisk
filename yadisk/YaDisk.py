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

            :returns: authentication URL
        """

        return functions.get_auth_url(self.id, *args, **kwargs)

    def get_code_url(self):
        """
            Get the URL for the user to get the confirmation code.
            The confirmation code can later be used to get the token.

            :returns: authentication URL
        """

        return functions.get_code_url(self.id)

    def get_token(self, code, *args, **kwargs):
        """
            Get a new token.

            :param code: confirmation code

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

            :returns: `DiskObject`
        """

        return functions.get_disk_info(self.make_session(), *args, **kwargs)

    def get_meta(self, path, *args, **kwargs):
        """
            Get meta information about a file/directory.

            :param path: path to the resource

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

            :returns: generator of `ResourceObject`
        """

        return functions.listdir(self.make_session(), path, *args, **kwargs)

    def get_upload_link(self, path, *args, **kwargs):
        """
            Get a link to upload the file to.

            :param path: destination path

            :returns: `LinkObject`
        """

        return functions.get_upload_link(self.make_session(), path, *args, **kwargs)

    def upload(self, path_or_file, dst_path, *args, **kwargs):
        """
            Upload a file to disk.

            :param path_or_file: path or file-like object to be uploaded
            :param dst_path: destination path

            :returns: `True` if the upload succeeded, `False` otherwise
        """

        return functions.upload(self.make_session(), path_or_file, dst_path, *args, **kwargs)

    def get_download_link(self, path, *args, **kwargs):
        """
            Get a download link for a file (or a directory).

            :param path: path to the resource

            :returns: `LinkObject`
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

            :returns: `LinkObject` if the operation is performed asynchronously, `None` otherwise
        """

        return functions.remove(self.make_session(), path, *args, **kwargs)

    def mkdir(self, path, *args, **kwargs):
        """
            Create a new directory.

            :param path: path to the directory to be created

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

            :returns: `LinkObject`
        """

        return functions.copy(self.make_session(), src_path, dst_path, *args, **kwargs)
