# -*- coding: utf-8 -*-

from .yadisk_object import YaDiskObject

from typing import Any, Optional

from ..common import str_or_error, bool_or_error

__all__ = ["LinkObject"]

class LinkObject(YaDiskObject):
    """
        Link object.

        :param link: `dict` or `None`
        :param yadisk: :any:`Client`/:any:`AsyncClient` or `None`, `YaDisk` object

        :ivar href: `str`, link URL
        :ivar method: `str`, HTTP method
        :ivar templated: `bool`, tells whether the URL is templated
    """

    href: Optional[str]
    method: Optional[str]
    templated: Optional[bool]

    def __init__(self,
                 link: Optional[dict] = None,
                 yadisk: Optional[Any] = None):
        YaDiskObject.__init__(
            self,
            {"href":      str_or_error,
             "method":    str_or_error,
             "templated": bool_or_error},
            yadisk)

        self.import_fields(link)
