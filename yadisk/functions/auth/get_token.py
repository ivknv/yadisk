#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

from ...api import GetTokenRequest

__all__ = ["get_token"]

def get_token(code, client_id, client_secret, *args, **kwargs):
    session = requests.Session()
    request = GetTokenRequest(session, code, client_id, client_secret, *args, **kwargs)
    request.send()

    return request.process()
