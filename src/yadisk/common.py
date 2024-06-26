# -*- coding: utf-8 -*-

import asyncio
import datetime
import inspect

from .compat import Callable, List
from . import settings

from typing import Optional, TypeVar, Any, Union

__all__ = ["typed_list", "int_or_error", "str_or_error", "bool_or_error",
           "dict_or_error", "str_or_dict_or_error", "yandex_date", "is_operation_link",
           "is_resource_link", "is_public_resource_link", "ensure_path_has_schema",
           "CaseInsensitiveDict"]

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


def ensure_path_has_schema(path: str, default_schema: str = "disk") -> str:
    # Modifies path to always have a schema (disk:/, trash:/ or app:/).
    # Without the schema Yandex.Disk won't let you upload filenames with the ':' character.
    # See https://github.com/ivknv/yadisk/issues/26 for more details

    KNOWN_SCHEMAS = ("disk:", "trash:", "app:", "photounlim:")

    if path in KNOWN_SCHEMAS:
        return default_schema + ":/" + path

    if path.startswith("/"):
        return default_schema + ":" + path

    if any(path.startswith(schema + "/") for schema in KNOWN_SCHEMAS):
        return path

    return default_schema + ":/" + path


# https://stackoverflow.com/a/32888599/3653520
class CaseInsensitiveDict(dict):
    @classmethod
    def _k(cls, key: str) -> str:
        return key.lower()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._convert_keys()

    def __getitem__(self, key: str) -> Any:
        return super().__getitem__(self.__class__._k(key))

    def __setitem__(self, key: str, value: Any) -> None:
        super().__setitem__(self.__class__._k(key), value)

    def __delitem__(self, key: str) -> Any:
        return super().__delitem__(self.__class__._k(key))

    def __contains__(self, key: Any) -> bool:
        return super().__contains__(self.__class__._k(key))

    def pop(self, key: str, /, *args, **kwargs) -> Any:
        return super().pop(self.__class__._k(key), *args, **kwargs)

    def get(self, key: str, /, *args, **kwargs) -> Any:
        return super().get(self.__class__._k(key), *args, **kwargs)

    def setdefault(self, key: str, *args, **kwargs) -> Any:
        return super().setdefault(self.__class__._k(key), *args, **kwargs)

    def update(self, *args, **kwargs) -> None:
        super().update(*(self.__class__(arg) for arg in args), **self.__class__(kwargs))

    def _convert_keys(self) -> None:
        for k in list(self.keys()):
            v = super(CaseInsensitiveDict, self).pop(k)
            self.__setitem__(k, v)


def is_async_func(func: Any) -> bool:
    return inspect.isgeneratorfunction(func) or asyncio.iscoroutinefunction(func)
