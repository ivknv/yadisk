#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

from . import functions

__all__ = ["YaDisk"]

class YaDisk(object):
    def __init__(self, id="", secret="", token=""):
        self.id = id
        self.secret = secret
        self.token = token

    def make_session(self, token=None):
        if token is None:
            token = self.token

        session = requests.Session()

        if token:
            session.headers["Authorization"] = "OAuth " + token

        return session

    def get_auth_url(self, *args, **kwargs):
        return functions.get_auth_url(self.id, *args, **kwargs)

    def get_code_url(self):
        return functions.get_auth_url(self.id)

    def get_token(self, code, *args, **kwargs):
        return functions.get_token(code, self.id, self.secret, *args, **kwargs)

    def refresh_token(self, refresh_token, *args, **kwargs):
        return functions.refresh_token(self.make_session(), refresh_token, self.id, self.secret, *args, **kwargs)

    def revoke_token(self, token=None, *args, **kwargs):
        if token is None:
            token = self.token

        return functions.revoke_token(token, self.id, self.secret, *args, **kwargs)

    def get_disk_info(self, *args, **kwargs):
        return functions.get_disk_info(self.make_session(), *args, **kwargs)

    def get_meta(self, path, *args, **kwargs):
        return functions.get_meta(self.make_session(), path, *args, **kwargs)

    def exists(self, path, *args, **kwargs):
        return functions.exists(self.make_session(), path, *args, **kwargs)

    def get_type(self, path, *args, **kwargs):
        return functions.get_type(self.make_session(), path, *args, **kwargs)

    def is_file(self, path, *args, **kwargs):
        return functions.is_file(self.make_session(), path, *args, **kwargs)

    def is_dir(self, path, *args, **kwargs):
        return functions.is_dir(self.make_session(), path, *args, **kwargs)

    def listdir(self, path, *args, **kwargs):
        return functions.listdir(self.make_session(), path, *args, **kwargs)

    def get_upload_link(self, path, *args, **kwargs):
        return functions.get_upload_link(self.make_session(), path, *args, **kwargs)

    def upload(self, path_or_file, dst_path, *args, **kwargs):
        return functions.upload(self.make_session(), path_or_file, dst_path, *args, **kwargs)

    def get_download_link(self, path, *args, **kwargs):
        return functions.get_download_link(self.make_session(), path, *args, **kwargs)

    def download(self, src_path, path_or_file, *args, **kwargs):
        return functions.download(self.make_session(), src_path, path_or_file, *args, **kwargs)

    def remove(self, path, *args, **kwargs):
        return functions.remove(self.make_session(), path, *args, **kwargs)

    def mkdir(self, path, *args, **kwargs):
        return functions.mkdir(self.make_session(), path, *args, **kwargs)

    def check_token(self, token=None, *args, **kwargs):
        return functions.check_token(self.make_session(token), *args, **kwargs)

    def get_trash_meta(self, path, *args, **kwargs):
        return functions.get_trash_meta(self.make_session(), path, *args, **kwargs)

    def trash_exists(self, path, *args, **kwargs):
        return functions.trash_exists(self.make_session(), path, *args, **kwargs)

    def get_operation_status(self, operation_id, *args, **kwargs):
        return functions.get_operation_status(self.make_session(), operation_id, *args, **kwargs)

    def copy(self, src_path, dst_path, *args, **kwargs):
        return functions.copy(self.make_session(), src_path, dst_path, *args, **kwargs)
