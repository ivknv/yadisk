#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ....api import GetTrashRequest

__all__ = ["get_trash_meta"]

def get_trash_meta(session, path, *args, **kwargs):
    request = GetTrashRequest(session, path, *args, **kwargs)

    request.send()

    return request.process()
