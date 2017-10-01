#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..APIRequest import APIRequest
from ...objects import ResourceObject

__all__ = ["GetMetaRequest"]

class GetMetaRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/resources"
    method = "GET"

    def __init__(self, session, path, limit=None, offset=None,
                 preview_size=None, preview_crop=None, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session,
                            {"path":         path,
                             "limit":        limit,
                             "offset":       offset,
                             "preview_size": preview_size,
                             "preview_crop": preview_crop,
                             "fields":       fields}, *args, **kwargs)

    def process_args(self, path, limit, offset, preview_size, preview_crop, fields):
        self.params["path"] = path

        if limit is not None:
            self.params["limit"] = limit

        if offset is not None:
            self.params["offset"] = offset

        if preview_size is not None:
            self.params["preview_size"] = preview_size

        if preview_crop is not None:
            self.params["preview_crop"] = "true" if preview_crop else "false"

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return ResourceObject(js)
