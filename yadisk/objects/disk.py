# -*- coding: utf-8 -*-

from functools import partial
from .yadisk_object import YaDiskObject
from ..common import str_or_error, bool_or_error, int_or_error

from typing import Optional, NoReturn, TYPE_CHECKING

if TYPE_CHECKING:
    from ..yadisk import YaDisk

__all__ = ["DiskInfoObject", "SystemFoldersObject", "UserObject", "UserPublicInfoObject"]

class DiskInfoObject(YaDiskObject):
    """
        Disk information object.

        :param disk_info: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar max_file_size: `int`, maximum supported file size (bytes)
        :ivar paid_max_file_size: `int`, maximum supported file size for a paid account (bytes)
        :ivar unlimited_autoupload_enabled: `bool`, tells whether unlimited
                                             autoupload from mobile devices is enabled
        :ivar total_space: `int`, total disk size (bytes)
        :ivar trash_size: `int`, amount of space used by trash (bytes), part of `used_space`
        :ivar is_paid: `bool`, tells if the account is paid or not
        :ivar used_space: `int`, amount of space used (bytes)
        :ivar system_folders: :any:`SystemFoldersObject`, paths to the system folders
        :ivar user: :any:`UserObject`, owner of the disk
        :ivar revision: `int`, current revision of Yandex.Disk
    """

    max_file_size:                Optional[int]
    paid_max_file_size:           Optional[int]
    unlimited_autoupload_enabled: Optional[bool]
    total_space:                  Optional[int]
    trash_size:                   Optional[int]
    is_paid:                      Optional[bool]
    used_space:                   Optional[int]
    system_folders:               "SystemFoldersObject"
    user:                         "UserObject"
    revision:                     Optional[int]

    def __init__(self, disk_info: Optional[dict] = None, yadisk: Optional["YaDisk"] = None):
        YaDiskObject.__init__(
            self,
            {"max_file_size":                int_or_error,
             "paid_max_file_size":           int_or_error,
             "unlimited_autoupload_enabled": bool_or_error,
             "total_space":                  int_or_error,
             "trash_size":                   int_or_error,
             "is_paid":                      bool_or_error,
             "used_space":                   int_or_error,
             "system_folders":               partial(SystemFoldersObject, yadisk=yadisk),
             "user":                         partial(UserObject, yadisk=yadisk),
             "revision":                     int_or_error},
            yadisk)

        self.import_fields(disk_info)

class SystemFoldersObject(YaDiskObject):
    """
        Object, containing paths to system folders.

        :param system_folders: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar odnoklassniki: `str`, path to the Odnoklassniki folder
        :ivar google: `str`, path to the Google+ folder
        :ivar instagram: `str`, path to the Instagram folder
        :ivar vkontakte: `str`, path to the VKontakte folder
        :ivar attach: `str`, path to the mail attachments folder
        :ivar mailru: `str`, path to the My World folder
        :ivar downloads: `str`, path to the Downloads folder
        :ivar applications: `str` path to the Applications folder
        :ivar facebook: `str`, path to the Facebook folder
        :ivar social: `str`, path to the social networks folder
        :ivar messenger: `str`, path to the Messenger Files folder
        :ivar calendar: `str`, path to the Meeting Materials folder
        :ivar photostream: `str`, path to the camera folder
        :ivar screenshots: `str`, path to the screenshot folder
        :ivar scans: `str`, path to the Scans folder
    """

    odnoklassniki: Optional[str]
    google:        Optional[str]
    instagram:     Optional[str]
    vkontakte:     Optional[str]
    attach:        Optional[str]
    mailru:        Optional[str]
    downloads:     Optional[str]
    applications:  Optional[str]
    facebook:      Optional[str]
    social:        Optional[str]
    messenger:     Optional[str]
    calendar:      Optional[str]
    photostream:   Optional[str]
    screenshots:   Optional[str]
    scans:         Optional[str]

    def __init__(self,
                 system_folders: Optional[dict] = None,
                 yadisk: Optional["YaDisk"] = None):
        YaDiskObject.__init__(
            self,
            {"odnoklassniki": str_or_error,
             "google":        str_or_error,
             "instagram":     str_or_error,
             "vkontakte":     str_or_error,
             "attach":        str_or_error,
             "mailru":        str_or_error,
             "downloads":     str_or_error,
             "applications":  str_or_error,
             "facebook":      str_or_error,
             "social":        str_or_error,
             "messenger":     str_or_error,
             "calendar":      str_or_error,
             "photostream":   str_or_error,
             "screenshots":   str_or_error,
             "scans":         str_or_error},
            yadisk)

        self.import_fields(system_folders)

class UserObject(YaDiskObject):
    """
        User object.

        :param user: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar country: `str`, user's country
        :ivar login: `str`, user's login
        :ivar display_name: `str`, user's display name
        :ivar uid: `str`, user's UID
    """

    country: Optional[str]
    login: Optional[str]
    display_name: Optional[str]
    uid: Optional[str]

    def __init__(self, user: Optional[dict] = None, yadisk: Optional["YaDisk"] = None):
        YaDiskObject.__init__(
            self,
            {"country":      str_or_error,
             "login":        str_or_error,
             "display_name": str_or_error,
             "uid":          str_or_error},
            yadisk)

        self.import_fields(user)

class UserPublicInfoObject(UserObject):
    """
        Public user information object.
        Inherits from :any:`UserObject` for compatibility.

        :param public_user_info: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar login: `str`, user's login
        :ivar display_name: `str`, user's display name
        :ivar uid: `str`, user's UID
    """

    country: NoReturn

    def __init__(self,
                 public_user_info: Optional[dict] = None,
                 yadisk: Optional["YaDisk"] = None):
        UserObject.__init__(self, None, yadisk)
        self.remove_field("country")
        self.import_fields(public_user_info)
