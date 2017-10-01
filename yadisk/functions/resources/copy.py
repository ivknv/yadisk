#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ...api import CopyRequest

__all__ = ["copy"]

def copy(session, src_path, dst_path, *args, **kwargs):
    request = CopyRequest(session, src_path, dst_path, *args, **kwargs)

    request.send()

    return request.process()
