#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ...api import GetOperationStatusRequest

__all__ = ["get_operation_status"]

def get_operation_status(session, operation_id, *args, **kwargs):
    request = GetOperationStatusRequest(session, operation_id, *args, **kwargs)
    request.send()

    return request.process().status
