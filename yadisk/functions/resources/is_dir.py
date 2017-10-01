#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ...exceptions import DiskNotFoundError
from .get_type import get_type

__all__ = ["is_dir"]

def is_dir(session, path, *args, **kwargs):
    try:
        return get_type(session, path, *args, **kwargs) == "dir"
    except DiskNotFoundError:
        return False
