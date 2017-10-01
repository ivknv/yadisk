#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..APIRequest import APIRequest
from ...objects import ResourceUploadLink

__all__ = ["GetUploadLinkRequest"]

class GetUploadLinkRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    method = "GET"

    def __init__(self, session, path, overwrite=False, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"path":      path,
                                            "overwrite": overwrite,
                                            "fields":    fields}, *args, **kwargs)

    def process_args(self, path, overwrite, fields):
        self.params["path"] = path
        self.params["overwrite"] = "true" if overwrite else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return ResourceUploadLink(js)
