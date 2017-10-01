#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ....exceptions import DiskNotFoundError
from .get_trash_meta import get_trash_meta

__all__ = ["trash_exists"]

def trash_exists(session, path, *args, **kwargs):
    try:
        get_trash_meta(session, path, *args, **kwargs)
        return True
    except DiskNotFoundError:
        return False
