#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..YaDiskObject import YaDiskObject
from .SystemFoldersObject import SystemFoldersObject

__all__ = ["DiskObject"]

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
