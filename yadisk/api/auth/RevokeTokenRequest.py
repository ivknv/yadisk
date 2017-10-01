#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..APIRequest import APIRequest
from ...objects import TokenRevokeStatus

__all__ = ["RevokeTokenRequest"]

class RevokeTokenRequest(APIRequest):
    url = "https://oauth.yandex.ru/revoke_token"
    method = "POST"

    def __init__(self, session, token, client_id, client_secret, *args, **kwargs):
        APIRequest.__init__(self, session, {"token":         token,
                                            "client_id":     client_id,
                                            "client_secret": client_secret}, *args, **kwargs)

    def process_args(self, token, client_id, client_secret):
        self.data["access_token"] = token
        self.data["client_id"] = client_id
        self.data["client_secret"] = client_secret

    def process_json(self, js):
        return TokenRevokeStatus(js)
