#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .YaDiskObject import YaDiskObject

__all__ = ["DiskObject", "SystemFoldersObject"]

class DiskObject(YaDiskObject):
    def __init__(self, disk=None):
        YaDiskObject.__init__(self, {"max_file_size":  int,
                                     "total_space":    int,
                                     "trash_size":     int,
                                     "is_paid":        bool,
                                     "used_space":     int,
                                     "system_folders": SystemFoldersObject,
                                     "revision":       int})

        self.import_fields(disk)

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
