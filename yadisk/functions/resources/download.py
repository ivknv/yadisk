#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

from ...api.APIRequest import APIRequest
from .get_download_link import get_download_link

__all__ = ["download"]

def download(session, src_path, file_or_path, *args, **kwargs):
    link = get_download_link(session, src_path, *args, **kwargs)

    n_retries = kwargs.get("n_retries", APIRequest.n_retries)

    if isinstance(file_or_path, (str, bytes)):
        file = open(file_or_path, "wb")
        close_file = True
    else:
        file = file_or_path
        close_file = False

    file_position = file.tell()

    try:
        for i in range(n_retries + 1):
            file.seek(file_position)

            try:
                response = requests.get(link, data=file, *args, **kwargs)

                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)

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

    return response.status_code == 200
