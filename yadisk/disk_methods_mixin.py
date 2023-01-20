# -*- coding: utf-8 -*-

from .api import DiskInfoRequest

__all__ = ["DiskMethodsMixin"]

class DiskMethodsMixin:
    def get_disk_info(self, **kwargs):
        """
            Get disk information.

            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: :any:`DiskInfoObject`
        """

        request = DiskInfoRequest(self.get_session(), **kwargs)
        request.send()

        return request.process()
