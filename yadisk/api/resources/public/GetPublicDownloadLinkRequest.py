#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ...APIRequest import APIRequest
from ....objects import LinkObject

__all__ = ["GetPublicDownloadLinkRequest"]

class GetPublicDownloadLinkRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
    method = "GET"

    def __init__(self, session, public_key, path=None, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"public_key":   public_key,
                                            "path":         path,
                                            "fields":       fields}, *args, **kwargs)

    def process_args(self, public_key, path, fields):
        self.params["public_key"] = public_key
        
        if path is not None:
            self.params["path"] = path

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return LinkObject(js)
