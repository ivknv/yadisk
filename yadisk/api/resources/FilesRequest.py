#!/usr/bin/env python
# -*- coding: utf-8 -*-

import collections

from ..APIRequest import APIRequest
from ...objects import FilesResourceListObject

__all__ = ["FilesRequest"]

class FilesRequest(APIRequest):
    """
        A request to get a flat list of all files (that doesn't include directories).

        :param session: an instance of `requests.Session` with prepared headers
        :param offset: offset from the beginning of the list
        :param limit: number of list elements to be included
        :param media_type: type of files to include in the list
        :param sort: sort type
    """

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

        if sort is not None:
            self.params["sort"] = sort

        if fields is not None:
            self.params["fields"] = ",".join(fields)

    def process_json(self, js):
        return FilesResourceListObject(js)
