#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ["YaDiskError", "UnknownYaDiskError", "UnauthorizedError",
           "DiskNotFoundError", "PathNotFoundError", "DirectoryExistsError",
           "PathExistsError"]

class YaDiskError(BaseException):
    def __init__(self, error_type=None, msg=""):
        BaseException.__init__(self, msg)

        self.error_type = error_type

class UnknownYaDiskError(YaDiskError):
    def __init__(self, msg=""):
        YaDiskError.__init__(self, None, msg)

class UnauthorizedError(YaDiskError):
    error_type = "UnauthorizedError"

    def __init__(self, msg=""):
        YaDiskError.__init__(self, UnauthorizedError.error_type, msg)

class DiskNotFoundError(YaDiskError):
    error_type = "DiskNotFoundError"

    def __init__(self, msg=""):
        YaDiskError.__init__(self, DiskNotFoundError.error_type, msg)

class PathNotFoundError(YaDiskError):
    error_type = "DiskPathDoesntExistsError"

    def __init__(self, msg=""):
        YaDiskError.__init__(self, PathNotFoundError.error_type, msg)

class DirectoryExistsError(YaDiskError):
    error_type = "DiskPathPointsToExistentDirectoryError"

    def __init__(self, msg=""):
        YaDiskError.__init__(self, DirectoryExistsError.error_type, msg)

class PathExistsError(YaDiskError):
    error_type = "DiskResourceAlreadyExistsError"

    def __init__(self, msg=""):
        YaDiskError.__init__(self, PathExistsError.error_type, msg)
