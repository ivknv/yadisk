#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ...APIRequest import APIRequest
from ....objects import LinkObject

__all__ = ["SaveToDiskRequest"]

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
