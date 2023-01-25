# -*- coding: utf-8 -*-

from .api_request import APIRequest
from ..objects import DiskInfoObject
from ..exceptions import InvalidResponseError

from typing import Optional, TYPE_CHECKING
from ..compat import Iterable

if TYPE_CHECKING:
    import requests

__all__ = ["DiskInfoRequest"]

class DiskInfoRequest(APIRequest):
    """
        A request to get disk information.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param fields: list of keys to be included in the response

        :returns: :any:`DiskInfoObject`
    """

    url = "https://cloud-api.yandex.net/v1/disk"
    method = "GET"

    def __init__(self,
                 session: "requests.Session",
                 fields: Optional[Iterable[str]] = None, **kwargs):
        APIRequest.__init__(self, session, {"fields": fields}, **kwargs)

    def process_args(self, fields: Optional[Iterable[str]]) -> None:
        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js: Optional[dict]) -> DiskInfoObject:
        if js is None:
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        return DiskInfoObject(js)
