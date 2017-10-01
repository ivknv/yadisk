#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..YaDiskObject import YaDiskObject

__all__ = ["ShareInfoObject"]

class ShareInfoObject(YaDiskObject):
    def __init__(self, share_info=None):
        YaDiskObject.__init__(self, {"is_root":  bool,
                                     "is_owned": bool,
                                     "rights":   str})
        self.import_fields(share_info)
