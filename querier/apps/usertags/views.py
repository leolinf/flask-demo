# -*- coding: utf-8 -*-

from flask import request, jsonify
from time import time

from apps.baseinfo import BaseView
from apps.forms import TelnoForm
from framework import const
from framework.logger import trace_view, class_logger, project_logger
from utils.auth import credit_phone_risk
from utils.data import get_shop_list
from utils.extract_ec_record_online import (
    tel_tag_record, extract_online_records_by_kv,
    user_tag_record,
)
from .handlers import top_all, portrait_online, filter_by_time
from .util import (consume_info_util, consume_list_util,
    base_info, dict_list_util
)


@class_logger
@trace_view
class GetUserTags(BaseView):

    def get(self):
        form = TelnoForm(request.args)
        if not form.validate():
            return self.raise_error(const.MISSPARAM)
        telnos = form.telno.data.split(",")
        info_list = []
        for telno in telnos:
            resp, basic, m_ref_cnt = user_tag_record('tel', telno)
            if not basic or not resp:
                continue
            leaf_cat = top_all(resp)
            basic.update(leaf_cat)
            info_list.append(basic)

        return jsonify({
            'code': const.SUCCESS,
            'data': {'info_list': info_list},
        })


@class_logger
@trace_view
class PortraitView(BaseView):

    def get(self):
        form = TelnoForm(request.args)
        if not form.validate():
            return self.raise_error(const.MISSPARAM)
        telnos = form.telno.data.split(",")
        mon_ago = form.mon_ago.data
        end_time = form.end_time.data
        info_list = []
        for telno in telnos:
            resp, basic, m_ref_cnt = user_tag_record('tel', telno)
            response = filter_by_time(resp, mon_ago, end_time=end_time)
            if not basic or not response:
                continue
            leaf_cat = top_all(response)
            if not leaf_cat:
                continue
            shop_list = portrait_online(response)
            basic.update(leaf_cat)
            basic.update(shop_list)
            basic.update({"m_ref_cnt": str(m_ref_cnt)})
            basic.update({"m_abnormal_cnt": str(len(credit_phone_risk(int(telno))))})
            info_list.append(basic)

        return jsonify({
            'code': const.SUCCESS,
            'data': {'info_list': info_list},
        })


@class_logger
@trace_view
class ThreePortrait(BaseView):

    def get(self):
        form = TelnoForm(request.args)
        if not form.validate():
            return self.raise_error(const.MISSPARAM)
        telnos = form.telno.data.split(",")
        info_list = {}
        start_time = time()
        for telno in telnos:
            consume_list = extract_online_records_by_kv('tel', telno, company='santai')
            info_list["consume_info"] = consume_list_util(consume_list)
            info_list.update(base_info(telno))
        project_logger.info("[GET][THREE][TIME|%s][PHONE|%s]", time()-start_time, telnos)
        dict_list_util(info_list)
        return jsonify({
            'code': const.SUCCESS,
            'data': info_list,
        })


#@class_logger
#@trace_view
#class PortraitView(BaseView):
#
#    def get(self):
#        form = TelnoForm(request.args)
#        if not form.validate():
#            return self.raise_error(const.MISSPARAM)
#        telnos = form.telno.data.split(",")
#        info_list = []
#        for telno in telnos:
#            shop_list = get_shop_list(telno)
#            resp, basic = user_tag_record('tel', telno)
#            if not basic or not resp or not shop_list:
#                continue
#            leaf_cat = top_all(resp)
#            basic.update(leaf_cat)
#            basic.update(shop_list)
#            info_list.append(basic)
#
#        return jsonify({
#            'code': const.SUCCESS,
#            'data': {'info_list': info_list},
#        })
