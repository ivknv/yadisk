#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

__all__ = ["get_auth_url"]

def get_auth_url(client_id):
    return "https://oauth.yandex.ru/authorize?" + urlencode({"response_type": "code",
                                                              "client_id": client_id})
