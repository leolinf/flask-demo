# -*- coding: utf-8 -*-
import json
import hashlib
import requests
import time
from flask import current_app

from app.config import Config as DefaultConfig
# from framework.logger import project_logger
# from app.models import RecordApi

import datetime


def gen_param(product_code, partner_trade_no, product_param, have_pic=0):

    json_data = dict(
        method = DefaultConfig.METHOD,
        version = DefaultConfig.VERSION,
        partner = DefaultConfig.PARTNER,
        sign_type = DefaultConfig.SIGN_TYPE,
        charset = DefaultConfig.CHARSET,
        business_data = dict(
            product_code=product_code,
            partner_trade_no=partner_trade_no,
            product_param=product_param
        )

    )
    if have_pic == 1:
        json_data['business_data'].update({
            'have_pic': '1'
        })
    return json_data


def encrypt(param=None, sign_key=None, is_sha1=False):
    list_param = []

    for k in sorted(param.keys()):
        res = param[k]
        if isinstance(param[k], dict):
            res = json.dumps(param[k]).replace(' ', '')
        list_param.append("%s=%s" % (k, res))
    if is_sha1:
        list_param.extend(['key=%s' % (sign_key)])
    else:
        list_param.extend(['sign=%s' % (sign_key)])
    str_sign = '&'.join(list_param)

    # res = hashlib.sha1(str_sign).hexdigest()
    if is_sha1:
        res = hashlib.sha1(str_sign.encode('utf-8')).hexdigest()
        return res
    else:
        return str_sign


def trans_error_to_json(response):
    """is_success = F & error = OVER_MAX_VISIT_COUNT"""
    ret = {}
    result_list = response.replace(' ', '').split('&')
    for ele in result_list:
        key_value = ele.split('=')
        key, value = key_value[0], key_value[1]
        ret.update({key: value})
    return ret


def record_requests(api_type, user_id, order_num, result):
    """ 对请求进行记录 """
    pass


import functools


def retry(max_t=5):
    def decators(func):
        @functools.wraps(func)
        def wrappers(*args, **kwargs):
            index, ret = 0, None
            while index < max_t:
                try:
                    ret = func(*args, **kwargs)
                except Exception:
                    index += 1
                else:
                    if ret.status_code == 200:
                        break
                    else:
                        index += 1
            if ret is None:
                ret = type(__name__, (object, ), {
                    "text": ""
                })()
            return ret
        return wrapper
    return decators


def net_get_data_handle(url, data):
    """
    """
    index = 1
    res = None
    while index <= 3:  # 如果出现系统错误,是需要重试的
        res = requests.post(url, data=data)
        if res.status_code != 200:
            return {}
        if res.status_code == 200 or res.status_code == '200':
            if 'SYSTEM_ERROR' in res.text:
                index += 1
                continue
            else:
                break
        index += 1

    # return res
    if 'success=F' in res.text:
        return trans_error_to_json(str(res.text))

    # 将里面有用的信息提取出来
    index = 0
    while index < len(res.text):
        if res.text[index] == '{':
            break
        index += 1

    last = len(res.text) - 1
    while last > -1:
        if res.text[last] == '}':
            break
        last -= 1

    ret = json.loads(res.text[index: last + 1])
    if 'result' in ret:
        ret['result'] = json.loads(ret['result'])
        return ret
    else:
        return {'result': {}}


class HttpRequestFactory(object):
    """ factory mode to support testunit"""
    @classmethod
    def create_http_request(cls, product_code):

        def faker_result(url, data):
            return True, {"result": {"MC_IDENT_IDS": {"IDENT_NAME": "一致"}}}
        try:
            return  net_get_data_handle if current_app.config['TESTING'] is False else faker_result
        except:
            return faker_result


def wrapper(name, trade_num, param, url=None, have_pic=0):
    """
    对加密和ulr构造进行封装
    :param name:
    :param kwargs.get("trade_num"):
    :param param:
    :param url:
    :return:
    """
    data = gen_param(name, trade_num, param, have_pic=have_pic)
    sign = encrypt(data, DefaultConfig.SIGNKEY, is_sha1=True)
    paramn_sign = encrypt(data, sign, is_sha1=False)
    # return net_get_data_handle(url or DefaultConfig.URL, paramn_sign)
    return HttpRequestFactory.create_http_request(name)(url or DefaultConfig.URL, paramn_sign)


def compare_today(date_obj, today):
    if date_obj is None:
        date_obj = datetime.datetime.now()
    his = date_obj.strftime("%Y%m%d")
    if his == (today.year + today.month + today.day):
        return True
    return False


def pass_verify(result):
    """ 根据马上给出的结果, 认证是否成功 """
    if result.get("result", {}).get('MC_IDENT_IDS', {}).get("IDENT_NAME", "") == u'一致':
        return True
    return False

def compare_str(a, b):
    if isinstance(a, str):
        a = a.decode("utf-8")
    if isinstance(b, str):
        b = b.decode("utf-8")
    if a == b:
        return True
    return False


class ThirdApiManager(object):
    def __generate_yield(self):
        index = 0
        while True:
            yield str(index)
            index += 1

    def __init__(self):
        self.yield_instance = self.__generate_yield()

    def mashang_idcard(self, **kwargs):
        """ 简项身份核查"""

        def is_pass(kw):
            if kw.get('id_num', None) and kw.get('name', None):
                return True
            else:
                return False

        param = dict(
            username=kwargs.get("name"),
            id_card=kwargs.get("idNum"))
        if kwargs.get("phone"):
            param.update({'phone_number': kwargs.get("phone")})

        func_name = 'DPD_AF_01501'
        ret = wrapper(
            func_name, kwargs.get("tradeNum") + "_" + str(int(time.time())) + next(self.yield_instance) + 'id_card', param)

        # if it is a tuple, it test environment
        if not isinstance(ret, tuple):
            record_requests('DPD_AF_01501', kwargs['userId'], kwargs['tradeNum'], ret)
            return ret
        else:
            return ret[1]