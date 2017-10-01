#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..APIRequest import APIRequest
from ...objects import DiskObject

__all__ = ["DiskRequest"]

class DiskRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk"
    method = "GET"

    def __init__(self, session, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"fields": fields}, *args, **kwargs)

    def process_args(self, fields):
        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return DiskObject(js)
