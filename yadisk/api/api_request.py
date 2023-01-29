# -*- coding: utf-8 -*-

import requests

from ..exceptions import InvalidResponseError

from ..utils import auto_retry, get_exception
from .. import settings

from typing import Optional, Union, TypeVar
from ..compat import Set

__all__ = ["APIRequest"]

# For cases when None can't be used
_DEFAULT_TIMEOUT = object()

class APIRequest(object):
    """
        Base class for all API requests.

        :param session: an instance of :any:`requests.Session`
        :param args: `dict` of arguments, that will be passed to `process_args`
        :param timeout: `float` or `tuple`, request timeout
        :param headers: `dict` or `None`, additional request headers
        :param n_retries: `int`, maximum number of retries
        :param retry_interval: delay between retries in seconds
        :param kwargs: other arguments for :any:`requests.Session.send`

        :ivar url: `str`, request URL
        :ivar method: `str`, request method
        :ivar content_type: `str`, Content-Type header ("application/x-www-form-urlencoded" by default)
        :ivar timeout: `float` or `tuple`, request timeout
        :ivar n_retries: `int`, maximum number of retries
        :ivar success_codes: `list`-like, list of response codes that indicate request's success
        :ivar retry_interval: `float`, delay between retries in seconds
    """

    url: Optional[str] = None
    method: Optional[str] = None
    content_type: str = "application/x-www-form-urlencoded"
    timeout = _DEFAULT_TIMEOUT
    n_retries: Optional[int] = None
    success_codes: Set[int] = {200}
    retry_interval: Optional[Union[int, float]] = None

    request: Optional[requests.PreparedRequest]
    response: Optional[requests.Response]

    T = TypeVar("T")

    def __init__(self, session: requests.Session, args: dict, **kwargs):
        n_retries = kwargs.pop("n_retries", None)
        retry_interval = kwargs.pop("retry_interval", None)
        headers = kwargs.pop("headers", {})

        if headers is None:
            headers = {}

        try:
            timeout = kwargs["timeout"]
        except KeyError:
            timeout = self.timeout

        if timeout is _DEFAULT_TIMEOUT:
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
        self.headers = headers
        self.request = None
        self.response = None
        self.data = {}
        self.params = {}

        self.process_args(**self.args)
        self.prepare()

    def process_args(self) -> None:
        raise NotImplementedError

    def prepare(self) -> None:
        """Prepare the request"""

        r = requests.Request(self.method, self.url,
                             data=self.data, params=self.params)
        r.headers["Content-Type"] = self.content_type
        r.headers.update(self.headers)
        self.request = self.session.prepare_request(r)

    def _attempt(self) -> None:
        assert self.request is not None

        self.response = self.session.send(self.request, **self.send_kwargs)

        success = self.response.status_code in self.success_codes

        if not success:
            raise get_exception(self.response)

    def send(self) -> requests.Response:
        """
            Actually send the request

           :returns: :any:`requests.Response` (`self.response`)
        """

        auto_retry(self._attempt, self.n_retries, self.retry_interval)

        assert self.response is not None

        return self.response

    def process_json(self, js: Optional[dict], **kwargs) -> T:
        """
            Process the JSON response.

            :param js: `dict` or `None`, JSON response
            :param kwargs: extra arguments (optional)

            :returns: processed response, can be anything
        """

        raise NotImplementedError

    def process(self, **kwargs) -> T:
        """
            Process the response.

            :param kwargs: extra arguments (optional)

            :returns: depends on `self.process_json()`
        """

        assert self.response is not None

        try:
            result = self.response.json()
        except (ValueError, RuntimeError):
            result = None

        try:
            return self.process_json(result, **kwargs)
        except ValueError as e:
            raise InvalidResponseError(f"Server returned invalid response: {e}")
