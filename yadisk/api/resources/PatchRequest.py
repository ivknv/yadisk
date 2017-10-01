#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json

from ..APIRequest import APIRequest
from ...objects import ResourceObject

__all__ = ["PatchRequest"]

class PatchRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    method = "PATCH"

    def __init__(self, session, path, body, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"path":   path,
                                            "body":   body,
                                            "fields": fields}, *args, **kwargs)

    def process_args(self, path, body, fields):
        self.params["path"] = path
        self.params["body"] = json.dumps(body)

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return ResourceObject(js)
