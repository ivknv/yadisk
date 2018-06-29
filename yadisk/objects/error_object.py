# -*- coding: utf-8 -*-

from .yadisk_object import YaDiskObject

__all__ = ["ErrorObject"]

class ErrorObject(YaDiskObject):
    """
        Mirrors Yandex.Disk REST API error object.

        :param error: `dict` or `None`

        :ivar message: `str`, human-readable error message
        :ivar description: `str`, technical error description
        :ivar error: `str`, error code
    """

    def __init__(self, error=None):
        YaDiskObject.__init__(self, {"message":     str,
                                     "description": str,
                                     "error":       str})
        self.set_alias("error_description", "message")
        self.import_fields(error)
