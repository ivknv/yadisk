# -*- coding: utf-8 -*-

from .yadisk_object import YaDiskObject

__all__ = ["TokenObject", "TokenRevokeStatusObject"]

class TokenObject(YaDiskObject):
    """
        Token object.

        :param token: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar access_token: `str`, token string
        :ivar refresh_token: `str`, the refresh-token
        :ivar token_type: `str`, type of the token
        :ivar expires_in: `int`, amount of time before the token expires
    """

    def __init__(self, token=None, yadisk=None):
        YaDiskObject.__init__(
            self,
            {"access_token":  str,
             "refresh_token": str,
             "token_type":    str,
             "expires_in":    int},
            yadisk)

        self.import_fields(token)

class TokenRevokeStatusObject(YaDiskObject):
    """
        Result of token revocation request.

        :param token_revoke_status: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar status: `str`, status of the operation
    """

    def __init__(self, token_revoke_status=None, yadisk=None):
        YaDiskObject.__init__(self, {"status": str}, yadisk)

        self.import_fields(token_revoke_status)
