# -*- coding: utf-8 -*-

from .yadisk_object import YaDiskObject
from ..common import str_or_error, int_or_error

from typing import Any, Optional

__all__ = ["TokenObject", "TokenRevokeStatusObject", "DeviceCodeObject"]

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

    def __init__(self, token: Optional[dict] = None, yadisk: Optional[Any] = None):
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
                 token_revoke_status: Optional[dict] = None,
                 yadisk: Optional[Any] = None):
        YaDiskObject.__init__(self, {"status": str_or_error}, yadisk)

        self.import_fields(token_revoke_status)

class DeviceCodeObject(YaDiskObject):
    """
        Result of :any:`Client.get_device_code()` / :any:`AsyncClient.get_device_code()`.

        :param device_code_object: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar device_code: `str`, device code that can be used for obtaining the token
        :ivar user_code: `str`, code that the user should enter on the OAuth page
        :ivar verification_url: `str`, URL of the OAuth page where user is
                                expected to enter the :code:`user_code`
        :ivar interval: `int`, the minimum interval (in seconds) with which the
                        app must request an OAuth token. If requests come more
                        often, Yandex OAuth may respond with an error
        :ivar expires_in: `int`, amount of time before the codes expire
    """

    device_code:      Optional[str]
    user_code:        Optional[str]
    verification_url: Optional[str]
    interval:         Optional[int]
    expires_in:       Optional[int]

    def __init__(self,
                 device_code_object: Optional[dict] = None,
                 yadisk: Optional[Any] = None):
        YaDiskObject.__init__(
            self,
            {
                "device_code":      str_or_error,
                "user_code":        str_or_error,
                "verification_url": str_or_error,
                "interval":         int_or_error,
                "expires_in":       int_or_error
            },
            yadisk)

        self.import_fields(device_code_object)
