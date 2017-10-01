#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .. import get_disk_info
from ...exceptions import UnauthorizedError

__all__ = ["check_token"]

def check_token(session, *args, **kwargs):
    try:
        get_disk_info(session, *args, **kwargs)
        return True
    except UnauthorizedError:
        return False
