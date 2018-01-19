# -*- coding = utf-8 -*-
import json
import time
import hashlib
from urllib import parse
import logging
from functools import wraps

from flask import request
from mongoengine import DoesNotExist, MultipleObjectsReturned

from app import Config
from app.common.constant import Code, Params
from app.common.helper import make_response
from app.models import User


class SignChecker:

    def __init__(self, sign, appkey, t, request_data):

        self.sign = sign
        self.appkey = appkey
        self.t = t
        self.request_data = request_data

        self.errcode = None
        self.user = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def _check_all(self):

        if not self._check_time():
            return False
        if not self._check_appkey():
            return False
        if not self._check_secret():
            return False

        return True

    def _check_time(self):

        now = time.time()
        try:
            t = float(self.t)
        except Exception as e:
            self.logger.debug(e)
            self.errcode = Code.VERIFYDENIED
            return False

        if abs(now - t) > Config.TEXPIRE:
            self.errcode = Code.TSEPIRE
            return False

        return True

    def _check_appkey(self):

        if not self.appkey:
            self.logger.debug("appkey都不给你还想请求数据")
            self.errcode = Code.VERIFYDENIED
            return False

        try:
            self.user = User.objects.get(appkey=self.appkey)
        except DoesNotExist:
            self.logger.debug("瞎逼填的appkey {0}".format(self.appkey))
            self.errcode = Code.VERIFYDENIED
            return False
        except MultipleObjectsReturned:
            self.errcode = Code.SERVERS_ERROR
            return False

        return True

    def _check_secret(self):

        if self.user is None:
            return False

        secret = self.user.appsecret
        l = []
        for k in self.request_data:
            if k.startswith('image'):
                continue
            if k in [Params.SIGN, "frontPhoto", "backPhoto"]:
                continue
            value = self.request_data[k]
            if isinstance(value, dict):
                value = json.dumps(value)
            l.append(k + parse.quote(value, safe='*').replace("%20", "+"))

        s = secret + ''.join(sorted(l)) + secret
        sign = hashlib.md5(s.encode()).hexdigest()
        if sign != self.sign:
            self.logger.debug("正确签名应该是 {sign}".format(sign=sign))
            self.errcode = Code.VERIFYDENIED
            return False

        return True

    def authenticate(self):
        """鉴权方法
        """
        if self._check_all():
            return self.user
        else:
            return None


def auth_required(func):
    """鉴权装饰器"""

    @wraps(func)
    def wrapper(*args, **kwargs):

        if request.method == "POST":
            # 给的不是json
            if not request.json:
                return make_response(code=Code.MISSPARAM)

            sign = request.json.get(Params.SIGN)
            appkey = request.json.get(Params.APPKEY)
            t = request.json.get(Params.TIMESTAMP)
            request_data = request.json
        else:
            sign = request.args.get(Params.SIGN)
            appkey = request.args.get(Params.APPKEY)
            t = request.args.get(Params.TIMESTAMP)
            request_data = request.args.copy()

        sign_checker = SignChecker(sign, appkey, t, request_data)
        sign_checker.authenticate()

        if sign_checker.errcode:

            return make_response(code=sign_checker.errcode)

        return func(*args, **kwargs)
    return wrapper
