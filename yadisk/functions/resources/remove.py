#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ...api import DeleteRequest

__all__ = ["remove"]

def remove(session, path, *args, **kwargs):
    request = DeleteRequest(session, path, *args, **kwargs)

    request.send()

    return request.process()
