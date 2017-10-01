#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ...APIRequest import APIRequest
from ....objects import LinkObject

__all__ = ["DeleteTrashRequest"]

class DeleteTrashRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/trash/resources"
    method = "DELETE"
    success_codes = {202, 204}

    def __init__(self, session, path=None, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"path":   path,
                                            "fields": fields}, *args, **kwargs)

    def process_args(self, path, fields):
        if path is not None:
            self.params["path"] = path

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return LinkObject(js)
