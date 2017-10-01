#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..YaDiskObject import YaDiskObject

__all__ = ["SystemFoldersObject"]

class SystemFoldersObject(YaDiskObject):
    def __init__(self, system_folders=None):
        YaDiskObject.__init__(self, {"odnoklassniki": str,
                                     "google":        str,
                                     "instagram":     str,
                                     "vkontakte":     str,
                                     "mailru":        str,
                                     "downloads":     str,
                                     "applications":  str,
                                     "facebook":      str,
                                     "social":        str,
                                     "screenshots":   str,
                                     "photostream":   str})

        self.import_fields(system_folders)
