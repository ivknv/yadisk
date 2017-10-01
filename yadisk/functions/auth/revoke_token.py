#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

from ...api import RevokeTokenRequest

__all__ = ["revoke_token"]

def revoke_token(token, client_id, client_secret, *args, **kwargs):
    session = requests.Session()
    request = RevokeTokenRequest(session, token, client_id, client_secret, *args, **kwargs)

    request.send()

    return request.process()
