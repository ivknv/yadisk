#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import defaultdict
import time

import requests

from ..exceptions import *
from ..objects import ErrorObject

from .. import settings

EXCEPTION_MAP = {400: defaultdict(lambda: BadRequestError,
                                  {"FieldValidationError": FieldValidationError}),
                 401: defaultdict(lambda: UnauthorizedError),
                 403: defaultdict(lambda: ForbiddenError),
                 404: defaultdict(lambda: NotFoundError,
                                  {"DiskNotFoundError": PathNotFoundError}),
                 406: defaultdict(lambda: NotAcceptableError),
                 409: defaultdict(lambda: ConflictError,
                                  {"DiskPathDoesntExistsError": ParentNotFoundError,
                                   "DiskPathPointsToExistentDirectoryError": DirectoryExistsError,
                                   "DiskResourceAlreadyExistsError": PathExistsError}),
                 415: defaultdict(lambda: UnsupportedMediaError),
                 423: defaultdict(lambda: LockedError,
                                  {"DiskResourceLockedError": ResourceIsLockedError}),
                 429: defaultdict(lambda: TooManyRequestsError),
                 500: defaultdict(lambda: InternalServerError),
                 503: defaultdict(lambda: UnavailableError),
                 509: defaultdict(lambda: InsufficientStorageError)}

class APIRequest(object):
    """
        Base class for all API requests.

        :param session: an instance of :any:`requests.Session`
        :param args: `dict` of arguments, that will be passed to `process_args`
        :param timeout: request timeout
        :param n_retries: maximum number of retries
        :param retry_interval: delay between retries in seconds
        :param send_args, send_kwargs: other parameters for session.send()

        :ivar url: `str`, request URL
        :ivar method: `str`, request method
        :ivar content_type: `str`, Content-Type header ("application/x-www-form-urlencoded" by default)
        :ivar timeout: `float` or `tuple`, request timeout
        :ivar n_retries: `int`, maximum number of retries
        :ivar success_codes: `list`-like, list of response codes that indicate request's success
        :ivar retry_codes: `list`-like, list of response codes that trigger a retry
        :ivar retry_interval: `float`, delay between retries in seconds
    """

    url = None
    method = None
    content_type = "application/x-www-form-urlencoded"
    timeout = None 
    n_retries = None
    success_codes = {200}
    retry_codes = {500, 502, 503, 504}
    retry_interval = None

    def __init__(self, session, args, timeout=None, n_retries=None, retry_interval=None,
                 *send_args, **send_kwargs):
        if timeout is None:
            timeout = self.timeout
        if timeout is None:
            timeout = settings.DEFAULT_TIMEOUT

        if n_retries is None:
            n_retries = self.n_retries
        if n_retries is None:
            n_retries = settings.DEFAULT_N_RETRIES

        if retry_interval is None:
            retry_interval = self.retry_interval
        if retry_interval is None:
            retry_interval = settings.DEFAULT_RETRY_INTERVAL

        self.session = session
        self.args = args
        self.send_args, self.send_kwargs = send_args, send_kwargs
        self.timeout = timeout
        self.n_retries = n_retries
        self.retry_interval = retry_interval
        self.request = None
        self.response = None
        self.data = {}
        self.params = {}

        self.process_args(**self.args)
        self.prepare()

    def process_args(self):
        raise NotImplementedError

    def prepare(self):
        """Prepare the request"""

        r = requests.Request(self.method, self.url,
                             data=self.data, params=self.params)
        r.headers["Content-Type"] = self.content_type
        self.request = self.session.prepare_request(r)

    def send(self):
        """
            Actually send the request
           
           :returns: :any:`requests.Response` (`self.response`)
        """

        for i in range(self.n_retries + 1):
            if i > 0:
                if not self.on_retry():
                    break

                time.sleep(self.retry_interval)

            try:
                self.response = self.session.send(self.request, *self.send_args, timeout=self.timeout, **self.send_kwargs)
            except requests.exceptions.RequestException as e:
                if i == self.n_retries:
                    raise e

                continue

            if self.response.status_code in self.retry_codes:
                continue

            break

        return self.response

    def on_retry(self):
        return True

    def process_json(self, js):
        """
            Process the JSON response.

            :param js: `dict`, JSON response

            :returns: processed response, can be anything
        """

        raise NotImplementedError

    def process_error(self, js):
        exceptions = EXCEPTION_MAP.get(self.response.status_code)

        if exceptions is None:
            return UnknownYaDiskError("Unknown Yandex.Disk error", self.response)

        error = ErrorObject(js)
        exc = exceptions[error.error]

        msg = error.message or "<empty>"
        desc = error.description or "<empty>"
        
        return exc(error.error, "%s (%s / %s)" % (msg, desc, error.error), self.response)

    def process(self):
        """
            Process the response.

            :returns: depends on `self.process_json()`
        """

        success = self.response.status_code in self.success_codes

        try:
            result = self.response.json()
        except (ValueError, RuntimeError):
            result = None

        if not success:
            raise self.process_error(result)
        elif result is not None:
            return self.process_json(result)
