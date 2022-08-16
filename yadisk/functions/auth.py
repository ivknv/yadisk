# -*- coding: utf-8 -*-

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

import requests

from .operations import get_operation_status
from ..api import GetTokenRequest, RefreshTokenRequest, RevokeTokenRequest
from ..exceptions import UnauthorizedError, OperationNotFoundError

__all__ = ["check_token", "get_auth_url", "get_code_url", "get_token",
           "refresh_token", "revoke_token"]

def check_token(session, **kwargs):
    """
        Check whether the token is valid.

        :param session: an instance of :any:`requests.Session` with prepared headers

        :returns: `bool`
    """

    # Any ID will do, doesn't matter whether it exists or not
    fake_operation_id = "0000"

    try:
        # get_operation_status() doesn't require any permissions, unlike most other requests
        get_operation_status(session, fake_operation_id, **kwargs)
        return True
    except UnauthorizedError:
        return False
    except OperationNotFoundError:
        return True

def get_auth_url(client_id, **kwargs):
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

    type           = kwargs.get("type")
    device_id      = kwargs.get("device_id")
    device_name    = kwargs.get("device_name")
    display        = kwargs.get("display", "popup")
    login_hint     = kwargs.get("login_hint")
    scope          = kwargs.get("scope")
    optional_scope = kwargs.get("optional_scope")
    force_confirm  = kwargs.get("force_confirm", True)
    state          = kwargs.get("state")

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

def get_code_url(client_id, **kwargs):
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

    kwargs = dict(kwargs)
    kwargs["type"] = "code"

    return get_auth_url(client_id, **kwargs)

def get_token(code, client_id, client_secret, **kwargs):
    """
        Get a new token.

        :param code: confirmation code
        :param client_id: application ID
        :param client_secret: application secret password
        :param device_id: unique device ID (between 6 and 50 characters)
        :param timeout: `float` or `tuple`, request timeout
        :param headers: `dict` or `None`, additional request headers
        :param n_retries: `int`, maximum number of retries
        :param retry_interval: delay between retries in seconds

        :returns: :any:`TokenObject`
    """

    with requests.Session() as session:
        request = GetTokenRequest(session, code, client_id, client_secret, **kwargs)
        request.send()

        return request.process()

def refresh_token(refresh_token, client_id, client_secret, **kwargs):
    """
        Refresh an existing token.

        :param refresh_token: the refresh token that was received with the token
        :param client_id: application ID
        :param client_secret: application secret password
        :param timeout: `float` or `tuple`, request timeout
        :param headers: `dict` or `None`, additional request headers
        :param n_retries: `int`, maximum number of retries
        :param retry_interval: delay between retries in seconds

        :returns: :any:`TokenObject`
    """

    with requests.Session() as session:
        request = RefreshTokenRequest(session, refresh_token,
                                      client_id, client_secret, **kwargs)
        request.send()

        return request.process()

def revoke_token(token, client_id, client_secret, **kwargs):
    """
        Revoke the token.

        :param token: token to revoke
        :param client_id: application ID
        :param client_secret: application secret password
        :param timeout: `float` or `tuple`, request timeout
        :param headers: `dict` or `None`, additional request headers
        :param n_retries: `int`, maximum number of retries
        :param retry_interval: delay between retries in seconds

        :returns: :any:`TokenRevokeStatusObject`
    """

    with requests.Session() as session:
        request = RevokeTokenRequest(session, token,
                                     client_id, client_secret, **kwargs)
        request.send()

        return request.process()
