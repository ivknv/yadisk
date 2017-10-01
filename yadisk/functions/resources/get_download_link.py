#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ...api import GetDownloadLinkRequest

__all__ = ["get_download_link"]

def get_download_link(session, path, *args, **kwargs):
    request = GetDownloadLinkRequest(session, path, *args, **kwargs)
    request.send()

    return request.process().href
