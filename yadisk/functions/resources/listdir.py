#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .get_meta import get_meta

__all__ = ["listdir"]

def listdir(session, path, *args, **kwargs):
    result = get_meta(session, path, *args, **kwargs)

    if result.type == "file":
        raise NotADirectoryError("%r is a file" % (path,))

    for child in result.embedded.items:
        yield child

    offset = result.embedded.offset
    limit = result.embedded.limit
    total = result.embedded.total

    while offset + limit < total:
        result = get_meta(session, path, *args, offset=offset, limit=limit, **kwargs)

        for child in result.embedded.items:
            yield child

        offset += limit
        limit = result.embedded.limit
        total = result.embedded.total
