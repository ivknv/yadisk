# -*- coding: utf-8 -*-

from ..api import GetOperationStatusRequest

__all__ = ["get_operation_status"]

def get_operation_status(session, operation_id, **kwargs):
    """
        Get operation status.

        :param session: an instance of :any:`requests.Session` with prepared headers
        :param operation_id: ID of the operation or a link
        :param fields: list of keys to be included in the response
        :param timeout: `float` or `tuple`, request timeout
        :param headers: `dict` or `None`, additional request headers
        :param n_retries: `int`, maximum number of retries
        :param retry_interval: delay between retries in seconds

        :returns: `str`
    """

    request = GetOperationStatusRequest(session, operation_id, **kwargs)
    request.send()

    return request.process().status
