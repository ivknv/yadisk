#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..APIRequest import APIRequest
from ...objects import FilesResourceListObject

__all__ = ["FilesRequest"]

class FilesRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/resources/files"
    method = "GET"

    def __init__(self, session, offset=0, limit=20, media_type=None,
                 preview_size=None, preview_crop=None, sort=None, fields=None,
                 *args, **kwargs):
        APIRequest.__init__(self, session, {"offset":       offset,
                                            "limit":        limit,
                                            "media_type":   media_type,
                                            "sort":         sort,
                                            "preview_size": preview_size,
                                            "preview_crop": preview_crop,
                                            "fields":       fields}, *args, **kwargs)

    def process_args(self, offset, limit, media_type, sort, preview_size, preview_crop, fields):
        self.params["offset"] = offset
        self.params["limit"] = limit

        if media_type is not None:
            self.params["media_type"] = media_type

        if preview_size is not None:
            self.params["preview_size"] = preview_size

        if preview_crop is not None:
            self.params["preview_crop"] = preview_crop

        if sort is not None:
            self.params["sort"] = sort

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return FilesResourceListObject(js)
