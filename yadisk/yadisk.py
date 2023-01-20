# -*- coding: utf-8 -*-

import functools
import threading
import weakref

import requests

from .disk_methods_mixin import DiskMethodsMixin
from .auth_methods_mixin import AuthMethodsMixin
from .operation_methods_mixin import OperationMethodsMixin
from .resource_methods_mixin import ResourceMethodsMixin

__all__ = ["YaDisk"]

class YaDisk(AuthMethodsMixin, DiskMethodsMixin, OperationMethodsMixin, ResourceMethodsMixin):
    """
        Implements access to Yandex.Disk REST API.

        :param id: application ID
        :param secret: application secret password
        :param token: application token

        :ivar id: `str`, application ID
        :ivar secret: `str`, application secret password
        :ivar token: `str`, application token
    """

    def __init__(self, id="", secret="", token=""):
        self.id = id
        self.secret = secret
        self.token = token

        @functools.lru_cache(maxsize=1024)
        def _get_session(token, tid):
            return self.make_session(token)

        self._get_session = _get_session

    def clear_session_cache(self):
        """Clears the session cache. Unused sessions will be closed."""

        self._get_session.cache_clear()

    def make_session(self, token=None):
        """
            Prepares :any:`requests.Session` object with headers needed for API.

            :param token: application token, equivalent to `self.token` if `None`
            :returns: :any:`requests.Session`
        """

        if token is None:
            token = self.token

        session = requests.Session()

        # Make sure the session is eventually closed
        weakref.finalize(session, session.close)

        if token:
            session.headers["Authorization"] = "OAuth " + token

        return session

    def get_session(self, token=None):
        """
            Like :any:`YaDisk.make_session` but wrapped in :any:`functools.lru_cache`.

            :returns: :any:`requests.Session`, different instances for different threads
        """

        if token is None:
            token = self.token

        return self._get_session(token, threading.get_ident())
