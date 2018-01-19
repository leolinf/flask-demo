# -*- coding: utf-8 -*-

from ..constant import Code
from flask import jsonify

def make_response(data=None, status=Code.SUCCESS, msg=""):

    if not msg:
        msg = Code.MSG.get(status)

    return jsonify({
        'data': data,
        'code': status,
        'msg': msg,
    })
