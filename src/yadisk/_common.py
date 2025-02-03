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

import asyncio
import datetime
import inspect

from ._typing_compat import Callable, List
from . import settings

from typing import Optional, TypeVar, Any, Union

from .types import TimeoutParameter, Tuple

__all__ = [
    "bool_or_error",
    "dict_or_error",
    "ensure_path_has_schema",
    "float_or_error",
    "int_or_error",
    "is_default_timeout",
    "is_operation_link",
    "is_public_resource_link",
    "is_resource_link",
    "remove_path_schema",
    "str_or_dict_or_error",
    "str_or_error",
    "typed_list",
    "yandex_date"
]

T = TypeVar("T", bound=Callable)


def typed_list(datatype: T) -> Callable[[Optional[List]], List[T]]:
    def list_factory(iterable: Optional[List] = None) -> List[T]:
        if iterable is None:
            return []

        if not isinstance(iterable, list):
            raise ValueError(f"Expected a list, got {type(iterable)}")

        return [datatype(i) for i in iterable]

    return list_factory


def int_or_error(x: Any) -> int:
    if not isinstance(x, int):
        raise ValueError(f"{repr(x)} is not an integer")

    return x


def float_or_error(x: Any) -> float:
    if not isinstance(x, (float, int)):
        raise ValueError(f"{repr(x)} is not a float")

    return x


def str_or_error(x: Any) -> str:
    if not isinstance(x, str):
        raise ValueError(f"{repr(x)} is not a string")

    return x


def bool_or_error(x: Any) -> bool:
    if not isinstance(x, bool):
        raise ValueError(f"{repr(x)} is not a boolean value")

    return x


def dict_or_error(x: Any) -> dict:
    if not isinstance(x, dict):
        raise ValueError(f"{repr(x)} is not a dict")

    return x


def str_or_dict_or_error(x: Any) -> Union[str, dict]:
    if not isinstance(x, (str, dict)):
        raise ValueError(f"{repr(x)} is not a string nor a dict")

    return x


def yandex_date(string: str) -> datetime.datetime:
    return datetime.datetime.strptime(string[:-3] + string[-2:], "%Y-%m-%dT%H:%M:%S%z")


def _is_endpoint_link(link: str, base_endpoint_url: str) -> bool:
    link_schema, _, link = link.partition("://")
    endpoint_schema, _, base_endpoint_url = base_endpoint_url.partition("://")

    if link_schema not in ("http", "https") or endpoint_schema not in ("http", "https"):
        return False

    if not base_endpoint_url.endswith("/") and not base_endpoint_url.endswith("?"):
        base_endpoint_url += "/"

    return link.startswith(base_endpoint_url)


def is_operation_link(link: str) -> bool:
    return _is_endpoint_link(link, f"{settings.BASE_API_URL}/v1/disk/operations/")


def is_resource_link(url: str) -> bool:
    return _is_endpoint_link(url, f"{settings.BASE_API_URL}/v1/disk/resources?")


def is_public_resource_link(url: str) -> bool:
    return _is_endpoint_link(url, f"{settings.BASE_API_URL}/v1/disk/public/resources?")


KNOWN_SCHEMAS = ("disk:", "trash:", "app:", "photounlim:")


def ensure_path_has_schema(path: str, default_schema: str = "disk") -> str:
    # Modifies path to always have a schema (disk:/, trash:/ or app:/).
    # Without the schema Yandex.Disk won't let you upload filenames with the ':' character.
    # See https://github.com/ivknv/yadisk/issues/26 for more details

    if path in KNOWN_SCHEMAS:
        return default_schema + ":/" + path

    if path.startswith("/"):
        return default_schema + ":" + path

    if any(path.startswith(schema + "/") for schema in KNOWN_SCHEMAS):
        return path

    return default_schema + ":/" + path


def remove_path_schema(path: str) -> Tuple[str, str]:
    """
        Remove schema from path.

        :param path: `str`, path to remove the schema from

        :returns: `tuple[str, str]`, removed schema (without `:/`) and the path without it
    """

    if path.startswith("/") or path in KNOWN_SCHEMAS:
        return "", path

    if any(path.startswith(schema + "/") for schema in KNOWN_SCHEMAS):
        schema, sep, path = path.partition(":/")

        return schema, path

    return "", path


def is_async_func(func: Any) -> bool:
    return inspect.isgeneratorfunction(func) or asyncio.iscoroutinefunction(func)

def is_default_timeout(timeout: TimeoutParameter) -> bool:
    return timeout is ...
