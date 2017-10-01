#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .get_meta import get_meta

__all__ = ["get_type"]

def get_type(session, path, *args, **kwargs):
    return get_meta(session, path, *args, **kwargs).type
