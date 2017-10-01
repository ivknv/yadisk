#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..YaDiskObject import YaDiskObject

__all__ = ["TokenRevokeStatus"]

class TokenRevokeStatus(YaDiskObject):
    def __init__(self, token_revoke_status=None):
        YaDiskObject.__init__(self, {"status": str})

        self.import_fields(token_revoke_status)
