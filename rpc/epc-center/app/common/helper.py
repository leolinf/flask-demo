# -*- coding = utf-8 -*-

import logging
from urllib import parse
from functools import wraps

from flask import jsonify, request

from app import Config
from app.common.constant import Code, Params
from app.extensions import cache


def make_response(code=Code.SUCCESS, data=None):

    return jsonify({
        "code": code,
        "data": data,
    })


def view_method_memoize(**kw):

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            if request.method == "POST" and request.json:
                request_params = request.json.copy()
            else:
                request_params = request.args.copy()

            unneeded_params = [Params.SIGN, Params.APPKEY, Params.TIMESTAMP]

            for key in unneeded_params:
                if key in request_params:
                    request_params.pop(key)

            def _fuck(params):
                string = sorted(params.items(), key=lambda param: param[0])
                return parse.urlencode(string)

            request_params = _fuck(request_params)

            if "timeout" not in kw:
                kw["timeout"] = Config.CACHE_DEFAULT_TIMEOUT

            @cache.memoize(**kw)
            def ciao(view, params):
                """
                :param params: 其实就是querystring
                :param view: 作用是让缓存区别不同的view
                """

                return func(*args, **kwargs)

            return ciao(args[0].__class__.__name__, request_params)

        return wrapper
    return decorator


def check_whether_cache_from_response(response):

    return True


def complete_url(url, protocol="http"):

    """

    :param protocol: http or https
    :type url: str
    """

    if not url:
        return url

    if not url.startswith("http"):
        return protocol + "://" + url

    return url
