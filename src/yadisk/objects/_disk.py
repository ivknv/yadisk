# -*- coding: utf-8 -*-
# Copyright © 2024 Ivan Konovalov

# This file is part of a Python library yadisk.

# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published
# by the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Lesser General Public License for more details.

# You should have received a copy of the GNU Lesser General Public License
# along with this library; if not, see <http://www.gnu.org/licenses/>.

from functools import partial
from ._yadisk_object import YaDiskObject
from .._typing_compat import Dict
from .._common import str_or_error, bool_or_error, int_or_error, yandex_date

from typing import Any, Optional, NoReturn, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    import datetime

__all__ = ["DiskInfoObject", "SystemFoldersObject", "UserObject", "UserPublicInfoObject"]


class DiskInfoObject(YaDiskObject):
    """
        Disk information object.

        :param disk_info: `dict` or `None`
        :param yadisk: :any:`YaDisk` or `None`, `YaDisk` object

        :ivar paid_max_file_size: `int`, maximum supported file size for a paid account (bytes)
        :ivar max_file_size: `int`, maximum supported file size (bytes)
        :ivar total_space: `int`, total disk size (bytes)
        :ivar trash_size: `int`, amount of space used by trash (bytes), part of `used_space`
        :ivar used_space: `int`, amount of space used (bytes)
        :ivar is_paid: `bool`, tells if the account is paid or not
        :ivar is_idm_managed_folder_address_access: `bool`, not clear what this is for
        :ivar reg_time: :any:`datetime.datetime`, Disk registration date
        :ivar system_folders: :any:`SystemFoldersObject`, paths to the system folders
        :ivar user: :any:`UserObject`, owner of the disk
        :ivar is_idm_managed_public_access: `bool`, not clear what this is for
        :ivar unlimited_autoupload_enabled: `bool`, tells whether unlimited
                                             autoupload from mobile devices is enabled
        :ivar revision: `int`, current revision of Yandex.Disk
        :ivar photounlim_size: `int`, total file size in unlimited photos
        :ivar will_be_overdrawn: `bool`, tells if the user will be in overdraft upon
                                 reaching `free_photounlim_end_date`
        :ivar free_photounlim_end_date: `int`, timestamp in ms of expiration date of
                                        unlimited photo upload
        :ivar payment_flow: `bool`, tells if the user is involved in `payment_flow`
    """

    paid_max_file_size:                   Optional[int]
    max_file_size:                        Optional[int]
    total_space:                          Optional[int]
    trash_size:                           Optional[int]
    used_space:                           Optional[int]
    is_paid:                              Optional[bool]
    is_idm_managed_folder_address_access: Optional[bool]
    reg_time:                             Optional["datetime.datetime"]
    system_folders:                       "SystemFoldersObject"
    user:                                 "UserObject"
    is_idm_managed_public_access:         Optional[bool]
    unlimited_autoupload_enabled:         Optional[bool]
    revision:                             Optional[int]
    photounlim_size:                      Optional[int]
    will_be_overdrawn:                    Optional[bool]
    free_photounlim_end_date:             Optional[int]
    payment_flow:                         Optional[bool]

    def __init__(self, disk_info: Optional[Dict] = None, yadisk: Optional[Any] = None) -> None:
        YaDiskObject.__init__(
            self,
            {"paid_max_file_size":                   int_or_error,
             "max_file_size":                        int_or_error,
             "total_space":                          int_or_error,
             "trash_size":                           int_or_error,
             "used_space":                           int_or_error,
             "is_paid":                              bool_or_error,
             "is_idm_managed_folder_address_access": bool_or_error,
             "reg_time":                             yandex_date,
             "system_folders":                       partial(SystemFoldersObject, yadisk=yadisk),
             "user":                                 partial(UserObject, yadisk=yadisk),
             "is_idm_managed_public_access":         bool_or_error,
             "unlimited_autoupload_enabled":         bool_or_error,
             "revision":                             int_or_error,
             "photounlim_size":                      int_or_error,
             "will_be_overdrawn":                    bool_or_error,
             "free_photounlim_end_date":             int_or_error,
             "payment_flow":                         bool_or_error
            },
            yadisk
        )

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

    def __init__(
        self,
        system_folders: Optional[Dict] = None,
        yadisk: Optional[Any] = None
    ) -> None:
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

        :ivar reg_time: :any:`datetime.datetime`, Disk registration date
        :ivar display_name: `str`, user's display name
        :ivar uid: `str`, user's UID
        :ivar country: `str`, user's country
        :ivar is_child: `bool`, tells whether it's a child account
        :ivar login: `str`, user's login
    """

    reg_time:     Optional["datetime.datetime"]
    display_name: Optional[str]
    uid:          Optional[str]
    country:      Optional[str]
    is_child:     Optional[bool]
    login:        Optional[str]

    def __init__(
        self,
        user: Optional[Dict] = None,
        yadisk: Optional[Any] = None
    ) -> None:
        YaDiskObject.__init__(
            self,
            {
                "reg_time":     yandex_date,
                "display_name": str_or_error,
                "uid":          str_or_error,
                "country":      str_or_error,
                "is_child":     bool_or_error,
                "login":        str_or_error
            },
            yadisk
        )

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

    country: NoReturn  # pyright: ignore[reportIncompatibleVariableOverride]

    def __init__(
        self,
        public_user_info: Optional[Dict] = None,
        yadisk: Optional[Any] = None
    ) -> None:
        UserObject.__init__(self, None, yadisk)
        self.remove_field("country")
        self.import_fields(public_user_info)
