#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..YaDiskObject import YaDiskObject
from ...common import yandex_date

__all__ = ["EXIFObject"]

class EXIFObject(YaDiskObject):
    def __init__(self, exif=None):
        YaDiskObject.__init__(self, {"date_time": yandex_date})

        self.import_fields(exif)
