#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

from ...api import RefreshTokenRequest

__all__ = ["refresh_token"]

def refresh_token(session, refresh_token, client_id, client_secret, *args, **kwargs):
    request = RefreshTokenRequest(session, refresh_token, client_id, client_secret, *args, **kwargs)
    request.send()

    return request.process()
