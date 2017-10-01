#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ...api import GetUploadLinkRequest

__all__ = ["get_upload_link"]

def get_upload_link(session, path, *args, **kwargs):
    request = GetUploadLinkRequest(session, path, *args, **kwargs)
    request.send()

    return request.process().href
