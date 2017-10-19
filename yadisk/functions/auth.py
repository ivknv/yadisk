#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

import requests

from .disk import get_disk_info
from ..api import GetTokenRequest, RefreshTokenRequest, RevokeTokenRequest
from ..exceptions import UnauthorizedError

__all__ = ["check_token", "get_auth_url", "get_code_url", "get_token",
           "refresh_token", "revoke_token"]

def check_token(session, *args, **kwargs):
    """
        Check whether the token is valid.

        :param session: an instance of `requests.Session` with prepared headers

        :returns: `bool`
    """

    try:
        get_disk_info(session, *args, **kwargs)
        return True
    except UnauthorizedError:
        return False

def get_auth_url(client_id, type="code", device_id=None, device_name=None, display="popup",
                 login_hint=None, scope=None, optional_scope=None, force_confirm=True,
                 state=None):
    """
        Get authentication URL for the user to go to.

        :param client_id: application ID
        :param type: response type ("code" to get the confirmation code or "token" to get the token automatically)
        :param device_id: unique device ID, must be between 6 and 50 characters
        :param device_name: device name, should not be longer than 100 characters
        :param display: indicates whether to use lightweight layout, values other than "popup" are ignored
        :param login_hint: username or email for the account the token is being requested for
        :param scope: list of permissions for the application
        :param optional_scope: list of optional permissions for the application
        :param force_confirm: if True, user will be required to confirm access to the account
                              even if the user has already granted access for the application
        :param state: The state string, which Yandex.OAuth returns without any changes (<= 1024 characters)

        :returns: authentication URL
    """

    if type not in {"code", "token"}:
        raise ValueError("type must be either 'code' or 'token'")

    params = {"response_type": type,
              "client_id":     client_id,
              "display":       display,
              "force_confirm": "yes" if force_confirm else "no"}

    if device_id is not None:
        params["device_id"] = device_id

    if device_name is not None:
        params["device_name"] = device_name

    if login_hint is not None:
        params["login_hint"] = login_hint

    if scope is not None:
        params["scope"] = " ".join(scope)

    if optional_scope is not None:
        params["optional_scope"] = " ".join(optional_scope)

    if state is not None:
        params["state"] = state

    return "https://oauth.yandex.ru/authorize?" + urlencode(params)

def get_code_url(client_id, *args, **kwargs):
    """
        Get the URL for the user to get the confirmation code.
        The confirmation code can later be used to get the token.

        :param client_id: application ID
        :param device_id: unique device ID, must be between 6 and 50 characters
        :param device_name: device name, should not be longer than 100 characters
        :param display: indicates whether to use lightweight layout, values other than "popup" are ignored
        :param login_hint: username or email for the account the token is being requested for
        :param scope: list of permissions for the application
        :param optional_scope: list of optional permissions for the application
        :param force_confirm: if True, user will be required to confirm access to the account
                              even if the user has already granted access for the application
        :param state: The state string, which Yandex.OAuth returns without any changes (<= 1024 characters)

        :returns: authentication URL
    """

    return get_auth_url(client_id, type="code", *args, **kwargs)

def get_token(code, client_id, client_secret, *args, **kwargs):
    """
        Get a new token.

        :param code: confirmation code
        :param client_id: application ID
        :param client_secret: application secret password
        :param device_id: unique device ID (between 6 and 50 characters)

        :returns: `TokenObject`
    """

    session = requests.Session()
    request = GetTokenRequest(session, code, client_id, client_secret, *args, **kwargs)
    request.send()

    return request.process()

def refresh_token(session, refresh_token, client_id, client_secret, *args, **kwargs):
    """
        Refresh an existing token.

        :param session: an instance of `requests.Session` with prepared headers
        :param refresh_token: the refresh token that was receieved with the token
        :param client_id: application ID
        :param client_secret: application secret password

        :returns: `TokenObject`
    """

    request = RefreshTokenRequest(session, refresh_token, client_id, client_secret, *args, **kwargs)
    request.send()

    return request.process()

def revoke_token(token, client_id, client_secret, *args, **kwargs):
    """
        Revoke the token.

        :param token: token to revoke
        :param client_id: application ID
        :param client_secret: application secret password

        :returns: `TokenRevokeStatusObject`
    """

    session = requests.Session()
    request = RevokeTokenRequest(session, token, client_id, client_secret, *args, **kwargs)

    request.send()

    return request.process()
