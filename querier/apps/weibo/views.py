# coding=utf-8
from flask import request, jsonify
from time import time

from apps.baseinfo import BaseView
from apps.forms import TelnoForm
from framework import const
from framework.logger import trace_view, class_logger, project_logger
from utils.auth import get_weibo_vip

from .handlers import weibo_info, weibo_fri


@class_logger
@trace_view
class GetWeiboInfo(BaseView):

    def get(self, *args, **kwargs):
        form = TelnoForm(request.args)
        if not form.validate():
            self.raise_error(const.MISSPARAM)
        telnos = form.telno.data.split(",")
        info_list = []
        for telno in telnos:
            response = weibo_info(telno)
            if response:
                info_list.append(response)
        res = {
            'code': 1200,
            'data': {'info_list': info_list},
        }
        return jsonify(res)


@class_logger
@trace_view
class GetWeiboFri(BaseView):

    def get(self, *args, **kwargs):
        form = TelnoForm(request.args)
        if not form.validate():
            self.raise_error(const.MISSPARAM)
        telnos = form.telno.data.split(",")
        info_list = []
        for telno in telnos:
            response = weibo_fri(telno)
            if response:
                info_list.append(response)
        res = {
            'code': 1200,
            'data': {'info_list': info_list},
        }
        return jsonify(res)


@class_logger
@trace_view
class GetWeiboVipInfo(BaseView):

    def post(self, *args, **kwargs):
        wids = request.form.get("ids", "")
        if wids:
            self.raise_error(const.MISSPARAM)
        wid = wids.split(",")
        info_list = []
        start_time = time()
        resps = get_weibo_vip([int(i) for i in  wid])
        project_logger.info("[GET][WEIBO_VIP][TIME|%s][REQUEST|%s]", time() - start_time, wid)
        for resp in resps:
            if resp:
                info_list.append(resp)
        res = {
            'code': 1200,
            'data': {'info_list': info_list},
        }
        return jsonify(res)
