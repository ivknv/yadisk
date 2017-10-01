#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .YaDiskObject import YaDiskObject

__all__ = ["ErrorObject"]

class ErrorObject(YaDiskObject):
    def __init__(self, error=None):
        YaDiskObject.__init__(self, {"message":     str,
                                     "description": str,
                                     "error":       str})
        self.import_fields(error)

        if self.message is None and error is not None:
            self.message = error.get("error_description")
