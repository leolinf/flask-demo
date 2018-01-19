# coding: utf-8

import json
import datetime
from functools import wraps
from app.constants import TelPrice as const


class CreditInterface:
    @classmethod
    def undesirable_info(cls, data: json):
        """ 公安不良信息那个接口 """
        ret = []

        def time_handle(d):

            ret, d = '', d.split(" ")[0]
            if '-' not in d:
                ret = d[0:4] + '-' + d[4:6] + '-' + d[6:8]
            else:
                ret = d
            return ret

        try:
            result_l = data.get("data").get("DETAIL").get("checkDetail")
            for ele in result_l:
                time_ = ele.get("caseTime")
                type_ = ele.get("caseType")
                source = ele.get("caseSource")
                ret.append({"type": type_, "time": time_, "source": source})

        except:
            pass
        return {"data": ret}

    @classmethod
    def net_loan_platforms(cls, data):
        """ 网贷逾期多平台 数据处理 """
        if isinstance(data, str):
            data = json.loads(data)
        if not data:
            data = {}
        ret = []
        try:
            d = data.get("data", {}).get("result", [])
            for ele in d:
                i = ele.get("entity")
                ret.append({
                    "overdue_time": i.get("overdueTime", ''),
                    "debt_num": i.get("debtNum", ''),
                    "debt_amt": i.get("debtAmt", ''),
                    "overdue_days": i.get("overdueDays", ''),
                    "update_time": i.get("updateTime", '')
                })
        except:
            pass
        return {
            "data": ret
        }

    @classmethod
    def net_net_loan_risk_check(cls, data):
        """ 网贷风险校验数据处理 """
        if isinstance(data, str):
            data = json.loads(data)
        if not data:
            data = {}
        l = []
        try:
            d_l = data.get("data", {}).get('DETAIL', {}).get("riskDetail", [])
            for d in d_l:
                if d.get("riskKind", '') or d.get("amountRange", '') or d.get("tradeTime", ''):
                    l.append({
                        "risk_kind": d.get("riskKind", ''),
                        "amount_range": d.get("amountRange", ''),
                        "trade_time": d.get("tradeTime", '').replace("/", "-")
                     })
        except:
            l = []
        return {"data": l}

    @classmethod
    def blacklist_check(cls, data):
        """ 黑名单校验 """
        if isinstance(data, str):
            data = json.loads(data)
        if not data:
            data = {}

        try:
            data = data.get("data", {})
            ret = {
                "status":  data.get("RESULT"),
                "result": data.get("RESULT_LIST", "")}
            if str(ret['status']) == '1' and ret['result']:
                ret['status'] = '是'
                return {"data": [ret]}
            else:
                return {"data": []}
        except:
            return {"data": []}

    @classmethod
    def online_time_check(cls, data):
        """ 小视在网时长接口 """
        if not data:
            return {}

        def t_hanle(d):
            if d == 1:
                return "0-3个月"
            elif d == 2:
                return "3-6个月"
            elif d == 3:
                return "6-12个月"
            elif d == 4:
                return "12-24个月"
            elif d == 5:
                return "24个月以上"
            else:
                return "--"

        ret_data = {
            "result":
                {
                    "MC_TECHK": {
                        "RUL_PHONE": "--",
                        "OPR_PHONE": "--"
                    },
                    "MC_TETIME": {"TIME_PHONE": "--"}}}
        try:
            t = data['data']['RESULT']
            ret_data['result']['MC_TETIME']['TIME_PHONE'] = t_hanle(int(t))
        except:
            pass
        return ret_data

    @classmethod
    def cellphone_check(cls, data):
        """ 运营商实名认证和运营商类型 """
        if not data:
            return {}
        ret_data = {
            "code": const.CODE,
            "data": {
                "res_code": "2",
                "res_operator": "--"
            }
        }
        try:
            code = data.get("data", {}).get("RESULT")
            # 对应码可以查看 handle_cellphone.handle_cellphone

            ret_data['data']['res_code'] = code

            c_type = data['data']['TYPE']
            if c_type == 'CHINA_CMCC':
                ret_type = "mobile"
            elif c_type == 'CHINA_UNICOM':
                ret_type = 'unicom'
            elif c_type == 'CHINA_TELECOM':
                ret_type = 'telecom'
            else:
                ret_type = ""
            ret_data['data']['res_operator'] = ret_type
        except:
            pass
        return ret_data

    @classmethod
    def user_contact_info_check(cls, data):
        ret = {
            "idcard_name": 1, # 身份证关联姓名
            "idcard_phone": 1, # 身份证关联手机
            "phone_idcard": 1, # 手机关联身份证
            "phone_name": 1, # 手机管理姓名
        }
        try:
            d = data.get("data")
            ret['idcard_name'] = len(d['idcardName']) or 1
            ret['idcard_phone'] = len(d['idcardPhone']) or 1
            ret['phone_idcard'] = len(d['phoneIdcard']) or 1
            ret['phone_name'] = len(d['phoneName']) or 1
        except:
            pass
        return ret

    @classmethod
    def user_queryed_info_check(cls, data):
        ret = {
            "idcard_record": {
                "one_month": 1,
                "three_month": 1,
                "six_month": 1,
                "one_year": 1
            },
            "phone_record": {
                "one_month": 1,
                "three_month": 1,
                "six_month": 1,
                "one_year": 1}}
        try:
            d = data.get("data")
            ret['idcard_record']['one_month'] = d['idcardRecord']['oneMonth'] or 1
            ret['idcard_record']['three_month'] = d['idcardRecord']['threeMonth'] or 1
            ret['idcard_record']['six_month'] = d['idcardRecord']['sixMonth'] or 1
            ret['idcard_record']['one_year'] = d['idcardRecord']['twelveMonth'] or 1

            ret['phone_record']['one_month'] = d['phoneRecord']['oneMonth'] or 1
            ret['phone_record']['three_month'] = d['phoneRecord']['threeMonth'] or 1
            ret['phone_record']['six_month'] = d['phoneRecord']['sixMonth'] or 1
            ret['phone_record']['one_year'] = d['phoneRecord']['twelveMonth'] or 1
        except:
            pass
        return ret
