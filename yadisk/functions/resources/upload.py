#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

import requests

from ...api.APIRequest import APIRequest
from .get_upload_link import get_upload_link

__all__ = ["upload"]

def upload(session, file_or_path, dst_path, overwrite=False, fields=None, *args, **kwargs):
    link = get_upload_link(session, dst_path, overwrite=overwrite, fields=fields, *args, **kwargs)

    kwargs = dict(kwargs)
    kwargs.setdefault("timeout", (APIRequest.timeout[0], 60))
    n_retries = kwargs.get("n_retries", APIRequest.n_retries)
    retry_interval = kwargs.get("retry_interval", 3.0)

    if isinstance(file_or_path, (str, bytes)):
        file = open(file_or_path, "rb")
        close_file = True
    else:
        file = file_or_path
        close_file = False

    file_position = file.tell()

    try:
        for i in range(n_retries + 1):
            file.seek(file_position)

            if i > 0:
                time.sleep(retry_interval)

            try:
                response = requests.put(link, data=file, stream=True, *args, **kwargs)
            except requests.exceptions.RequestException as e:
                if i == n_retries:
                    raise e

                continue

            if response.status_code in APIRequest.retry_codes:
                continue

            break
    finally:
        if close_file:
            file.close()

    return response.status_code == 201
