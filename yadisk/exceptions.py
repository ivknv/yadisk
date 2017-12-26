#!/usr/bin/env python
# -*- coding: utf-8 -*-

__all__ = ["YaDiskError", "UnknownYaDiskError", "BadRequestError",
           "UnauthorizedError", "ForbiddenError", "NotFoundError",
           "NotAcceptableError", "ConflictError", "UnsupportedMediaError",
           "LockedError", "TooManyRequestsError", "InternalServerError",
           "UnavailableError", "InsufficientStorageError", "PathNotFoundError",
           "ParentNotFoundError", "PathExistsError", "DirectoryExistsError",
           "FieldValidationError", "ResourceIsLockedError"]

class YaDiskError(Exception):
    """
        Base class for all exceptions in this library.

        :ivar error_type: `str`, unique error code as returned by API
        :ivar response: an instance of :any:`requests.Response`
    """

    def __init__(self, error_type=None, msg="", response=None):
        Exception.__init__(self, msg)

        self.error_type = error_type
        self.response = response

class UnknownYaDiskError(YaDiskError):
    """Thrown when the request failed but the response does not contain any error info."""

    def __init__(self, msg="", response=None):
        YaDiskError.__init__(self, None, msg, response)

class BadRequestError(YaDiskError):
    """Thrown when the server returns code 400."""
    pass

class UnauthorizedError(YaDiskError):
    """Thrown when the server returns code 401."""
    pass

class ForbiddenError(YaDiskError):
    """Thrown when the server returns code 403."""
    pass

class NotFoundError(YaDiskError):
    """Thrown when the server returns code 404."""
    pass

class NotAcceptableError(YaDiskError):
    """Thrown when the server returns code 406."""
    pass

class ConflictError(YaDiskError):
    """Thrown when the server returns code 409."""
    pass

class UnsupportedMediaError(YaDiskError):
    """Thrown when the server returns code 415."""
    pass

class LockedError(YaDiskError):
    """Thrown when the server returns code 423."""
    pass

class TooManyRequestsError(YaDiskError):
    """Thrown when the server returns code 429."""
    pass

class InternalServerError(YaDiskError):
    """Thrown when the server returns code 500."""
    pass

class UnavailableError(YaDiskError):
    """Thrown when the server returns code 503."""
    pass

class InsufficientStorageError(YaDiskError):
    """Thrown when the server returns code 509."""
    pass

class PathNotFoundError(NotFoundError):
    """Thrown when the requested path does not exist."""
    pass

class ParentNotFoundError(ConflictError):
    """Thrown by `mkdir`, `upload`, etc. when the parent directory doesn't exist."""
    pass

class PathExistsError(ConflictError):
    """Thrown when the requested path already exists."""
    pass

class DirectoryExistsError(PathExistsError):
    """Thrown when the directory already exists."""
    pass

class FieldValidationError(BadRequestError):
    """Thrown when the request contains fields with invalid data."""
    pass

class ResourceIsLockedError(LockedError):
    """Thrown when the resource is locked by another operation."""
    pass
