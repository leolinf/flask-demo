# -*- coding: utf-8 -*-

from flask import request, jsonify
from flask.views import MethodView

from forms import AuthForm
from framework import const
from utils.auth import authenticate, record


class BaseView(MethodView):

    def dispatch_request(self, *args, **kwargs):

        form = AuthForm(request.args)
        if not form.validate():
            return self.raise_error(const.MISSPARAM)
        appkey = form.username.data
        secret = form.password.data
        # 验证
        if not authenticate(appkey, secret):
            return self.raise_error(const.VERIFYDENIED)
        # 记录
        record(appkey, request)

        return super(BaseView, self).dispatch_request(*args, **kwargs)

    def raise_error(self, code):
        return jsonify({"code": code, "data": const.MSG[code]})
