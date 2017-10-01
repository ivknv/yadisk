#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..APIRequest import APIRequest
from ...objects import PublicResourcesListObject

__all__ = ["GetPublicResourcesRequest"]

class GetPublicResourcesRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/resources/public"
    method = "GET"

    def __init__(self, session, offset=0, limit=20, preview_size=None,
                 preview_crop=None, type=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"offset":       offset,
                                            "limit":        limit,
                                            "preview_size": preview_size,
                                            "preview_crop": preview_crop,
                                            "type":         type}, *args, **kwargs)

    def process_args(self, offset, limit, preview_size, preview_crop, type):
        self.params["offset"] = offset
        self.params["limit"] = limit

        if preview_size is not None:
            self.params["preview_size"] = preview_size

        if preview_crop is not None:
            self.params["preview_crop"] = preview_crop

        if type is not None:
            self.params["type"] = type

    def process_json(self, js):
        return PublicResourcesListObject(js)
