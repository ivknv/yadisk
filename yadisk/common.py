# -*- coding: utf-8 -*-

import datetime

__all__ = ["typed_list", "yandex_date", "is_operation_link", "is_resource_link",
           "is_public_resource_link", "ensure_path_has_schema"]

def typed_list(datatype):
    def list_factory(iterable=None):
        if iterable is None:
            return []

        return [datatype(i) for i in iterable]

    return list_factory

def yandex_date(string):
    return datetime.datetime.strptime(string[:-3] + string[-2:], "%Y-%m-%dT%H:%M:%S%z")

def is_operation_link(link):
    if link.startswith("https://cloud-api.yandex.net/v1/disk/operations/"):
        return True

    # Same but http:// version
    return link.startswith("http://cloud-api.yandex.net/v1/disk/operations/")

def is_resource_link(url):
    if url.startswith("https://cloud-api.yandex.net/v1/disk/resources?"):
        return True

    # Check also for HTTP version
    return url.startswith("http://cloud-api.yandex.net/v1/disk/resources?")

def is_public_resource_link(url):
    if url.startswith("https://cloud-api.yandex.net/v1/disk/public/resources?"):
        return True

    # Check also for HTTP version
    return url.startswith("http://cloud-api.yandex.net/v1/disk/public/resources?")

def ensure_path_has_schema(path, default_schema="disk"):
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
