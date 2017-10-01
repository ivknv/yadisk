#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..YaDiskObject import YaDiskObject

__all__ = ["TokenObject"]

class TokenObject(YaDiskObject):
    def __init__(self, token=None):
        YaDiskObject.__init__(self, {"access_token":  str,
                                     "refresh_token": str,
                                     "token_type":    str,
                                     "exprires_in":   int})

        self.import_fields(token)
