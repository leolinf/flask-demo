# -*- coding: utf-8 -*-

from .constants import Code
from app.config import Config


def make_response(data=None, status=Code.SUCCESS, msg=""):

    if not msg:
        msg = Code.MSG.get(status)

    return {
        'data': data,
        'code': status,
        'msg': msg,
    }
