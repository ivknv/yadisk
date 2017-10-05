#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ..api import GetOperationStatusRequest

__all__ = ["get_operation_status"]

def get_operation_status(session, operation_id, *args, **kwargs):
    """
        Get operation status.

        :param session: an instance of `requests.Session` with prepared headers
        :param operation_id: ID of the operation or a link

        :returns: `str`
    """

    request = GetOperationStatusRequest(session, operation_id, *args, **kwargs)
    request.send()

    return request.process().status
