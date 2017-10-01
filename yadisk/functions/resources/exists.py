#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ...exceptions import DiskNotFoundError
from .get_meta import get_meta

__all__ = ["exists"]

def exists(session, path, *args, **kwargs):
    try:
        get_meta(session, path, *args, **kwargs)

        return True
    except DiskNotFoundError:
        return False
