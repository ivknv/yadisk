# -*- coding: utf-8 -*-
# Copyright © 2024 Ivan Konovalov

# This file is part of a Python library yadisk.

# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, see <http://www.gnu.org/licenses/>.

from urllib.parse import urlparse, parse_qs, quote

from .api_request import APIRequest
from ..objects import OperationStatusObject
from .._common import is_operation_link
from ..exceptions import InvalidResponseError

from typing import Optional, TYPE_CHECKING
from .._typing_compat import Iterable

if TYPE_CHECKING:  # pragma: no cover
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

    def __init__(
        self,
        session: "AnySession",
        operation_id: str,
        fields: Optional[Iterable[str]] = None,
        **kwargs
    ) -> None:
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
