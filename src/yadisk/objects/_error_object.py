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

__all__ = ["ErrorObject"]


class ErrorObject(YaDiskObject):
    """
        Mirrors Yandex.Disk REST API error object.

        :param error: `dict` or `None`
        :param yadisk: `YaDisk` or `None`, `YaDisk` object

        :ivar message: `str`, human-readable error message
        :ivar description: `str`, technical error description
        :ivar error: `str`, error code
    """

    def __init__(self, error=None, yadisk=None):
        YaDiskObject.__init__(
            self,
            {"message":     str,
             "description": str,
             "error":       str},
            yadisk)
        self.set_alias("error_description", "message")
        self.import_fields(error)
