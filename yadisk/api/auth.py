# -*- coding: utf-8 -*-

from .api_request import APIRequest
from ..objects import TokenObject, TokenRevokeStatusObject
from ..exceptions import InvalidResponseError

from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import requests

__all__ = ["RefreshTokenRequest", "RevokeTokenRequest", "GetTokenRequest"]

class RefreshTokenRequest(APIRequest):
    """
        A request to refresh an existing token.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param refresh_token: the refresh token that was received with the original token
        :param client_id: application ID
        :param client_secret: application secret password

        :returns: :any:`TokenObject`
    """

    url = "https://oauth.yandex.ru/token"
    method = "POST"

    def __init__(self,
                 session: "requests.Session",
                 refresh_token: str,
                 client_id: str,
                 client_secret: str, **kwargs):
        APIRequest.__init__(self, session, {"refresh_token": refresh_token,
                                            "client_id":     client_id,
                                            "client_secret": client_secret}, **kwargs)

    def process_args(self, refresh_token: str, client_id: str, client_secret: str) -> None:
        self.data["grant_type"] = "refresh_token"
        self.data["refresh_token"] = refresh_token
        self.data["client_id"] = client_id
        self.data["client_secret"] = client_secret

    def process_json(self, js: Optional[dict]) -> TokenObject:
        if js is None:
            raise InvalidResponseError("Yandex.Disk did not return valid JSON")

        return TokenObject(js)

class RevokeTokenRequest(APIRequest):
    """
        A request to revoke the token.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param token: the token to be revoked
        :param client_id: application ID
        :param client_secret: application secret password

        :returns: :any:`TokenRevokeStatusObject`
    """

    url = "https://oauth.yandex.ru/revoke_token"
    method = "POST"

    def __init__(self,
                 session: "requests.Session",
                 token: str,
                 client_id: str,
                 client_secret: str, **kwargs):
        APIRequest.__init__(self, session, {"token":         token,
                                            "client_id":     client_id,
                                            "client_secret": client_secret}, **kwargs)

    def process_args(self, token: str, client_id: str, client_secret: str) -> None:
        self.data["access_token"] = token
        self.data["client_id"] = client_id
        self.data["client_secret"] = client_secret

    def process_json(self, js: Optional[dict]) -> TokenRevokeStatusObject:
        if js is None:
            raise InvalidResponseError("Yandex.Disk did not return valid JSON")

        return TokenRevokeStatusObject(js)

class GetTokenRequest(APIRequest):
    """
        A request to get the token.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param code: confirmation code
        :param client_id: application ID
        :param client_secret: application secret password
        :param device_id: unique device ID (between 6 and 50 characters)

        :returns: :any:`TokenObject`
    """

    url = "https://oauth.yandex.ru/token"
    method = "POST"

    def __init__(self,
                 session: "requests.Session",
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
        self.data["grant_type"] = "authorization_code"
        self.data["code"] = code
        self.data["client_id"] = client_id
        self.data["client_secret"] = client_secret

        if device_id is not None:
            self.data["device_id"] = device_id

        if device_name is not None:
            self.data["device_name"] = device_name

    def process_json(self, js: Optional[dict]) -> TokenObject:
        if js is None:
            raise InvalidResponseError("Yandex.Disk did not return valid JSON")

        return TokenObject(js)
