#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ...api import DiskRequest

__all__ = ["get_disk_info"]

def get_disk_info(session, fields=None, **send_args):
    request = DiskRequest(session, fields=fields)
    request.send(**send_args)

    return request.process()
