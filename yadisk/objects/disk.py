#!/usr/bin/env python
# -*- coding: utf-8 -*-

from .YaDiskObject import YaDiskObject

__all__ = ["DiskInfoObject", "SystemFoldersObject", "UserObject"]

class DiskInfoObject(YaDiskObject):
    """
        Disk information object.

        :param disk_info: `dict` or `None`

        max_file_size
            `int`, maximum supported file size (bytes)
        total_space
            `int`, total disk size (bytes)
        trash_size
            `int`, amount of space used by trash (bytes), part of `used_space`
        is_paid
            `bool`, tells if the account is paid or not
        used_space
            `int`, amount of space used (bytes)
        system_folders
            `SystemFoldersObject`, paths to the system folders
        user
            `UserObject`, owner of the disk
        revision
            `int`, current revision of Yandex.Disk
    """

    def __init__(self, disk_info=None):
        YaDiskObject.__init__(self, {"max_file_size":  int,
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

        odnoklassniki
            `str`, path to the Odnoklassniki folder
        google
            `str`, path to the Google+ folder
        instagram
            `str`, path to the Instagram folder
        vkontakte
            `str`, path to the VKontakte folder
        mailru
            `str`, path to the My World folder
        facebook
            `str`, path to the Facebook folder
        social
            `str`, path to the social networks folder
        screenshots
            `str`, path to the screenshot folder
        photostream
            `str`, path to the camera folder
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

        login
            `str`, user's login
        display_name
            `str`. user's display name
        uid
            `str`, user's UID
    """

    def __init__(self, user=None):
        YaDiskObject.__init__(self, {"login":        str,
                                     "display_name": str,
                                     "uid":          str})

        self.import_fields(user)
