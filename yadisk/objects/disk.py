# -*- coding: utf-8 -*-

from .yadisk_object import YaDiskObject

__all__ = ["DiskInfoObject", "SystemFoldersObject", "UserObject", "UserPublicInfoObject"]

class DiskInfoObject(YaDiskObject):
    """
        Disk information object.

        :param disk_info: `dict` or `None`

        :ivar max_file_size: `int`, maximum supported file size (bytes)
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

    def __init__(self, disk_info=None):
        YaDiskObject.__init__(self, {"max_file_size":  int,
                                     "unlimited_autoupload_enabled": bool,
                                     "total_space":    int,
                                     "trash_size":     int,
                                     "is_paid":        bool,
                                     "used_space":     int,
                                     "system_folders": SystemFoldersObject,
                                     "user":           UserObject,
                                     "revision":       int})

        self.import_fields(disk_info)

class SystemFoldersObject(YaDiskObject):
    """
        Object, containing paths to system folders.

        :param system_folders: `dict` or `None`

        :ivar odnoklassniki: `str`, path to the Odnoklassniki folder
        :ivar google: `str`, path to the Google+ folder
        :ivar instagram: `str`, path to the Instagram folder
        :ivar vkontakte: `str`, path to the VKontakte folder
        :ivar mailru: `str`, path to the My World folder
        :ivar facebook: `str`, path to the Facebook folder
        :ivar social: `str`, path to the social networks folder
        :ivar screenshots: `str`, path to the screenshot folder
        :ivar photostream: `str`, path to the camera folder
    """

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

class UserObject(YaDiskObject):
    """
        User object.

        :param user: `dict` or `None`

        :ivar country: `str`, user's country
        :ivar login: `str`, user's login
        :ivar display_name: `str`, user's display name
        :ivar uid: `str`, user's UID
    """

    def __init__(self, user=None):
        YaDiskObject.__init__(self, {"country":      str,
                                     "login":        str,
                                     "display_name": str,
                                     "uid":          str})

        self.import_fields(user)

class UserPublicInfoObject(UserObject):
    """
        Public user information object.
        Inherits from :any:`UserObject` for compatibility.

        :param public_user_info: `dict` or `None`

        :ivar login: `str`, user's login
        :ivar display_name: `str`, user's display name
        :ivar uid: `str`, user's UID
    """

    def __init__(self, public_user_info=None):
        UserObject.__init__(self, public_user_info)
        self.remove_field("country")
        self.import_fields(public_user_info)
