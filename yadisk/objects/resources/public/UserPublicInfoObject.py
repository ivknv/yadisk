#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ...YaDiskObject import YaDiskObject

__all__ = ["UserPublicInfoObject"]

class UserPublicInfoObject(YaDiskObject):
    def __init__(self, user_public_info=None):
        YaDiskObject.__init__(self, {"login":        str,
                                     "display_name": str,
                                     "uid":          str})
        self.import_fields(user_public_info)
