#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .YaDiskObject import YaDiskObject

__all__ = ["TokenObject", "TokenRevokeStatusObject"]

class TokenObject(YaDiskObject):
    """
        Token object.

        :param token: `dict` or `None`

        access_token
            `str`, token string
        refresh_token
            `str`, the refresh-token
        token_type
            `str`, type of the token
        expires_in
            `int`, amount of time before the token expires
    """

    def __init__(self, token=None):
        YaDiskObject.__init__(self, {"access_token":  str,
                                     "refresh_token": str,
                                     "token_type":    str,
                                     "exprires_in":   int})

        self.import_fields(token)

class TokenRevokeStatusObject(YaDiskObject):
    """
        Result of token revocation request.

        :param token_revoke_status: `dict` or `None`

        status
            `str`, status of the operation
    """

    def __init__(self, token_revoke_status=None):
        YaDiskObject.__init__(self, {"status": str})

        self.import_fields(token_revoke_status)
