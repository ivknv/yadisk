#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ...APIRequest import APIRequest
from ....objects import TrashResourceObject

__all__ = ["GetTrashRequest"]

class GetTrashRequest(APIRequest):
    url = "https://cloud-api.yandex.net/v1/disk/trash/resources"
    method = "GET"

    def __init__(self, session, path=None, offset=0, limit=20, sort=None,
                 preview_size=None, preview_crop=None, fields=None, *args, **kwargs):
        APIRequest.__init__(self, session, {"path":         path,
                                            "offset":       offset,
                                            "limit":        limit,
                                            "sort":         sort,
                                            "preview_size": preview_size,
                                            "preview_crop": preview_crop,
                                            "fields":       fields}, *args, **kwargs)

    def process_args(self, path, offset, limit, sort, preview_size, preview_crop, fields):
        self.params["path"] = path
        self.params["offset"] = offset
        self.params["limit"] = limit

        if sort is not None:
            self.params["sort"] = sort

        if preview_size is not None:
            self.params["preview_size"] = preview_size

        if preview_crop is not None:
            self.params["preview_crop"] = preview_crop

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return TrashResourceObject(js)
