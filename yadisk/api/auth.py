# -*- coding: utf-8 -*-

from .api_request import APIRequest
from ..objects import TokenObject, TokenRevokeStatusObject
from ..exceptions import InvalidResponseError

from typing import Optional, TYPE_CHECKING

from urllib.parse import urlencode

if TYPE_CHECKING:
    from ..types import AnySession

__all__ = ["RefreshTokenRequest", "RevokeTokenRequest", "GetTokenRequest"]

class RefreshTokenRequest(APIRequest):
    """
        A request to refresh an existing token.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param refresh_token: the refresh token that was received with the original token
        :param client_id: application ID
        :param client_secret: application secret password

        :returns: :any:`TokenObject`
    """

    url = "https://oauth.yandex.ru/token"
    method = "POST"

    def __init__(self,
                 session: "AnySession",
                 refresh_token: str,
                 client_id: str,
                 client_secret: str, **kwargs):
        APIRequest.__init__(self, session, {"refresh_token": refresh_token,
                                            "client_id":     client_id,
                                            "client_secret": client_secret}, **kwargs)

    def process_args(self, refresh_token: str, client_id: str, client_secret: str) -> None:
        self.data = urlencode({
            "grant_type":    "refresh_token",
            "refresh_token": refresh_token,
            "client_id":     client_id,
            "client_secret": client_secret,
        }).encode("utf8")

    def process_json(self, js: Optional[dict]) -> TokenObject:
        if js is None:
            raise InvalidResponseError("Yandex.Disk did not return valid JSON")

        return TokenObject(js)

class RevokeTokenRequest(APIRequest):
    """
        A request to revoke the token.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param token: the token to be revoked
        :param client_id: application ID
        :param client_secret: application secret password

        :returns: :any:`TokenRevokeStatusObject`
    """

    url = "https://oauth.yandex.ru/revoke_token"
    method = "POST"

    def __init__(self,
                 session: "AnySession",
                 token: str,
                 client_id: str,
                 client_secret: str, **kwargs):
        APIRequest.__init__(self, session, {"token":         token,
                                            "client_id":     client_id,
                                            "client_secret": client_secret}, **kwargs)

    def process_args(self, token: str, client_id: str, client_secret: str) -> None:
        self.data = urlencode({
            "access_token":  token,
            "client_id":     client_id,
            "client_secret": client_secret
        }).encode("utf8")

    def process_json(self, js: Optional[dict]) -> TokenRevokeStatusObject:
        if js is None:
            raise InvalidResponseError("Yandex.Disk did not return valid JSON")

        return TokenRevokeStatusObject(js)

class GetTokenRequest(APIRequest):
    """
        A request to get the token.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param code: confirmation code
        :param client_id: application ID
        :param client_secret: application secret password
        :param device_id: unique device ID (between 6 and 50 characters)

        :returns: :any:`TokenObject`
    """

    url = "https://oauth.yandex.ru/token"
    method = "POST"

    def __init__(self,
                 session: "AnySession",
                 code: str,
                 client_id: str,
                 client_secret: str,
                 device_id: Optional[str] = None,
                 device_name: Optional[str] = None, **kwargs):
        APIRequest.__init__(self, session, {"code":          code,
                                            "client_id":     client_id,
                                            "client_secret": client_secret,
                                            "device_id":     device_id,
                                            "device_name":   device_name}, **kwargs)

    def process_args(self,
                     code: str,
                     client_id: str,
                     client_secret: str,
                     device_id: Optional[str],
                     device_name: Optional[str]) -> None:

        data = {}

        data["grant_type"] = "authorization_code"
        data["code"] = code
        data["client_id"] = client_id
        data["client_secret"] = client_secret

        if device_id is not None:
            data["device_id"] = device_id

        if device_name is not None:
            data["device_name"] = device_name

        self.data = urlencode(data).encode("utf8")

    def process_json(self, js: Optional[dict]) -> TokenObject:
        if js is None:
            raise InvalidResponseError("Yandex.Disk did not return valid JSON")

        return TokenObject(js)
