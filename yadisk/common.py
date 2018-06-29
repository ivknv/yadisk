# -*- coding: utf-8 -*-

import datetime

__all__ = ["typed_list", "yandex_date", "is_operation_link"]

def typed_list(datatype):
    def list_factory(iterable=None):
        if iterable is None:
            return []

        return [datatype(i) for i in iterable]

    return list_factory

def yandex_date(string):
    return datetime.datetime.strptime(string[:-3] + string[-2:], "%Y-%m-%dT%H:%M:%S%z")

def is_operation_link(link):
    return link.startswith("https://cloud-api.yandex.net/v1/disk/operations/")
