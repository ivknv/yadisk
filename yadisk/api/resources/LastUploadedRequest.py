#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections

from ..APIRequest import APIRequest
from ...objects import LastUploadedResourceListObject

__all__ = ["LastUploadedRequest"]

class LastUploadedRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/resources/last-uploaded"
    method = "GET"

    def __init__(self, session, limit=20, media_type=None, preview_size=None,
                 preview_crop=None, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"limit":        limit,
                                            "media_type":   media_type,
                                            "preview_size": preview_size,
                                            "preview_crop": preview_crop,
                                            "fields":       fields}, *args, **kwargs)

    def process_args(self, limit, media_type, preview_size, preview_crop, fields):
        self.params["limit"] = limit

        if media_type is not None:
            if not isinstance(media_type, collections.Iterable):
                raise TypeError("media_type should be a string or an iterable")

            if isinstance(media_type, str):
                self.params["media_type"] = media_type
            else:
                self.params["media_type"] = ",".join(media_type)

        if preview_size is not None:
            self.params["preview_size"] = preview_size

        if preview_crop is not None:
            self.params["preview_crop"] = preview_crop

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return LastUploadedResourceListObject(js)
