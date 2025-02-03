# -*- coding: utf-8 -*-
# Copyright © 2024 Ivan Konovalov

# This file is part of a Python library yadisk.

# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, see <http://www.gnu.org/licenses/>.

from .api_request import APIRequest
from ..objects import TokenObject, TokenRevokeStatusObject, DeviceCodeObject
from ..exceptions import InvalidResponseError
from ..types import JSON
from .. import settings

from typing import Optional, Union, Literal, TYPE_CHECKING

from urllib.parse import urlencode

if TYPE_CHECKING:  # pragma: no cover
    from ..types import AnySession

__all__ = [
    "GetDeviceCodeRequest",
    "GetTokenRequest",
    "RefreshTokenRequest",
    "RevokeTokenRequest"
]


class RefreshTokenRequest(APIRequest):
    """
        A request to refresh an existing token.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param refresh_token: the refresh token that was received with the original token
        :param client_id: application ID
        :param client_secret: application secret password

        :returns: :any:`TokenObject`
    """

    method = "POST"
    base_url = settings.BASE_OAUTH_API_URL
    path = "/token"

    def __init__(
        self,
        session:       "AnySession",
        refresh_token: str,
        client_id:     str,
        client_secret: str,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.data = urlencode({
            "grant_type":    "refresh_token",
            "refresh_token": refresh_token,
            "client_id":     client_id,
            "client_secret": client_secret,
        }).encode("utf8")

    def process_json(self, js: JSON, **kwargs) -> TokenObject:
        if not isinstance(js, dict):
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

    method = "POST"
    base_url = settings.BASE_OAUTH_API_URL
    path = "/revoke_token"

    def __init__(
        self,
        session:       "AnySession",
        token:         str,
        client_id:     str,
        client_secret: str,
        **kwargs
    ) -> None:
        APIRequest.__init__(self, session, **kwargs)

        self.data = urlencode({
            "access_token":  token,
            "client_id":     client_id,
            "client_secret": client_secret
        }).encode("utf8")

    def process_json(self, js: JSON, **kwargs) -> TokenRevokeStatusObject:
        if not isinstance(js, dict):
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
        :param device_name: device name, should not be longer than 100 characters
        :param code_verifier: `str`, verifier code, used with the PKCE authorization flow

        :returns: :any:`TokenObject`
    """

    method = "POST"
    base_url = settings.BASE_OAUTH_API_URL
    path = "/token"

    def __init__(
        self,
        session: "AnySession",
        grant_type: Union[
            Literal["authorization_code"],
            Literal["device_code"],
            Literal["refresh_token"]
        ],
        client_id:     str,
        code:          Optional[str] = None,
        token:         Optional[str] = None,
        client_secret: Optional[str] = None,
        device_id:     Optional[str] = None,
        device_name:   Optional[str] = None,
        code_verifier: Optional[str] = None,
        **kwargs
    ):
        APIRequest.__init__(self, session, **kwargs)

        data = {
            "grant_type": grant_type,
            "client_id": client_id
        }

        if code:
            data["code"] = code

        if token:
            data["token"] = token

        if client_secret:
            data["client_secret"] = client_secret

        if device_id:
            data["device_id"] = device_id

        if device_name:
            data["device_name"] = device_name

        if code_verifier:
            data["code_verifier"] = code_verifier

        self.data = urlencode(data).encode("utf8")

    def process_json(self, js: JSON, **kwargs) -> TokenObject:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk did not return valid JSON")

        return TokenObject(js)


class GetDeviceCodeRequest(APIRequest):
    """
        This request is used for authorization using the Yandex OAuth page.
        In this case the user must enter the verification code (:code:`user_code`)
        in the browser on the Yandex OAuth page.
        After the user has entered the code on the OAuth page, the application
        can exchange the :code:`device_code` for the token.

        :param session: an instance of :any:`Session` or :any:`AsyncSession` with prepared headers
        :param client_id: application ID
        :param device_id: unique device ID (between 6 and 50 characters)
        :param device_name: device name, should not be longer than 100 characters
        :param scope: `str`, list of permissions for the application
        :param optional_scope: `str`, list of optional permissions for the application
    """

    method = "POST"
    base_url = settings.BASE_OAUTH_API_URL
    path = "/device/code"

    def __init__(
        self,
        session:        "AnySession",
        client_id:      str,
        device_id:      Optional[str] = None,
        device_name:    Optional[str] = None,
        scope:          Optional[str] = None,
        optional_scope: Optional[str] = None,
        **kwargs
    ):
        APIRequest.__init__(self, session, **kwargs)

        data = {"client_id": client_id}

        if device_id:
            data["device_id"] = device_id

        if device_name:
            data["device_name"] = device_name

        if scope:
            data["scope"] = scope

        if optional_scope:
            data["optional_scope"] = optional_scope

        self.data = urlencode(data).encode("utf8")

    def process_json(self, js: JSON, **kwargs) -> DeviceCodeObject:
        if not isinstance(js, dict):
            raise InvalidResponseError("Yandex.Disk did not return valid JSON")

        return DeviceCodeObject(js)
