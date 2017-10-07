#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

import requests

from ..exceptions import *
from ..objects import ErrorObject

EXCEPTION_MAP = {i.error_type: i for i in (UnauthorizedError,
                                           DiskNotFoundError,
                                           PathNotFoundError,
                                           DirectoryExistsError,
                                           PathExistsError)}

class APIRequest(object):
    """
        Base class for all API requests

        url:
            request URL

        method:
            request method

        timeout:
            request timeout

        n_retries:
            maximum number of retries

        success_codes:
            list of response codes that indicate request's success

        retry_codes:
            list of response codes that trigger a retry

        retry_interval:
            delay between retries in seconds (`float`)

        :param session: an instance of `requests.Session`
        :param args: `dict` of arguments, that will be passed to `process_args`
        :param timeout: request timeout
        :param n_retries: maximum number of retries
        :param send_args, send_kwargs: other parameters for session.send()
    """

    url = None
    method = None
    timeout = (10, 15)
    n_retries = 3
    success_codes = {200}
    retry_codes = {500, 502, 503, 504}
    retry_interval = 0.0

    def __init__(self, session, args, timeout=None, n_retries=None, *send_args, **send_kwargs):
        if timeout is None:
            timeout = self.timeout

        if n_retries is None:
            n_retries = self.n_retries

        self.session = session
        self.args = args
        self.send_args, self.send_kwargs = send_args, send_kwargs
        self.timeout = timeout
        self.n_retries = n_retries
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

        self.request = requests.Request(self.method, self.url,
                                        data=self.data, params=self.params)

    def send(self):
        """
            Actually send the request
           
           :returns: `requests.Response` (`self.response`)
        """
        for i in range(self.n_retries + 1):
            if i > 0:
                if not self.on_retry():
                    break

                time.sleep(self.retry_interval)

            prepped = self.session.prepare_request(self.request)

            try:
                self.response = self.session.send(prepped, *self.send_args, timeout=self.timeout, **self.send_kwargs)
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
        raise NotImplementedError

    def process_error(self, js):
        if js is None:
            return UnknownYaDiskError("Unknown Yandex.Disk error")

        error = ErrorObject(js)
        exc = EXCEPTION_MAP.get(error.error,
                                lambda msg: YaDiskError(error.error, msg))

        msg = error.message or "<empty>"
        desc = error.description or "<empty>"
        
        return exc("%s: %s (%s)" % (error.error, msg, desc))

    def process(self):
        """Process the response"""

        success = self.response.status_code in self.success_codes

        try:
            result = self.response.json()
        except (ValueError, RuntimeError):
            result = None

        if not success:
            raise self.process_error(result)
        elif result is not None:
            return self.process_json(result)
