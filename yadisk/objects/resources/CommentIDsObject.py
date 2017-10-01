#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..YaDiskObject import YaDiskObject

__all__ = ["CommentIDsObject"]

class CommentIDsObject(YaDiskObject):
    def __init__(self, comment_ids=None):
        YaDiskObject.__init__(self, {"private_resource": str,
                                     "public_resource":  str})

        self.import_fields(comment_ids)
