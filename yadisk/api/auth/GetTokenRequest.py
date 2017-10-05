#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..APIRequest import APIRequest
from ...objects import TokenObject

__all__ = ["GetTokenRequest"]

class GetTokenRequest(APIRequest):
    """
        A request to get the token.

        :param session: an instance of `requests.Session` with prepared headers
        :param code: confirmation code
        :param client_id: application ID
        :param device_id: unique device ID (between 6 and 50 characters)
    """

    url = "https://oauth.yandex.ru/token"
    method = "POST"

    def __init__(self, session, code, client_id,
                 device_id=None, device_name=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"code":          code,
                                            "client_id":     client_id,
                                            "device_id":     device_id,
                                            "device_name":   device_name}, *args, **kwargs)

    def process_args(self, code, client_id, device_id, device_name):
        self.data["grant_type"] = "authorization_code"
        self.data["code"] = code
        self.data["client_id"] = client_id

        if device_id is not None:
            self.data["device_id"] = device_id

        if device_name is not None:
            self.data["device_name"] = device_name

    def process_json(self, js):
        return TokenObject(js)
