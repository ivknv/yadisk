# -*- coding: utf-8 -*-

from urllib.parse import urlparse, parse_qs, quote

from .api_request import APIRequest
from ..objects import OperationStatusObject
from ..common import is_operation_link
from ..exceptions import InvalidResponseError

from typing import Optional, TYPE_CHECKING
from ..compat import Iterable

if TYPE_CHECKING:
    from ..types import AnySession, JSON

__all__ = ["GetOperationStatusRequest"]

class GetOperationStatusRequest(APIRequest):
    """
        A request to get operation status.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param operation_id: operation ID or link
        :param fields: list of keys to be included in the response

        :returns: :any:`OperationStatusObject`
    """

    method = "GET"

    def __init__(self,
                 session: "AnySession",
                 operation_id: str,
                 fields: Optional[Iterable[str]] = None, **kwargs):
        if is_operation_link(operation_id):
            parsed_url = urlparse(operation_id)
            operation_id = parsed_url.path.rpartition("/")[2]

            params = parse_qs(parsed_url.query)

            if fields is None:
                fields = params.get("fields", [None])[0]
        else:
            operation_id = quote(operation_id)

        self.path = f"/v1/disk/operations/{operation_id}"

        APIRequest.__init__(self, session, **kwargs)

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js: "JSON", **kwargs) -> OperationStatusObject:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        if js.get("status") not in ("in-progress", "success", "failed"):
            raise InvalidResponseError(f"Yandex.Disk returned invalid operation status object: {js}")

        return OperationStatusObject(js)
