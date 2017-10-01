#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ...APIRequest import APIRequest
from ....objects import LinkObject

__all__ = ["GetPublicMetaRequest"]

class GetPublicMetaRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/public/resources"
    method = "GET"

    def __init__(self, session, public_key, offset=0, limit=20, path=None,
                 sort=None, preview_size=None, preview_crop=None, fields=None,
                 *args, **kwargs):
        APIRequest.__init__(self, session, {"public_key":   public_key,
                                            "offset":       offset,
                                            "limit":        limit,
                                            "path":         path,
                                            "sort":         sort,
                                            "preview_size": preview_size,
                                            "preview_crop": preview_crop,
                                            "fields":       fields}, *args, **kwargs)

    def process_args(self, public_key, offset, limit, path,
                     sort, preview_size, preview_crop, fields):
        self.params["public_key"] = public_key
        self.params["offset"] = offset
        self.params["limit"] = limit
        
        if path is not None:
            self.params["path"] = path

        if sort is not None:
            self.params["sort"] = sort

        if preview_size is not None:
            self.params["preview_size"] = preview_size

        if preview_crop is not None:
            self.params["preview_crop"] = preview_crop

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return LinkObject(js)
