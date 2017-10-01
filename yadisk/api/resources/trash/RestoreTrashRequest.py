#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ...APIRequest import APIRequest
from ....objects import LinkObject

__all__ = ["RestoreTrashRequest"]

class RestoreTrashRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/trash/resources/restore"
    method = "PUT"
    success_codes = {201, 202}

    def __init__(self, session, path=None, name=None, overwrite=False, fields=None,
                 *args, **kwargs):
        APIRequest.__init__(self, session, {"path":      path,
                                            "name":      name,
                                            "overwrite": overwrite,
                                            "fields":    fields}, *args, **kwargs)

    def process_args(self, path, name, overwrite, fields):
        self.params["path"] = path
        self.params["overwrite"] = "true" if overwrite else "false"

        if name is not None:
            self.params["name"] = name

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return LinkObject(js)
