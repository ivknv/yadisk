#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

__all__ = ["get_auth_url"]

def get_auth_url(client_id, device_id=None, device_name=None, display="popup",
                 login_hint=None, scope=None, optional_scope=None, force_confirm=True,
                 state=None):
    params = {"response_type": "token",
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
        params["scope"] = scope

    if optional_scope is not None:
        params["optional_scope"] = optional_scope

    if state is not None:
        params["state"] = state

    return "https://oauth.yandex.ru/authorize?" + urlencode(params)
