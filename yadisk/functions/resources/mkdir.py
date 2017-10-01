#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ...api import MkdirRequest

__all__ = ["mkdir"]

def mkdir(session, path, *args, **kwargs):
    request = MkdirRequest(session, path, *args, **kwargs)

    request.send()

    return request.process()
