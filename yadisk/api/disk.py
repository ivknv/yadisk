# -*- coding: utf-8 -*-

from .api_request import APIRequest
from ..objects import DiskInfoObject
from ..exceptions import InvalidResponseError

from typing import Optional, TYPE_CHECKING
from ..compat import Iterable

if TYPE_CHECKING:
    from ..types import AnySession, JSON

__all__ = ["DiskInfoRequest"]

class DiskInfoRequest(APIRequest):
    """
        A request to get disk information.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param fields: list of keys to be included in the response

        :returns: :any:`DiskInfoObject`
    """

    method = "GET"
    path = "/v1/disk"

    def __init__(self,
                 session: "AnySession",
                 fields: Optional[Iterable[str]] = None, **kwargs):
        APIRequest.__init__(self, session, **kwargs)

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js: "JSON", **kwargs) -> DiskInfoObject:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        return DiskInfoObject(js)
