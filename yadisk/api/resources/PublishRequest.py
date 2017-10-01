#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..APIRequest import APIRequest
from ...objects import LinkObject

__all__ = ["PublishRequest"]

class PublishRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/resources/publish"
    method = "PUT"

    def __init__(self, session, path, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"path":   path,
                                            "fields": fields}, *args, **kwargs)

    def process_args(self, path, fields):
        self.params["path"] = path

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return LinkObject(js)
