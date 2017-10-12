#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from urllib.parse import urlparse, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs

from .APIRequest import APIRequest
from ..objects import OperationStatusObject

__all__ = ["GetOperationStatusRequest"]

class GetOperationStatusRequest(APIRequest):
    """
        A request to get operation status.

        :param session: an instance of `requests.Session` with prepared headers
        :param operation_id: operation ID or link
        :param fields: list of keys to be included in the response
    """

    method = "GET"

    def __init__(self, session, operation_id, fields=None, *args, **kwargs):
        if operation_id.startswith("https://"):
            parsed_url = urlparse(operation_id)
            self.url = parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path

            params = parse_qs(parsed_url.query)
            operation_id = parsed_url.path.rsplit("/", 1)[0]

            if fields is None:
                fields = params.get("fields", [None])[0]
        else:
            self.url = "https://cloud-api.yandex.net/v1/disk/operations/%s" % (operation_id,)

        APIRequest.__init__(self, session, {"fields": fields}, *args, **kwargs)

    def process_args(self, fields):
        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        if "items" in js:
            return OperationStatusObject(js["items"][0])
        return OperationStatusObject(js)
