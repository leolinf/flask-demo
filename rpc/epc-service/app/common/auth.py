# -*- coding = utf-8 -*-

import time
import hashlib
import urllib
import logging
from functools import wraps

from flask import request
from mongoengine import DoesNotExist, MultipleObjectsReturned

from app.common.constant import Code
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

        return all([
            self._check_time(),
            self._check_appkey(),
            self._check_secret(),
        ])

    def _check_time(self):

        now = time.time()
        try:
            t = float(self.t)
        except Exception as e:
            self.logger.debug(e)
            self.errcode = Code.VERIFYDENIED
            return False

        if abs(now - t) > 3600:
            self.errcode = Code.TSEPIRE
            return False

        return True

    def _check_appkey(self):

        try:
            self.user = User.objects.get(appkey=self.appkey)
        except DoesNotExist:
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
            if k in ["sign", "frontPhoto", "backPhoto"]:
                continue
            l.append(k + urllib.parse.quote(self.request_data[k], safe=''))

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

        sign = request.args.get("sign")
        appkey = request.args.get("appkey")
        t = request.args.get("t")

        sign_checker = SignChecker(sign, appkey, t, request.args.copy())
        sign_checker.authenticate()

        if sign_checker.errcode:

            return make_response(code=sign_checker.errcode)

        return func(*args, **kwargs)
    return wrapper
