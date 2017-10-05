#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..APIRequest import APIRequest
from ...objects import TokenRevokeStatusObject

__all__ = ["RevokeTokenRequest"]

class RevokeTokenRequest(APIRequest):
    """
        A request to revoke the token.

        :param session: an instance of `requests.Session` with prepared headers
        :param token: the token to be revoked
        :param client_id: application ID
        :param client_secret: application secret password
    """

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
        return TokenRevokeStatusObject(js)
