# -*- coding: utf-8 -*-

from .api import GetOperationStatusRequest

__all__ = ["OperationMethodsMixin"]

class OperationMethodsMixin:
    def get_operation_status(self, operation_id, /, **kwargs):
        """
            Get operation status.

            :param operation_id: ID of the operation or a link
            :param fields: list of keys to be included in the response
            :param timeout: `float` or `tuple`, request timeout
            :param headers: `dict` or `None`, additional request headers
            :param n_retries: `int`, maximum number of retries
            :param retry_interval: delay between retries in seconds

            :returns: `str`
        """

        return self._get_operation_status(self.get_session(), operation_id)

    def _get_operation_status(self, session, operation_id, /, **kwargs):
        # This method is kept for private use (such as for check_token())
        request = GetOperationStatusRequest(session, operation_id, **kwargs)
        request.send()

        return request.process().status
