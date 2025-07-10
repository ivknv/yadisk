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

from collections.abc import Generator
from typing import Any, Optional
from .._typing_compat import Callable, Iterator

__all__ = ["YaDiskObject"]


class YaDiskObject:
    """
        Base class for all objects mirroring the ones returned by Yandex.Disk REST API.
        It must have a fixed number of fields, each field must have a type.
        It also supports subscripting and access of fields through the . operator.

        :param field_types: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object
    """

    FIELD_TYPES: dict
    FIELDS: dict
    ALIASES: dict
    _yadisk: Optional[Any]

    def __init__(self,
                 field_types: Optional[dict] = None,
                 yadisk: Optional[Any] = None):
        if field_types is None:
            field_types = {}

        self.FIELD_TYPES = {}
        self.FIELDS = {}
        self.ALIASES = {}
        self.set_field_types(field_types)

        self._yadisk = yadisk

    def __dir__(self) -> Generator[str, None, None]:
        """
            Return available attributes.
        """

        yield from super().__dir__()
        yield from self.FIELD_TYPES.keys()
        yield from self.ALIASES.keys()

    def set_field_types(self, field_types: dict) -> None:
        """
            Set the field types of the object

            :param field_types: `dict`, where keys are the field names and values are types (or factories)
        """

        self.FIELD_TYPES = field_types

    def set_field_type(self, field: str, type: Callable) -> None:
        """
            Set field type.

            :param field: `str`
            :param type: type or factory
        """

        self.FIELD_TYPES[field] = type

    def set_alias(self, alias: str, name: str) -> None:
        """
            Set an alias.

            :param alias: `str`, alias to add
            :param name: `str`, field name
        """

        self.ALIASES[alias] = name

    def remove_alias(self, alias: str) -> None:
        """
            Remove an alias.

            :param alias: `str`
        """

        self.ALIASES.pop(alias)

    def remove_field(self, field: str) -> None:
        """
            Remove field.

            :param field: `str`
        """

        self.FIELDS.pop(field, None)
        self.FIELD_TYPES.pop(field)

    def import_fields(self, source_dict: Optional[dict]) -> None:
        """
            Set all the fields of the object to the values in `source_dict`.
            All the other fields are ignored

            :param source_dict: `dict` or `None` (nothing will be done in that case)
        """

        if source_dict is not None:
            for field in self.FIELD_TYPES:
                try:
                    self[field] = source_dict[field]
                except KeyError:
                    pass

            for alias, field in self.ALIASES.items():
                try:
                    self[field] = source_dict[alias]
                except KeyError:
                    pass

    def __setattr__(self, attr: str, value: Any) -> None:
        if attr in ("FIELDS", "FIELD_TYPES", "ALIASES", "_yadisk"):
            self.__dict__[attr] = value
            return

        attr = self.ALIASES.get(attr, attr)

        if attr not in self.FIELD_TYPES:
            raise AttributeError("Unknown attribute: %r" % (attr,))

        datatype = self.FIELD_TYPES[attr]
        self.FIELDS[attr] = datatype(value) if value is not None else None

    def __getattr__(self, attr: str) -> Any:
        attr = self.ALIASES.get(attr, attr)

        if attr not in self.FIELD_TYPES:
            raise AttributeError("Unknown attribute: %r" % (attr,))

        return self.FIELDS.get(attr)

    def __getitem__(self, key: str) -> Any:
        key = self.ALIASES.get(key, key)

        if key not in self.FIELD_TYPES:
            raise KeyError(str(key))

        return self.FIELDS.get(key)

    def __setitem__(self, key: str, value: Any) -> None:
        self.__setattr__(key, value)

    def __delitem__(self, key: str) -> None:
        key = self.ALIASES.get(key, key)

        if key not in self.FIELD_TYPES:
            raise KeyError(str(key))

        self.FIELDS.pop(key, None)

    def __iter__(self) -> Iterator[dict]:
        return iter(self.FIELDS)

    def __len__(self) -> int:
        return len(self.FIELDS)

    def __repr__(self) -> str:
        return "<%s%r>" % (self.__class__.__name__, self.FIELDS)

    def _repr_pretty_(self, p, cycle: bool) -> None:
        """IPython pretty-print implementation."""

        if cycle:
            p.text(f"<{self.__class__.__name__}{'{...}'}>")
        else:
            if not self.FIELDS:
                p.text(f"<{self.__class__.__name__}{'{}'}>")
                return

            with p.group(4, f"<{self.__class__.__name__}{'{'}", "})>"):
                p.breakable()

                for idx, (k, v) in enumerate(self.FIELDS.items()):
                    if idx:
                        p.text(",")
                        p.breakable()

                    p.text(repr(k))
                    p.text(": ")
                    p.pretty(v)

    def field(self, name: str) -> Any:
        """
            Get value of field `name`, guarantee it's not :code:`None` or
            raise a :any:`ValueError`.

            :param name: `str`, name of the field

            :raises ValueError: value of the given field is :code:`None`

            :returns: field's value
        """

        value = self.__getattr__(name)

        if value is not None:
            return value

        raise ValueError(f"field {repr(name)} is None")

    def __matmul__(self, name: str) -> Any:
        """
            The :code:`@` operator. Same as :any:`YaDiskObject.field()`.
            Can be used like this:

            .. code:: python

                # if embedded or embedded.total turn out to be None, we'll get a ValueError
                file_count = client.get_meta("/some_folder") @ "embedded" @ "total"
                print(f"/some_folder contains {file_count} files")

            :param name: `str`, name of the field

            :raises ValueError: value of the given field is :code:`None`

            :returns: field's value
        """

        return self.field(name)
