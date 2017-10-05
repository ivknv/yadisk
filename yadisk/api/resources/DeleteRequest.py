#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..APIRequest import APIRequest
from ...objects import LinkObject

__all__ = ["DeleteRequest"]

class DeleteRequest(APIRequest):
    """
        A request to delete a file or a directory.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the resource to be removed
        :param permanently: if `True`, the resource will be removed permanently,
                            otherwise, it will be just moved to the trash
        :param fields: list of keys to be included in the response
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources"
    method = "DELETE"
    success_codes = {202, 204}

    def __init__(self, session, path, permanently=False, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"path":        path,
                                            "permanently": permanently,
                                            "fields":      fields}, *args, **kwargs)

    def process_args(self, path, permanently, fields):
        self.params["path"] = path
        self.params["permanently"] = "true" if permanently else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        if js is not None:
            return LinkObject(js)
