#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..api import DiskRequest

__all__ = ["get_disk_info"]

def get_disk_info(session, *args, **kwargs):
    """
        Get disk information.

        :param session: an instance of `requests.Session` with prepared headers
        :param fields: list of keys to be included in the response

        :returns: `DiskObject`
    """

    request = DiskRequest(session, *args, **kwargs)
    request.send()

    return request.process()
