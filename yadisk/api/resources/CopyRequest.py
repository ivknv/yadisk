#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..APIRequest import APIRequest
from ...objects import LinkObject

__all__ = ["CopyRequest"]

class CopyRequest(APIRequest):
    """
        A request to copy a file or a directory.

        :param session: an instance of `requests.Session` with prepared headers
        :param src_path: source path
        :param dst_path: destination path
        :param overwrite: if `True` the destination path can be overwritten,
                          otherwise, an error will be raised
        :param fields: list of keys to be included in the response
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources/copy"
    method = "POST"
    success_codes = {201, 202}

    def __init__(self, session, src_path, dst_path, overwrite=False,
                 fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"src_path":  src_path,
                                            "dst_path":  dst_path,
                                            "overwrite": overwrite,
                                            "fields":    fields}, *args, **kwargs)

    def process_args(self, src_path, dst_path, overwrite, fields):
        self.params["from"] = src_path
        self.params["path"] = dst_path
        self.params["overwrite"] = "true" if overwrite else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return LinkObject(js)
