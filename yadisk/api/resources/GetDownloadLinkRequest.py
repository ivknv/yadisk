#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..APIRequest import APIRequest
from ...objects import LinkObject

__all__ = ["GetDownloadLinkRequest"]

class GetDownloadLinkRequest(APIRequest):
    """
        A request to get a download link to a resource.

        :param session: an instance of `requests.Session` with prepared headers
        :param path: path to the resource to be downloaded
        :param fields: list of keys to be included in the response
    """

    url = "https://cloud-api.yandex.net/v1/disk/resources/download"
    method = "GET"

    def __init__(self, session, path, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"path": path, "fields": fields},
                            *args, **kwargs)

    def process_args(self, path, fields):
        self.params["path"] = path

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return LinkObject(js)
