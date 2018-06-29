# -*- coding: utf-8 -*-

from .yadisk_object import YaDiskObject

__all__ = ["TokenObject", "TokenRevokeStatusObject"]

class TokenObject(YaDiskObject):
    """
        Token object.

        :param token: `dict` or `None`

        :ivar access_token: `str`, token string
        :ivar refresh_token: `str`, the refresh-token
        :ivar token_type: `str`, type of the token
        :ivar expires_in: `int`, amount of time before the token expires
    """

    def __init__(self, token=None):
        YaDiskObject.__init__(self, {"access_token":  str,
                                     "refresh_token": str,
                                     "token_type":    str,
                                     "expires_in":    int})

        self.import_fields(token)

class TokenRevokeStatusObject(YaDiskObject):
    """
        Result of token revocation request.

        :param token_revoke_status: `dict` or `None`

        :ivar status: `str`, status of the operation
    """

    def __init__(self, token_revoke_status=None):
        YaDiskObject.__init__(self, {"status": str})

        self.import_fields(token_revoke_status)
