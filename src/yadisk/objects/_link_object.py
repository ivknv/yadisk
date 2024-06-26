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

from ._yadisk_object import YaDiskObject

from typing import Any, Optional

from .._common import str_or_error, bool_or_error

__all__ = ["LinkObject"]


class LinkObject(YaDiskObject):
    """
        Link object.

        :param link: `dict` or `None`
        :param yadisk: :any:`Client`/:any:`AsyncClient` or `None`, `YaDisk` object

        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
    """

    href: Optional[str]
    method: Optional[str]
    templated: Optional[bool]

    def __init__(self,
                 link: Optional[dict] = None,
                 yadisk: Optional[Any] = None):
        YaDiskObject.__init__(
            self,
            {"href":      str_or_error,
             "method":    str_or_error,
             "templated": bool_or_error},
            yadisk)

        self.import_fields(link)
