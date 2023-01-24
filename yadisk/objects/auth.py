# -*- coding: utf-8 -*-

from .yadisk_object import YaDiskObject
from ..common import str_or_error, int_or_error

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..yadisk import YaDisk

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

    access_token: Optional[str]
    refresh_token: Optional[str]
    token_type: Optional[str]
    expires_in: Optional[int]

    def __init__(self, token: Optional[dict] = None, yadisk: Optional["YaDisk"] = None):
        YaDiskObject.__init__(
            self,
            {"access_token":  str_or_error,
             "refresh_token": str_or_error,
             "token_type":    str_or_error,
             "expires_in":    int_or_error},
            yadisk)

        self.import_fields(token)

class TokenRevokeStatusObject(YaDiskObject):
    """
        Result of token revocation request.

        :param token_revoke_status: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar status: `str`, status of the operation
    """

    status: Optional[str]

    def __init__(self,
                 token_revoke_status: Optional[dict]=None,
                 yadisk: Optional["YaDisk"] = None):
        YaDiskObject.__init__(self, {"status": str_or_error}, yadisk)

        self.import_fields(token_revoke_status)
