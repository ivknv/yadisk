# -*- coding: utf-8 -*-

__all__ = [
    "YaDiskError", "RequestError", "YaDiskConnectionError", "TooManyRedirectsError",
    "RequestTimeoutError", "RetriableYaDiskError", "UnknownYaDiskError",
    "WrongResourceTypeError",  "BadRequestError", "UnauthorizedError",
    "ForbiddenError", "NotFoundError", "NotAcceptableError",
    "ConflictError", "PayloadTooLargeError", "UnsupportedMediaError",
    "LockedError", "UploadTrafficLimitExceededError", "TooManyRequestsError",
    "InternalServerError", "BadGatewayError", "UnavailableError",
    "GatewayTimeoutError", "InsufficientStorageError", "PathNotFoundError",
    "ParentNotFoundError", "PathExistsError", "DirectoryExistsError",
    "FieldValidationError", "ResourceIsLockedError", "MD5DifferError",
    "OperationNotFoundError", "InvalidResponseError", "AuthorizationPendingError",
    "InvalidClientError", "InvalidGrantError", "BadVerificationCodeError",
    "UnsupportedTokenTypeError"
]

class YaDiskError(Exception):
    """
        Base class for all exceptions in this library.

        :ivar error_type: `str`, unique error code as returned by API
        :ivar response: an instance of :any:`Response`

        :param error_type: `str`, unique error code as returned by API
        :param msg: `str`, exception message
        :param response: an instance of :any:`Response`
    """

    def __init__(self, error_type=None, msg="", response=None):
        Exception.__init__(self, msg)

        self.error_type = error_type
        self.response = response

class RequestError(YaDiskError):
    """
        Generic exception class for cases when a request could not be sent or
        response could not be received.
    """

    def __init__(self, msg=""):
        YaDiskError.__init__(self, None, msg)

class YaDiskConnectionError(RequestError):
    """Thrown when a connection error occured."""
    pass

class TooManyRedirectsError(RequestError):
    """Thrown when there were too many redirects."""
    pass

class RequestTimeoutError(RequestError):
    """Thrown when a request timed out."""
    pass

class WrongResourceTypeError(YaDiskError):
    """Thrown when the resource was expected to be of different type (e.g., file instead of directory)."""

    def __init__(self, msg=""):
        YaDiskError.__init__(self, None, msg, None)

class RetriableYaDiskError(YaDiskError):
    """Thrown when there was an error but it would make sense to retry the request."""
    pass

class UnknownYaDiskError(RetriableYaDiskError):
    """Thrown when the request failed but the response does not contain any error info."""

    def __init__(self, msg="", response=None):
        RetriableYaDiskError.__init__(self, None, msg, response)

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

class PayloadTooLargeError(YaDiskError):
    """Thrown when the server returns code 413."""
    pass

class UnsupportedMediaError(YaDiskError):
    """Thrown when the server returns code 415."""
    pass

class LockedError(YaDiskError):
    """Thrown when the server returns code 423."""
    pass

class UploadTrafficLimitExceededError(LockedError):
    """Thrown when upload limit has been exceeded."""
    pass

class TooManyRequestsError(YaDiskError):
    """Thrown when the server returns code 429."""
    pass

class InternalServerError(RetriableYaDiskError):
    """Thrown when the server returns code 500."""
    pass

class BadGatewayError(RetriableYaDiskError):
    """Thrown when the server returns code 502"""
    pass

class UnavailableError(RetriableYaDiskError):
    """Thrown when the server returns code 503."""
    pass

class GatewayTimeoutError(RetriableYaDiskError):
    """Thrown when the server returns code 504"""
    pass

class InsufficientStorageError(YaDiskError):
    """Thrown when the server returns code 507."""
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

class MD5DifferError(ConflictError):
    """Thrown when the MD5 hash of the file to be deleted doesn't match with the actual one."""
    pass

class OperationNotFoundError(NotFoundError):
    """Thrown by `get_operation_status()` when the operation doesn't exist."""
    pass

class InvalidResponseError(YaDiskError):
    """Thrown when Yandex.Disk did not return a JSON response or if it's invalid."""
    pass

class AuthorizationPendingError(BadRequestError):
    """Thrown when authorization is currently pending, the application has to wait."""
    pass

class InvalidClientError(BadRequestError):
    """Thrown when an invalid client ID or client secret was provided"""
    pass

class InvalidGrantError(BadRequestError):
    """Thrown when a verification code is expired or invalid"""
    pass

class BadVerificationCodeError(BadRequestError):
    """Thrown when a verification code has invalid format"""
    pass

class UnsupportedTokenTypeError(BadRequestError):
    """Thrown when the specified token cannot be used in a request"""
    pass
