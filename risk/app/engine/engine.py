# -*- coding = utf-8 -*-
import datetime
import json
import logging
import operator
import re
from functools import wraps

import jieba
from sqlalchemy.orm import scoped_session

from app import Session
from app.constants import ReceiveType
from app.credit.pipeline import handle_operator_multiplatform, handle_multiple_loan_apply_a, handle_obtain_piccompare, \
    handle_operator_phonetime, handle_multiple_loan_apply_b, handle_netloan_platforms, handle_overdue_b, \
    handle_overdue_c, handle_financial_bad, no_faith, handle_obtain_riskinfocheck
from app.models import InputApply, BreakRule


DEFAULT_DENY_RULE = [
    "or",
    ["deny_operator_multiplatform", 1, ">", 0],
    ["deny_multiple_loan_apply_a", 1, ">", 0],
    ["deny_linkman_apply_limit", 1, ">", 0],
    ["deny_obtain_piccompare", 1, "<", 600],
    ["deny_address_check", 1, ">", 500],
    ["deny_phone_online", 1, "<", 6],
    ["deny_multi_loan_apply_b", 1, ">", 0],
    ["deny_net_loan_overdue_platforms", 1, ">", 0],
    ["deny_overdue_b", 1, ">", 0],
    ["deny_overdue_c", 1, ">", 0],
    ["deny_financial_bad", 1, ">", 0],
    ["deny_no_faith_list", 1, ">", 0],
    ["deny_obtain_riskinfocheck", 1, ">", 0],
    ["deny_address_check_taobao", 1, ">", 500],
    ["deny_operator_1", 1, ">", 1],
    ["deny_operator_2", 1, ">", 1],
    ["deny_operator_3", 1, "<", 10],
    ["deny_operator_4", 1, "<", 10],
    ["deny_operator_5", 1, ">", 10],
    ["deny_operator_6", 1, ">", 60],
    ["deny_operator_7", 1, ">", 0.5],
    ["deny_operator_8", 1, ">", 0.5],
    ["deny_operator_9", 1, ">", 0.5],
    ["deny_operator_10", 1, ">", 5],
    ["deny_operator_11", 1, ">", 0.5],
]


DEFAULT_PASS_RULE = [
    "and",
    ["pass_multiple_loan", 1, "<", 3],
    ["pass_overdue", 1, "<", 1],
]


def record_break_rule(apply_number, key, value):

    BreakRule.objects(apply_number=apply_number).update(
        upsert=True,
        add_to_set__break_rule=[key, value],
    )


def check_switch(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        switch = args[3]
        if not switch:
            return False
        return func(*args, **kwargs)
    return wrapper


class Engine(object):

    def __init__(self, rule, input_apply, search):

        """

        :type rule: list
        """
        if isinstance(rule, str):
            rule = json.loads(rule)
        self.rule = rule
        self.input_apply = input_apply
        self.search = search

    def _evaluate(self, rule, fns):

        def _recurse_eval(arg):
            if isinstance(arg, list):
                return self._evaluate(arg, fns)
            else:
                return arg

        r = list(map(_recurse_eval, rule))
        r[0] = fns.ALIAS[r[0]]
        func = getattr(fns, r[0])
        resp = func(self.input_apply, self.search, *r[1:])
        if r[0].startswith("deny_"):
            logging.info("{0} 结果: {1}".format(r[0], "拒绝" if resp else "不拒绝"))
        elif r[0].startswith("pass_"):
            logging.info("{0} 结果: {1}".format(r[0], "通过" if resp else "不通过"))
        else:
            logging.info("{0} 结果: {1}".format(r[0], resp))
        return resp

    def evaluate(self):

        fns = Function()
        ret = self._evaluate(self.rule, fns)
        return ret


class Function(object):
    """引擎函数"""

    ALIAS = {
        ">": "gt",
        "<": "lt",
        "and": "and_",
        "or": "or_",
        "deny_operator_multiplatform": "deny_operator_multiplatform",
        "deny_multiple_loan_apply_a": "deny_multiple_loan_apply_a",
        "deny_linkman_apply_limit": "deny_linkman_apply_limit",
        "deny_obtain_piccompare": "deny_obtain_piccompare",
        "deny_address_check": "deny_address_check",
        "deny_phone_online": "deny_phone_online",
        "deny_multi_loan_apply_b": "deny_multi_loan_apply_b",
        "deny_net_loan_overdue_platforms": "deny_net_loan_overdue_platforms",
        "deny_overdue_b": "deny_overdue_b",
        "deny_overdue_c": "deny_overdue_c",
        "deny_financial_bad": "deny_financial_bad",
        "deny_no_faith_list": "deny_no_faith_list",
        "deny_obtain_riskinfocheck": "deny_obtain_riskinfocheck",
        "deny_address_check_taobao": "deny_address_check_taobao",
        "deny_operator_1": "deny_operator_1",
        "deny_operator_2": "deny_operator_2",
        "deny_operator_3": "deny_operator_3",
        "deny_operator_4": "deny_operator_4",
        "deny_operator_5": "deny_operator_5",
        "deny_operator_6": "deny_operator_6",
        "deny_operator_7": "deny_operator_7",
        "deny_operator_8": "deny_operator_8",
        "deny_operator_9": "deny_operator_9",
        "deny_operator_10": "deny_operator_10",
        "deny_operator_11": "deny_operator_11",
        "pass_multiple_loan": "pass_multiple_loan",
        "pass_overdue": "pass_overdue",
    }

    @staticmethod
    def gt(x, y):
        return x > y

    @staticmethod
    def lt(x, y):
        return x < y

    @staticmethod
    def and_(input_apply, search, *args):
        return all(args)

    @staticmethod
    def or_(input_apply, search, *args):
        return any(args)

    @check_switch
    def deny_operator_multiplatform(self, input_apply, search, switch, op, threshold):
        """多平台借贷W1 多平台借贷注册校验（D平台）"""

        result = handle_operator_multiplatform(search.operator_multiplatform_data)
        num = len(result["targetList"])

        if not num:
            return False

        if getattr(self, self.ALIAS[op])(num, threshold):
            record_break_rule(input_apply.id, "多平台申请校验", "注册贷款平台{0}个。大于{1}个时，多头负债风险高。".format(num, threshold))
            return True
        return False

    @check_switch
    def deny_multiple_loan_apply_a(self, input_apply, search, switch, op, threshold):
        """信贷整合查询W1 多平台借贷申请校验（B平台）"""

        result = handle_multiple_loan_apply_a(search.multiple_loan_apply_a)
        num = len(result["targetList"])

        if not num:
            return False

        if getattr(self, self.ALIAS[op])(num, threshold):
            record_break_rule(input_apply.id, "多平台申请校验", "申请贷款平台{0}个。大于{1}个时，多头负债风险高。".format(num, threshold))
            return True
        return False

    @check_switch
    def deny_linkman_apply_limit(self, input_apply, search, switch, op, threshold):
        """联系人申请限制"""

        session = scoped_session(Session)
        num = session.query(InputApply).filter(
            InputApply.name.in_([
                input_apply.school_contact_phone,
                input_apply.work_contact_phone,
                input_apply.home_mem_phone,
            ])).count()
        session.remove()

        if getattr(self, self.ALIAS[op])(num, threshold):
            record_break_rule(input_apply.id, "联系人信息校验", "联系人手机号码存在申请。")
            return True
        return False

    @check_switch
    def deny_obtain_piccompare(self, input_apply, search, switch, op, threshold):
        """人像相似度校验"""

        face_score = handle_obtain_piccompare(search.obtain_piccompare)["faceScore"]
        if not face_score:
            return False

        face_score = float(face_score)
        if getattr(self, self.ALIAS[op])(face_score * 100, threshold):
            record_break_rule(input_apply.id, "身份验证", "人像认证不一致。")
            return True
        return False

    @check_switch
    def deny_address_check(self, input_apply, search, switch, op, threshold):
        """地址位置校验 申请时定位信息与商户地址"""

        # 不是消费分期的不管
        if input_apply.merchant.product.recieve_type != ReceiveType.CLIENT:
            return False

        if search.distance and isinstance(search.distance, dict):
            distance = search.distance.get("apply2bussiness")
            if not distance:
                return False

            if getattr(self, self.ALIAS[op])(distance, threshold):
                record_break_rule(input_apply.id, "地址校验", "消费分期申请时定位信息与商户地址距离{0}米。大于{1}米时，有欺诈风险。".format(distance, threshold))
            return True

        return False

    @check_switch
    def deny_phone_online(self, input_apply, search, switch, op, threshold):
        """在网时长校验"""

        result = handle_operator_phonetime(search.operator_phonetime_data)

        def _process(time_range):

            if time_range == "0-6个月":
                time_number = 6
            elif time_range == "6-12个月":
                time_number = 12
            elif time_range == "12-24个月":
                time_number = 24
            else:
                time_number = 100

            return time_number

        resp = _process(result["timeRange"])

        # 没数据就不管
        if not resp:
            return False

        if getattr(self, self.ALIAS[op])(resp, threshold):
            record_break_rule(input_apply.id, "运营商在网时长验证", "手机号码在网时长{0}。失联风险高。".format(result["timeRange"]))
            return True
        return False

    @check_switch
    def deny_multi_loan_apply_b(self, input_apply, search, switch, op, threshold):
        """多平台借贷申请校验（C平台）借款人风险查询-晟盾接口"""

        resp = handle_multiple_loan_apply_b(search.multiple_loan_apply_b)

        num = len(resp["targetList"])

        if not num:
            return False

        if getattr(self, self.ALIAS[op])(num, threshold):
            record_break_rule(input_apply.id, "多平台申请校验", "申请贷款平台{0}个。大于{1}个时，多头负债风险高。".format(num, threshold))
            return True
        return False

    @check_switch
    def deny_net_loan_overdue_platforms(self, input_apply, search, switch, op, threshold):
        """网贷逾期校验（A平台） 网贷逾期黑名单T1-中诚信接口"""

        resp = handle_netloan_platforms(search.channel_netloanblacklist)

        num = len(resp["targetList"])

        if not num:
            return False

        if getattr(self, self.ALIAS[op])(num, threshold):
            record_break_rule(input_apply.id, "逾期记录", "历史最长逾期{0}天。大于{1}天时，欺诈风险高。".format(num, threshold))
            return True
        return False

    @check_switch
    def deny_overdue_b(self, input_apply, search, switch, op, threshold):
        """网贷逾期B平台校验 信贷整合查询-晟盾"""

        resp = handle_overdue_b(search.overdue_b)
        num = len(resp["targetList"])

        if not num:
            return False

        if getattr(self, self.ALIAS[op])(num, threshold):
            record_break_rule(input_apply.id, "逾期记录", "历史逾期最大笔数{0}。大于{1}天时，欺诈风险高。".format(num, threshold))
            return True
        return False

    @check_switch
    def deny_overdue_c(self, input_apply, search, switch, op, threshold):
        """网贷逾期C平台校验 借款人风险查询-晟盾"""

        resp = handle_overdue_c(search.overdue_c)
        num = len(resp["targetList"])

        if not num:
            return False

        if getattr(self, self.ALIAS[op])(num, threshold):
            record_break_rule(input_apply.id, "逾期记录", "历史最长逾期{0}天。大于{1}天时，欺诈风险高。".format(num, threshold))
            return True
        return False

    @check_switch
    def deny_financial_bad(self, input_apply, search, switch, op, threshold):
        """黑名单-行业风险信息校验 借款人风险查询-晟盾"""

        resp = handle_financial_bad(search.financial_bad)
        num = len(resp["targetList"])

        if not num:
            return False

        if getattr(self, self.ALIAS[op])(num, threshold):
            record_break_rule(input_apply.id, "身份号关联验证", "三个月身份证关联{0}个手机号，违约风险高。".format(num))
            return True
        return False

    @check_switch
    def deny_no_faith_list(self, input_apply, search, switch, op, threshold):
        """黑名单-失信校验 失信执行查询-中诚信接口"""

        resp = no_faith(search.no_faith_list)
        num = len(resp["targetList"])

        if not num:
            return False

        if getattr(self, self.ALIAS[op])(num, threshold):
            record_break_rule(input_apply.id, "失信行为校验", "本人身份证号命中失信被执行。")
            return True
        return False

    @check_switch
    def deny_obtain_riskinfocheck(self, input_apply, search, switch, op, threshold):
        """黑名单-公安不良信息校验 不良信息查询W1-维氏盾接口"""

        resp = handle_obtain_riskinfocheck(search.obtain_riskinfocheck_data)
        num = len(resp["targetList"])

        if not num:
            return False

        if getattr(self, self.ALIAS[op])(num, threshold):
            record_break_rule(input_apply.id, "公安不良校验", "本人身份证号命中公安不良信息。")
            return True
        return False

    @check_switch
    def deny_address_check_taobao(self, input_apply, search, switch, op, threshold):
        """地址校验 淘宝最近收货地址（淘宝最多收货地址）与家庭地址或单位地址"""

        if search.distance and isinstance(search.distance, dict):
            distance_1 = search.distance.get("live2third", 0) or 0
            distance_1 = float(distance_1)
            distance_2 = search.distance.get("third2work", 0) or 0
            distance_2 = float(distance_2)
            if not distance_1 and not distance_2:
                return False

            func = getattr(self, self.ALIAS[op])
            if func(distance_1, threshold) and func(distance_2, threshold):
                record_break_rule(
                    input_apply.id,
                    "淘宝授权验证", "淘宝最近收货地址（淘宝最多收货地址）与家庭地址相距{0}米.，且单位地址相距{1}米.，大于{2}米时，欺诈风险高。".format(
                        distance_1, distance_2, threshold))
            return True

        return False

    @check_switch
    def deny_operator_1(self, input_apply, search, switch, op, threshold):
        """运营商授权-近1个月贷款类号码呼叫"""

        operator_data = search.operator_data.get("callback_operator", {}) if search.operator_data else {}
        if not operator_data or operator_data.get('code') != 31000:
            return False

        call_records_info = operator_data.get('data', {}).get('deceitRisk', {}).get('monthCallInfo', {}).get('oneMonth', {}).get('callList', [])
        call_list = [i for i in call_records_info if '贷款中介' in (i.get('remark', '') or '')]
        call_set = []
        for i in call_list:
            if i in call_set:
                continue
            call_set.append(i.get("peer_number"))

        num = len(set(call_set))

        if getattr(self, self.ALIAS[op])(num, threshold):
            record_break_rule(input_apply.id, "运营商授权验证", "近1个月主动呼叫贷款类号码{0}个,多头负债风险高。".format(num))
            return True
        return False

    @check_switch
    def deny_operator_2(self, input_apply, search, switch, op, threshold):
        """运营商授权-近3个月贷款类号码呼叫"""

        operator_data = search.operator_data.get("callback_operator", {}) if search.operator_data else {}
        if not operator_data or operator_data.get('code') != 31000:
            return False

        call_records_info = operator_data.get('data', {}).get('deceitRisk', {}).get('monthCallInfo', {}).get('threeMonth', {}).get('callList', [])
        call_list = [i for i in call_records_info if '贷款中介' in (i.get('remark', '') or '')]
        call_set = []
        for i in call_list:
            if i in call_set:
                continue
            call_set.append(i.get("peer_number"))

        num = len(set(call_set))

        if getattr(self, self.ALIAS[op])(num, threshold):
            record_break_rule(input_apply.id, "运营商授权验证", "近3个月主动呼叫贷款类号码{0}个,多头负债风险高。".format(num))
            return True
        return False

    @check_switch
    def deny_operator_3(self, input_apply, search, switch, op, threshold):
        """运营商授权-月平均联系人数量"""

        operator_data = search.operator_data.get("callback_operator", {}) if search.operator_data else {}
        if not operator_data or operator_data.get('code') != 31000:
            return False

        num = operator_data.get('data', {}).get('deceitRisk', {}).get('monthCallInfo', {}).get('sixMonth', {}).get('contactsNum', None)

        if num is None:
            return False

        if getattr(self, self.ALIAS[op])(num / 6, threshold):
            record_break_rule(input_apply.id, "运营商授权验证", "近6个月月均联系人数量{0}人。小于{1}人时，失联风险高。".format(num, threshold))
            return True
        return False

    @check_switch
    def deny_operator_4(self, input_apply, search, switch, op, threshold):
        """运营商授权-月平均互通电话数"""

        operator_data = search.operator_data.get("callback_operator", {}) if search.operator_data else {}
        if not operator_data or operator_data.get('code') != 31000:
            return False

        num = operator_data.get('data', {}).get('deceitRisk', {}).get('monthCallInfo', {}).get('sixMonth', {}).get('mutualNum', None)

        if num is None:
            return False

        if getattr(self, self.ALIAS[op])(num / 6, threshold):
            record_break_rule(input_apply.id, "运营商授权验证", "近6个月月均互通电话数量{0}人。小于{1}人时，失联风险高。".format(num, threshold))
            return True
        return False

    @check_switch
    def deny_operator_5(self, input_apply, search, switch, op, threshold):
        """运营商授权-连续静默时长"""

        operator_data = search.operator_data.get("callback_operator", {}) if search.operator_data else {}
        if not operator_data or operator_data.get('code') != 31000:
            return False

        src = operator_data.get('data', {}).get('deceitRisk', {}).get('silenceInfo', [])
        num = 0

        def _trans_time(t):
            return datetime.datetime.strptime(t, "%Y%m%d")

        for i, item in enumerate(src):
            if i == 0:
                continue

            n = (_trans_time(item["connDate"]) - _trans_time(src[i-1]["connDate"])).days
            if n > num:
                num = n

        if not num:
            return False

        if getattr(self, self.ALIAS[op])(num, threshold):
            record_break_rule(input_apply.id, "运营商授权验证", "近6个月手机号连续静默时间{0}天，大于{1}时，拒绝。".format(num, threshold))
            return True
        return False

    @check_switch
    def deny_operator_6(self, input_apply, search, switch, op, threshold):
        """运营商授权-直属亲属联系"""

        operator_data = search.operator_data.get("callback_operator", {}) if search.operator_data else {}
        if not operator_data or operator_data.get('code') != 31000:
            return False
        if not input_apply.home_mem_phone:
            return False

        data = operator_data.get("data", {}).get("callRecordsInfo", [])
        d = {}

        def _map(record):
            d[record["phoneNo"]] = record["lastCallTime"]

        list(map(_map, data))

        if input_apply.home_mem_phone not in d:
            record_break_rule(input_apply.id, "运营商授权验证", "与直系亲属近{0}个月无联系。大于{1}天时，失联风险高。".format(3, threshold))
            return True

        try:
            num = - (datetime.datetime.fromtimestamp(d[input_apply.home_mem_phone]) - input_apply.create_time).days
        except:
            return False

        if getattr(self, self.ALIAS[op])(num, threshold):
            record_break_rule(input_apply.id, "运营商授权验证", "近6个月手机号连续静默时间{0}天，大于{1}时，拒绝。".format(num, threshold))
            return True
        return False

    @check_switch
    def deny_operator_7(self, input_apply, search, switch, op, threshold):
        """运营商授权-近3月异地通话"""

        operator_data = search.operator_data.get("callback_operator", {}) if search.operator_data else {}
        if not operator_data or operator_data.get('code') != 31000:
            return False

        remote_num = operator_data.get('data', {}).get('deceitRisk', {}).get('monthCallInfo', {}).get('threeMonth', {}).get('remoteNum', 0) or 0
        all_num = operator_data.get('data', {}).get('deceitRisk', {}).get('monthCallInfo', {}).get('threeMonth', {}).get('allNum', 0) or 0

        if not all_num:
            return False

        num = float(remote_num) / all_num

        if getattr(self, self.ALIAS[op])(num, threshold):
            record_break_rule(input_apply.id, "运营商授权验证", "近3个月异地通话时间占比{0:.2f}%。大于{1:.2f}%，违约风险高。".format(num * 100, threshold * 100))
            return True
        return False

    @check_switch
    def deny_operator_8(self, input_apply, search, switch, op, threshold):
        """运营商授权-近6月异地通话"""

        operator_data = search.operator_data.get("callback_operator", {}) if search.operator_data else {}
        if not operator_data or operator_data.get('code') != 31000:
            return False

        remote_num = operator_data.get('data', {}).get('deceitRisk', {}).get('monthCallInfo', {}).get('sixMonth', {}).get('remoteNum', 0) or 0
        all_num = operator_data.get('data', {}).get('deceitRisk', {}).get('monthCallInfo', {}).get('sixMonth', {}).get('allNum', 0) or 0

        if not all_num:
            return False

        num = float(remote_num) / all_num

        if getattr(self, self.ALIAS[op])(num, threshold):
            record_break_rule(input_apply.id, "运营商授权验证", "近6个月异地通话时间占比{0:.2f}%。大于{1:.2f}%，违约风险高。".format(num * 100, threshold * 100))
            return True
        return False

    @check_switch
    def deny_operator_9(self, input_apply, search, switch, op, threshold):
        """运营商授权-同城申请判断 op和threshold随便写没用"""

        operator_data = search.operator_data.get("callback_operator", {}) if search.operator_data else {}
        if not operator_data or operator_data.get('code') != 31000:
            return False

        home = input_apply.home_live_address
        work = input_apply.work_address

        def _parse_address(addr):
            """尝试解析地址
            因为java填的空地址很日求，有null，[]，和["", "", ""]等多种形态
            """

            try:
                addr = json.loads(addr)
            except:
                return False

            if not addr:
                return False

            if isinstance(addr, list) and len(addr) > 1 and addr[0] and addr[1]:
                return addr[0], addr[1]

            return False

        home_addr = _parse_address(home)
        work_addr = _parse_address(work)
        # 没有家庭地址和单位地址就不管
        if not home_addr and not work_addr:
            return False

        call_place_info = operator_data.get("data", {}).get("callPlaceInfo", []) or []

        if not call_place_info:
            return False

        call_place_info.sort(reverse=True, key=operator.itemgetter("connTimes"))

        first = call_place_info[0]["commType"]
        if not first:
            return False

        first = list(jieba.cut(first))
        if len(first) == 1:
            return False

        flag = True
        if home_addr and (re.match(first[0], home_addr[0]) or re.match(home_addr[0], first[0])) and (re.match(first[1], home_addr[1]) or re.match(home_addr[1], first[1])):
            flag = False
        if work_addr and (re.match(first[0], work_addr[0]) or re.match(work_addr[0], first[0])) and (re.match(first[1], work_addr[1]) or re.match(work_addr[1], first[1])):
            flag = False

        return flag

    @check_switch
    def deny_operator_10(self, input_apply, search, switch, op, threshold):
        """运营商授权-疑似催收号码"""

        operator_data = search.operator_data.get("callback_operator", {}) if search.operator_data else {}
        if not operator_data or operator_data.get('code') != 31000:
            return False

        num = operator_data.get('data', {}).get('deceitRisk', {}).get('monthCallInfo', {}).get('threeMonth', {}).get('collectionNum', 0) or 0

        if getattr(self, self.ALIAS[op])(num, threshold):
            record_break_rule(input_apply.id, "运营商授权验证", "近3个月疑似催收号码出现{0}个。多头负债风险高。".format(num))
            return True
        return False

    @check_switch
    def deny_operator_11(self, input_apply, search, switch, op, threshold):
        """运营商授权-夜间通话占比"""

        operator_data = search.operator_data.get("callback_operator", {}) if search.operator_data else {}
        if not operator_data or operator_data.get('code') != 31000:
            return False

        data = operator_data.get('data', {}).get('deceitRisk', {}).get("callDuration", []) or []

        def judge_night(d):
            """判断是不是夜间"""
            def calcu(t):
                try:
                    if 0 <= int(t[0:2]) <= 4:
                        return True
                    return False
                except:
                    return False

            if d['connTime'] == '2330' or d['connTime'] == '0500' or calcu(d['connTime']):
                return True
            return False

        night_count, sum_ = 0, 0
        for ele in data:
            sum_ += int(ele.get('connTimes', 0))
            if judge_night(ele) is True:
                night_count += int(ele.get('connTimes', 0))

        if not sum_:
            return False

        resp = float(night_count) / sum_

        if getattr(self, self.ALIAS[op])(resp, threshold):
            record_break_rule(input_apply.id, "运营商授权验证", "近3个月夜间通话占比{0:.2f}%，违约风险高。".format(resp * 100))
            return True
        return False

    @check_switch
    def pass_multiple_loan(self, input_apply, search, switch, op, threshold):
        """多平台借贷注册、申请校验（D、B、C平台)"""

        result = handle_operator_multiplatform(search.operator_multiplatform_data)
        num_1 = len(result["targetList"])
        result = handle_multiple_loan_apply_a(search.multiple_loan_apply_a)
        num_2 = len(result["targetList"])
        result = handle_multiple_loan_apply_b(search.multiple_loan_apply_b)
        num_3 = len(result["targetList"])

        num = sum([num_1, num_2, num_3])

        return getattr(self, self.ALIAS[op])(num, threshold)

    @check_switch
    def pass_overdue(self, input_apply, search, switch, op, threshold):
        """网贷逾期校验（A、B、C平台）"""

        resp = handle_netloan_platforms(search.channel_netloanblacklist)
        num_1 = len(resp["targetList"])
        resp = handle_overdue_b(search.overdue_b)
        num_2 = len(resp["targetList"])
        resp = handle_overdue_c(search.overdue_c)
        num_3 = len(resp["targetList"])

        num = sum([num_1, num_2, num_3])

        return getattr(self, self.ALIAS[op])(num, threshold)


if __name__ == '__main__':

    from app import create_app
    from app.models import SingleSearch

    create_app()
    session = Session()

    apply_number = 6313661603627665411

    search = SingleSearch.objects(apply_number=apply_number).first()
    input_apply = session.query(InputApply).get(apply_number)

    # engine = Engine(DEFAULT_DENY_RULE, input_apply, search)
    engine = Engine(DEFAULT_PASS_RULE, input_apply, search)
    res = engine.evaluate()
    session.close()
