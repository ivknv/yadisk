#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests

from ..utils import auto_retry, get_exception
from .. import settings

__all__ = ["APIRequest"]

class APIRequest(object):
    """
        Base class for all API requests.

        :param session: an instance of :any:`requests.Session`
        :param args: `dict` of arguments, that will be passed to `process_args`
        :param timeout: request timeout
        :param n_retries: maximum number of retries
        :param retry_interval: delay between retries in seconds
        :param kwargs: other parameters for session.send()

        :ivar url: `str`, request URL
        :ivar method: `str`, request method
        :ivar content_type: `str`, Content-Type header ("application/x-www-form-urlencoded" by default)
        :ivar timeout: `float` or `tuple`, request timeout
        :ivar n_retries: `int`, maximum number of retries
        :ivar success_codes: `list`-like, list of response codes that indicate request's success
        :ivar retry_interval: `float`, delay between retries in seconds
    """

    url = None
    method = None
    content_type = "application/x-www-form-urlencoded"
    timeout = None 
    n_retries = None
    success_codes = {200}
    retry_interval = None

    def __init__(self, session, args, **kwargs):
        kwargs = dict(kwargs)

        timeout = kwargs.get("timeout")
        n_retries = kwargs.pop("n_retries", None)
        retry_interval = kwargs.pop("retry_interval", None)

        if timeout is None:
            timeout = self.timeout
        if timeout is None:
            timeout = settings.DEFAULT_TIMEOUT

        kwargs["timeout"] = timeout

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
        self.send_kwargs = kwargs
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

    def _attempt(self):
        self.response = self.session.send(self.request, **self.send_kwargs)

        success = self.response.status_code in self.success_codes

        if not success:
            raise get_exception(self.response)

    def send(self):
        """
            Actually send the request
           
           :returns: :any:`requests.Response` (`self.response`)
        """

        auto_retry(self._attempt, self.n_retries, self.retry_interval)

        return self.response

    def process_json(self, js):
        """
            Process the JSON response.

            :param js: `dict`, JSON response

            :returns: processed response, can be anything
        """

        raise NotImplementedError

    def process(self):
        """
            Process the response.

            :returns: depends on `self.process_json()`
        """

        try:
            result = self.response.json()
        except (ValueError, RuntimeError):
            result = None
        
        if result is not None:
            return self.process_json(result)
