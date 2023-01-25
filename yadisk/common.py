# -*- coding: utf-8 -*-

import datetime

from .compat import Callable, List

from typing import Optional, TypeVar, Any, Union

__all__ = ["typed_list", "int_or_error", "str_or_error", "bool_or_error",
           "dict_or_error", "str_or_dict_or_error", "yandex_date", "is_operation_link",
           "is_resource_link", "is_public_resource_link", "ensure_path_has_schema"]

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

def is_operation_link(link: str) -> bool:
    if link.startswith("https://cloud-api.yandex.net/v1/disk/operations/"):
        return True

    # Same but http:// version
    return link.startswith("http://cloud-api.yandex.net/v1/disk/operations/")

def is_resource_link(url: str) -> bool:
    if url.startswith("https://cloud-api.yandex.net/v1/disk/resources?"):
        return True

    # Check also for HTTP version
    return url.startswith("http://cloud-api.yandex.net/v1/disk/resources?")

def is_public_resource_link(url: str) -> bool:
    if url.startswith("https://cloud-api.yandex.net/v1/disk/public/resources?"):
        return True

    # Check also for HTTP version
    return url.startswith("http://cloud-api.yandex.net/v1/disk/public/resources?")

def ensure_path_has_schema(path: str, default_schema: str = "disk") -> str:
    # Modifies path to always have a schema (disk:/ or trash:/).
    # Without the schema Yandex.Disk won't let you upload filenames with the ':' character.
    # See https://github.com/ivknv/yadisk/issues/26 for more details

    if path in ("disk:", "trash:"):
        return default_schema + ":/" + path

    if path.startswith("disk:/") or path.startswith("trash:/"):
        return path

    if path.startswith("/"):
        return default_schema + ":" + path

    return default_schema + ":/" + path
