#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..YaDiskObject import YaDiskObject

__all__ = ["LinkObject"]

class LinkObject(YaDiskObject):
    def __init__(self, link=None):
        YaDiskObject.__init__(self, {"href":      str,
                                     "method":    str,
                                     "templated": bool})

        self.import_fields(link)
