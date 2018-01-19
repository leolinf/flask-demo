# coding=utf-8
from flask import request, jsonify
from time import time

from apps.baseinfo import BaseView
from apps.forms import TelnoForm
from framework import const
from framework.logger import trace_view, class_logger, project_logger
from utils.extract_ec_record_online import (extract_online_records_by_kv,
                                            tel_tag_record)


@class_logger
@trace_view
class GetTelList(BaseView):

    def get(self, *args, **kwargs):
        form = TelnoForm(request.args)
        if not form.validate():
            return self.raise_error(const.MISSPARAM)
        telnos = form.telno.data.split(",")
        info_list = []
        start_time = time()
        for telno in telnos:
            response = extract_online_records_by_kv('tel', telno)
            if response:
                info_list.extend(response)
        project_logger.info("[GET][TEL_LIST][TIME|%s][REQUEST|%s]", time() - start_time, telnos)
        res = {
            'code': 1200,
            'data': {'info_list': info_list},
        }
        return jsonify(res)

@class_logger
@trace_view
class GetOldTelList(BaseView):

    def get(self, *args, **kwargs):
        form = TelnoForm(request.args)
        if not form.validate():
            return self.raise_error(const.MISSPARAM)
        telnos = form.telno.data.split(",")
        info_list = []
        start_time = time()
        for telno in telnos:
            response = extract_online_records_by_kv('tel', telno, company='old')
            if response:
                info_list.extend(response)
        project_logger.info("[GET][TEL_OLD_LIST][TIME|%s][REQUEST|%s]", time() - start_time, telnos)
        res = {
            'code': 1200,
            'data': {'info_list': info_list},
        }
        return jsonify(res)


@class_logger
@trace_view
class GetTelTag(BaseView):

    def get(self, *args, **kwargs):
        form = TelnoForm(request.args)
        if not form.validate():
            return self.raise_error(const.MISSPARAM)
        telnos = form.telno.data.split(",")
        info_list = []
        start_time = time()
        for telno in telnos:
            response = tel_tag_record('tel', telno)
            if response:
                info_list.extend(response)

        project_logger.info("[GET][TEL_TAG][TIME|%s][REQUEST|%s]", time() - start_time, telnos)
        res = {
            'code': 1200,
            'data': {'info_list': info_list},
        }
        return jsonify(res)
