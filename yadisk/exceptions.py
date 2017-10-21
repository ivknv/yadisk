#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ["YaDiskError", "UnknownYaDiskError", "UnauthorizedError",
           "DiskNotFoundError", "PathNotFoundError", "DirectoryExistsError",
           "PathExistsError"]

class YaDiskError(BaseException):
    """
        Base class for all exceptions in this library.

        :ivar error_type: `str`, unique error code as returned by API
    """

    def __init__(self, error_type=None, msg=""):
        BaseException.__init__(self, msg)

        self.error_type = error_type

class UnknownYaDiskError(YaDiskError):
    """
        Thrown when the request failed but the response does not contain any error info.
    """

    def __init__(self, msg=""):
        YaDiskError.__init__(self, None, msg)

class UnauthorizedError(YaDiskError):
    """Thrown when the application is not authorized."""

    error_type = "UnauthorizedError"

    def __init__(self, msg=""):
        YaDiskError.__init__(self, UnauthorizedError.error_type, msg)

class DiskNotFoundError(YaDiskError):
    """Thrown when the requested path does not exist."""

    error_type = "DiskNotFoundError"

    def __init__(self, msg=""):
        YaDiskError.__init__(self, DiskNotFoundError.error_type, msg)

class PathNotFoundError(YaDiskError):
    """Thrown by `mkdir` when the parent directory doesn't exist."""

    error_type = "DiskPathDoesntExistsError"

    def __init__(self, msg=""):
        YaDiskError.__init__(self, PathNotFoundError.error_type, msg)

class DirectoryExistsError(YaDiskError):
    """
        Thrown when the directory already exists.
    """

    error_type = "DiskPathPointsToExistentDirectoryError"

    def __init__(self, msg=""):
        YaDiskError.__init__(self, DirectoryExistsError.error_type, msg)

class PathExistsError(YaDiskError):
    """
        Thrown when the requested path already exists.
    """

    error_type = "DiskResourceAlreadyExistsError"

    def __init__(self, msg=""):
        YaDiskError.__init__(self, PathExistsError.error_type, msg)
