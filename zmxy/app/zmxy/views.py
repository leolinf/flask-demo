# -*- coding: utf-8 -*-

from flask_restful import Resource
from flask import jsonify, redirect, request
from flask.views import MethodView
from urllib.parse import quote, unquote

from .form import AuthForm, DataForm
from .util import zmxy_auth, score, watchlist
from app.core.function import make_response
from app.constant import Code


class AuthView(MethodView):
    """请求授权"""

    def post(self):

        form = AuthForm(request.form)
        if not form.validate():
            return make_response(status=Code.MISSPARAMS)
        name = form.name.data
        idCard = form.idCard.data
        phone = form.phone.data
        resp = zmxy_auth(name, idCard, phone)
        if resp.get("code") == 1200:
            callback_url = resp.get("data").get("url")
            return redirect(callback_url)
        else:
            return redirect("/")


class GetDataView(MethodView):
    """获取数据"""

    def get(self):
        form = DataForm(request.args)
        if not form.validate():
            return make_response(status=Code.MISSPARAMS)
        params = form.params.data
        sign = form.sign.data
        params = '%' in params and unquote(params) or params
        sign = '%' in sign and unquote(sign) or sign
        _score = score(params, sign)
        _watchlist = watchlist(params, sign)
        data = {"score": _score, "watchlist": _watchlist}
        return make_response(data=data)
