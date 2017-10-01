#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

__all__ = ["typed_list", "yandex_date"]

def typed_list(datatype):
    class TypedList(list):
        def __init__(self, iterable=None):
            if iterable is None:
                list.__init__(self)
                return

            list.__init__(self, (datatype(i) for i in iterable))

    return TypedList

def yandex_date(string):
    return datetime.datetime.strptime(string[:-3] + string[-2:], "%Y-%m-%dT%H:%M:%S%z")
