#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ...api import GetMetaRequest

__all__ = ["get_meta"]

def get_meta(session, *args, **kwargs):
    request = GetMetaRequest(session, *args, **kwargs)
    request.send()

    return request.process()
