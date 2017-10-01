#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..APIRequest import APIRequest
from ...objects import LinkObject

__all__ = ["UploadURLRequest"]

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
