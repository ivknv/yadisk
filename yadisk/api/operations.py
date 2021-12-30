# -*- coding: utf-8 -*-

from urllib.parse import urlparse, parse_qs
from urllib.parse import quote as urlencode

from .api_request import APIRequest
from ..objects import OperationStatusObject
from ..common import is_operation_link

__all__ = ["GetOperationStatusRequest"]

class GetOperationStatusRequest(APIRequest):
    """
        A request to get operation status.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param operation_id: operation ID or link
        :param fields: list of keys to be included in the response

        :returns: :any:`OperationStatusObject`
    """

    method = "GET"

    def __init__(self, session, operation_id, fields=None, **kwargs):
        if is_operation_link(operation_id):
            parsed_url = urlparse(operation_id)
            self.url = "https://" + parsed_url.netloc + parsed_url.path

            params = parse_qs(parsed_url.query)

            if fields is None:
                fields = params.get("fields", [None])[0]
        else:
            operation_id = urlencode(operation_id)
            self.url = "https://cloud-api.yandex.net/v1/disk/operations/%s" % (operation_id,)

        APIRequest.__init__(self, session, {"fields": fields}, **kwargs)

    def process_args(self, fields):
        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        if "items" in js:
            return OperationStatusObject(js["items"][0])
        return OperationStatusObject(js)
