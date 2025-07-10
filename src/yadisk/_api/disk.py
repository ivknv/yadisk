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

from .api_request import APIRequest
from ..objects import DiskInfoObject
from ..exceptions import InvalidResponseError

from typing import Optional, TYPE_CHECKING
from .._typing_compat import Iterable

if TYPE_CHECKING:  # pragma: no cover
    from ..types import AnySession, JSON

__all__ = ["DiskInfoRequest"]


class DiskInfoRequest(APIRequest):
    """
        A request to get disk information.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param extra_fields: list of additional keys to be included in the response
        :param fields: list of keys to be included in the response

        :returns: :any:`DiskInfoObject`
    """

    method = "GET"
    path = "/v1/disk"

    def __init__(
        self,
        session: "AnySession",
        extra_fields: Optional[Iterable[str]] = None,
        fields: Optional[Iterable[str]] = None,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        if extra_fields is not None:
            self.params["extra_fields"] = ",".join(extra_fields)

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js: "JSON", **kwargs) -> DiskInfoObject:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk returned invalid JSON")

        return DiskInfoObject(js)
