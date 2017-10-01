#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..APIRequest import APIRequest
from ...objects import TokenObject

__all__ = ["RefreshTokenRequest"]

class RefreshTokenRequest(APIRequest):
    url = "https://oauth.yandex.ru/token"
    method = "POST"

    def __init__(self, session, refresh_token, client_id, client_secret, *args, **kwargs):
        APIRequest.__init__(self, session, {"refresh_token": refresh_token,
                                            "client_id":     client_id,
                                            "client_secret": client_secret}, *args, **kwargs)

    def process_args(self, refresh_token, client_id, client_secret):
        self.data["grant_type"] = "refresh_token"
        self.data["refresh_token"] = refresh_token
        self.data["client_id"] = client_id
        self.data["client_secret"] = client_secret

    def process_json(self, js):
        return TokenObject(js)
