# -*- encoding: utf-8 -*-

import time
import json
import re
import operator
from itertools import groupby

from app.constants import TelPrice as const
from app.core.logger import project_logger
from app.core.functions import time_change, time_change_phone
import datetime
from app.databases import session_scope
from app.models.sqlas import InputApply


def portait(response):
    """金融用户画像"""

    def _fun(ratio):
        try:
            return '%.2f'%(float(ratio)*100) + "%"
        except ValueError:
            return ""

    def _tag(tag_data):
        tag = []
        for k,v in tag_data.items():
            if k[2: -4]:
                if len(k[2: -4]) == 1:
                    tag.append(k[2:-2])
                else:
                    tag.append(k[2: -4])
            else:
                tag.append(k[2: -2])
        return tag

    if response:
        if response.get("code") == const.CODE:
            info_list = response.get("data").get("info_list")
            if info_list:
                for i in info_list:
                    consumeGrade = int(i.get("consume_sumlevel"))
                    consumeSituation = {}
                    consumeSituation["isRealName"] = i.get("consume_auth")
                    consumeSituation["liveness"] = i.get("consume_act")
                    consumeSituation["percent"] = i.get("m_bfifty_cnt_ratio")
                    consumeSituation["registerTime"] = i.get("consume_year")
                    consumeTags = _tag(i.get("tag"))
                    consumeTrend = [{"name": k, "percent": v} for k,v in i.get("favor_leaf_cat").items()]
                    priceTrend = [{"name": k, "percent": v} for k,v in i.get("favor_brand").items()]
                return {"consumeGrade": consumeGrade, "consumeSituation": consumeSituation,
                        "consumeTags": consumeTags, "consumeTrend": consumeTrend,
                        "priceTrend": priceTrend}

    return {"consumeGrade": -100, "consumeSituation":{
                "isRealName": "", "liveness": '',"percent": "", "registerTime": ""},
                "consumeTags": [], "consumeTrend": [],
                "priceTrend": []
        }


def tel_list_pipe(response):
    """电商消费记录过滤"""
    portait_data = portait(response.get("portait_data"))
    resp = response.get("phone_list")
    if resp:
        if resp.get("code") == const.CODE:
            info_list = resp.get("data").get("info_list")
            if info_list:
                priceCompare = []
                tel_list = sorted(info_list, key=operator.itemgetter("category_name"))
                for k, v in groupby(tel_list, operator.itemgetter("category_name")):
                    data = list(v)
                    priceCompare.append({
                        "type": k,
                        "average": float(const.DATA_DICT.get(k) if const.DATA_DICT.get(k) else 0),
                        "singlePrice": sum(float(i.get("price")) for i in data) / float(len(data))})
                portait_data.update({"priceCompare": priceCompare})
                return portait_data
    portait_data.update({"priceCompare": []})
    return portait_data


def tel_risk(response):
    """电商高危接口请求"""

    if response:
        if response.get("code") == const.CODE:
            hit = 0
            info_list = response.get("data").get("info_list")
            if info_list:
                for i in info_list:
                    if "phone" in i:
                        i.pop("phone")
                    if "keywords" in i:
                        i["keyword"] = i.pop("keywords")
                    if "buytime" in i:
                        i["orderTime"] = time_change(i.pop("buytime"))
                hit = len(info_list)
            return {'isTarget': 1 if hit else 0, 'targetNum': hit, 'targetList': info_list}
    return {'isTarget': 0, 'targetNum': 0, 'targetList': []}


def many_plat(response):
    """多平借贷"""

    if response:
        if response.get("code") == const.CODE:
            plat_num = response.get("data").get("plat_num")
            target_list = []
            plat_list = response.get("data").get("plat_list")
            if plat_list:
                for i in plat_list:
                    if i.get("flag") == 1:
                        target_list.append(i.get("platfrom"))
            return {'isTarget': 1 if plat_num else 0, 'loanNum': plat_num, 'targetList': target_list}
    return {'isTarget': 0, 'loanNum': 0, 'targetList': []}



def phone_relative(response):
    """手机号关联多账户"""

    if response:
        if response.get("code") == const.CODE:
            info = response.get("data").get("info_list")
            cache = 3
            if info:
                if "phone" in info:
                    info.pop("phone")
                if all([v <3 for v in info.values()]):
                    cache = 1
                else:
                    cache = 2
            a = {'isTarget': cache}
            if info:
                a.update(info)
            return a
    return {'isTarget': 3}


def info_danger(response):
    """信息平台高危清单"""

    if response:
        if response.get("code") == const.CODE:
            hit = 0
            info = None
            info_list = response.get("data").get("info_list")
            if info_list:
                info = [{"keyword": i.get("keywords", ""), "content": i.get("title", "")} for i in info_list]
                hit = len(info_list)
            return {'isTarget': 1 if hit else 0, 'targetNum': hit, 'targetList': info if info else []}
    return {'isTarget': 0, 'targetNum': 0, 'targetList': []}


def phone_mark_black(response):
    """手机号标注黑名单"""

    if response:
        if response.get("code") == const.CODE:
            info_list = []
            info = response.get("data").get("info_list")
            cache = False
            if info:
                for i in info:
                    tag = i.get("tag", "")
                    amount = i.get("amount", 0)
                    if tag:
                        info_list.append({"markNum": amount, "markType": tag})
                        if u'公司' not in tag and amount:
                            cache = True
            return {'isTarget': 1 if cache else 0, 'targetNum': 0, 'targetList': info_list}
    return {'isTarget': 0, 'targetNum': 0, 'targetList': []}


def phone_mark_enterprise(response):
    """公司被标注"""

    if response:
        if response.get("code") == const.CODE:
            info = response.get("data").get("info_list")
            if info:
                for i in info:
                    tag = i.get("tag", "")
                    if "公司" in tag:
                        return tag
    return ""



def phone_active(response):
    """手机活跃度综合校验"""

    if response:
        if response.get("code") == const.CODE:
            info = response.get("data").get("info_list")
            if info is None:
                return {}
            for k, v in info.items():
                if k == 'elec_regtime' and v != '-':
                    info[k] = time_change_phone(v)
                if k == 'social_regtime' and v != '-':
                    info[k] = time_change(v)
            return info if info else {}
    return {}


def social_danger(response):
    """社交平台高位数据"""

    if response:
        if response.get("code") == const.CODE:
            info_list = response.get("data").get("info_list")
            hit = 0
            info = None
            _attentionList = []
            if info_list:
                social_info = []
                for i in info_list:
                    keyword = ""
                    content = ""
                    if i.get("desc_keywords", ""):
                        keyword = i.get("desc_keywords")
                    if i.get("nick_keywords", ""):
                        keyword += i.get("nick_keywords")
                    if i.get("description", ""):
                        content = i.get("description")
                    if i.get("screen_name", ""):
                        content += i.get("screen_name")
                    if keyword and content:
                        social_info.append({"keyword": keyword, "content": content})
                attentionList = '|'.join([i.get("finance_weibonames") for i in info_list if i.get("finance_weibonames")])
                _attentionList = [i for i in set(attentionList.split("|")) if i]
                hit = len(info_list)
                info = []
                for social in social_info:
                    if any(social.values()):
                        info.append(social)
                hit = len(info)
            return {'isTarget': 1 if hit else 0, 'targetNum': hit,
                    'targetList': info if info else [], 'attentionList': _attentionList}
    return {'isTarget': 0, 'targetNum': 0, 'targetList': [], 'attentionList': []}


def channel_idcard(response):
    """身份验证"""

    code_data = {"0": 2, "-1": 3, "1": 4}
    if response:
        if response.get("status") == "search":
            return {"isId": 1}
        if response.get("code") == const.CODE:
            data = response.get("data")
            return {"isId": code_data[str(data)]}
    return {"isId": 2}


def bank_three(response):
    """银行卡三要素验证"""

    code_data = {"d": 2, "f": 3, "t": 4}
    if response:
        if response.get("status") == 'search':
            return {"isBankNum": 1}
        if response.get("code") == const.CODE:
            data = response.get("data").get("result")
            return {"isBankNum": code_data[str(data)]}
    return {"isBankNum": 2}


def name_idcard_account(response):
    """小视银行卡三要素"""

    code_data = {"3": 2, "2": 3, "1": 4, "-1": 2}
    if response:
        if response.get("status") == 'search':
            return {"isBankNum": 1}
        if response.get("code") == const.CODE:
            data = response.get("data").get("RESULT", "3")
            return {"isBankNum": code_data[str(data)]}
    return {"isBankNum": 2}

def loan_over(response):
    """网贷逾期黑名单"""

    if response:
        if response.get("status") == "search":
            return {'isTarget': 1, 'targetNum': 0, 'targetList': []}
        if response.get("code") == const.CODE:
            info = response.get("data").get("info_list")
            if info:
                info = [{"loanTime": time_change(i.get("borrow_date")),
                         "loanStage": i.get("borrow_nper"),
                         "loanMoney": i.get("time_out_interest"),
                         "overDay": i.get("time_out_days")} for i in info]
            return {'isTarget': 2 if info else 3, 'targetNum': 0, 'targetList': info if info else []}
    return {'isTarget': 3, 'targetNum': 0, 'targetList': []}


def no_faith(response):
    """失信网个人失信黑名单"""

    if response:
        if response.get("status") == "search":
            return {'isTarget': 1, 'targetNum': 0, 'targetList': []}
        if response.get("code") == const.CODE:
            info = response.get("data").get("info_list")
            if info:
                info = [{"court": i.get("courtName") or "--",
                        "performance": i.get("performance") or "--",
                        "detailAction": i.get("duty") or "--",
                        "registerTime": i.get("regDate") or "--",
                        "registerNum": i.get("caseCode") or "--"} for i in info]
            return {'isTarget': 2 if info else 3, 'targetNum': 0, 'targetList': info if info else []}
    return {'isTarget': 3, 'targetNum': 0, 'targetList': []}


def address_search(address, response):
    """地址信息查询"""

    if not address:
        return {'usualAddress': "", 'eAddress': [], 'addressStatus': 1}
    if response:
        if response.get("status") == 'search':
            return {'usualAddress': "", 'eAddress': [], 'addressStatus': 1}
        if response.get("code") == const.CODE:
            info_data = []
            info = response.get("data")
            if info:
                for i in info.get("info_list", []):
                    address_data = ""
                    if i.get("state", ""):
                        address_data += i.get("state", "")
                    if i.get("city", ""):
                        address_data += i.get('city', "")
                    if i.get("address", ""):
                        address_data += i.get("address", "")
                    if address_data not in info_data:
                        info_data.append(address_data)
            return {'usualAddress': address, 'eAddress': info_data if info_data else [],
                    'addressStatus': 2 if info else 3}
    return {'usualAddress': address, 'eAddress': [], 'addressStatus': 3}


def firm_info(response, enterprise_addr):
    """企业工商信息查询"""

    def _fun(data):
        if not data:
            return ""
        else:
            return data

    if response:
        if response.get("code") == const.CODE and response.get("data"):
            base_info = response.get("data").get("Baseinfo")
            if base_info:
                baseInfo =  {}
                baseInfo["companyName"] = _fun(response.get("data").get("companyName", ""))
                baseInfo["Address"] = _fun(base_info["Company"].get("Address", ""))
                baseInfo["EconKind"] = _fun(base_info["Company"].get("EconKind", ""))
                baseInfo["Industry"] = _fun(base_info["Company"].get("Industry").get("Industry", ""))
                baseInfo["RegistCapi"] = _fun(base_info["Company"].get("RegistCapi", ""))
                baseInfo["OperName"] = _fun(base_info["Company"].get("OperName", ""))
                regist = re.findall(r'[0-9]+', _fun(base_info["Company"].get("RegistCapi")))
                if regist:
                    if not int(regist[0]):
                        baseInfo["RegistCapi"] = "--"
                baseInfo["Status"] = _fun(base_info["Company"].get("Status", ""))
                baseInfo["TermStart"] = _fun(base_info["Company"].get("TermStart"))[:10]
                return baseInfo
    return {"Address":"", "EconKind":"", "Industry":"", "RegistCapi": "",
            "Status": "", "TermStart": "", "companyName": "", "OperName": ""}


def firm_shixin(response):
    """失信网企业失信数据"""

    if response:
        if response.get("code") == const.CODE and response.get("data"):
            info_list = response.get("data").get("info_list")
            if info_list:
                ShiXing = []
                for i in info_list:
                    info = {}
                    info["caseCode"] = i.get("caseCode")
                    info["courtName"] = i.get("courtName")
                    info["duty"] = i.get("duty")
                    info["performance"] = i.get("performance")
                    info["regDate"] = i.get("regDate")
                    ShiXing.append(info)
                return ShiXing
    return []


def firm_court(response):
    """法院公告信息"""

    if response:
        if response.get("code") == const.CODE and response.get("data"):
            cements = response.get("data").get("CourtAnnouncements")
            if cements:
                announ = []
                for cement in cements:
                    Court = []
                    for i in cement:
                        if i["key"] == "当事人":
                            Court.append(i)
                        elif i["key"] == "刊登日期":
                            Court.append(i)
                        elif i['key'] == "内容":
                            Court.append(i)
                        elif i['key'] == "公告法院":
                            Court.append(i)
                    if Court:
                        if len(Court) != 4:
                            keys = [i["key"] for i in Court]
                            if "当事人" not in keys:
                                Court.append({"key": "当事人", "value": ""})
                            if "刊登日期" not in keys:
                                Court.append({"key": "刊登日期", "value": ""})
                            if "内容" not in keys:
                                Court.append({"key": "内容", "value": ""})
                            if "公告法院" not in keys:
                                Court.append({"key": "公告法院", "value": ""})
                    announ.append(Court)
                return announ
    return []


def firm_judgment(response):
    """企业裁判文书信息"""

    if response:
        if response.get("code") == const.CODE and response.get("data"):
            judgment = response.get("data").get("JudgmentDocDetail")
            if judgment:
                _CreditCode = []
                for i in judgment:
                    CreditCode = {}
                    CreditCode["CaseName"] = i.get("CaseName")
                    CreditCode["CaseNo"] = i.get("CaseNo")
                    CreditCode["Court"] = i.get("Court")
                    CreditCode["SubmitDate"] = i.get("SubmitDate")
                    _CreditCode.append(CreditCode)
                return _CreditCode
    return []


def firm_zhixing(response):
    """企业被执行信息"""

    if response:
        if response.get("code") == const.CODE and response.get("data"):
            Zhixing = response.get("data").get("Zhixing")
            if Zhixing:
                _zhixing = []
                for i in Zhixing:
                    zhixing =  {}
                    zhixing["Anno"] = i.get("Anno")
                    zhixing["Biaodi"] = i.get("Biaodi")
                    zhixing["Executegov"] = i.get("Executegov")
                    zhixing["Liandate"] = i.get("Liandate")[:10]
                    _zhixing.append(zhixing)
                return _zhixing
    return []


def mashang_credit(response):
    """综合反欺诈"""
    ret, target = [], 0
    j_d = response.get('result') or {}

    def is_target(grade):
        if grade == '中' or grade == '高':
            return 1
        return 0

    for i in j_d.get('MC_CPF', []):
        grade = i.get('RSLE_CPF', '')
        if target == 0 and (is_target(grade) == 1):
            target = 1
        ret.append({
            'name': i.get('RUNA_CPF', ''),
            'grade': grade
        })
    return {
        'isTarget': target,
        'targetList': ret
    }


def mashang_negative(response):
    """马上的 负面信息"""
    if 'result' not in response:
        return {
            'isTarget': 0,
            'isAction': -1,
            'isAntiFraud': -1,
            'isLost': -1
        }

    j_d = response.get('result', {}).get('MC_FRD', {})

    def is_target(grade):
        if grade == '是':
            return 1
        return 0
    action = j_d.get('IF_EXE', '')
    fraud = j_d.get('IF_F', '')
    lost = j_d.get('IF_DC', '')

    def __filter(cont):
        if '是' in cont:
            return 1
        elif '否' in cont:
            return 0
        return -1

    return {
        'isTarget': is_target(action) or is_target(fraud) or is_target(lost),
        'isAction': __filter(action),
        'isAntiFraud': __filter(fraud),
        'isLost': __filter(lost)
    }


def mashang_overdue(response):
    """马上的 逾期信息"""
    if 'result' not in response:
        return {
            'isNow': -1,
            'isPast': -1,
            'isTarget': 0,
        }

    j_d = response.get('result', {}).get('MC_PD', {})

    def __filter(cont):
        if '是' in cont:
            return 1
        elif '否' in cont:
            return 0
        return -1

    def is_target(grade):
        if grade == '是':
            return 1
        return 0

    now_ = j_d.get('IF_OD', '')
    pass_ = j_d.get('IF_ODN', '')

    return {
        'isNow': __filter(now_),
        'isPast': __filter(pass_),
        'isTarget': is_target(now_) or is_target(pass_)
    }


def horse_idcard(id_card):
    """简项身份认证"""

    if id_card.get('is_pass') is True:
        return {'isId': 1}

    if 'result' in id_card:
        t = id_card.get('result', {}).get('MC_IDENT_IDS', {}).get('IDENT_NAME', '')
        if not t:
            return {'isId': 3}
        if '不' in t:
            return {'isId': 3}
        else:
            return {'isId': 4}
    else:
        return {'isId': 1}


def horse_score(score):
    if 'result' in score:
        t = score.get('result', {}).get('MC_CRESCO', {}).get('RUL_SUM', '')
        try:
            t = int(t)
        except Exception:
            t = -100
        return {'score': t}
    else:
        return {'score': -100}


def horse_online(phone_onlin):
    if phone_onlin.get('is_pass') is True:
        return {'isPhone': 1}

    if 'result' in phone_onlin:
        t = phone_onlin.get('result', {}).get('MC_TECHK', {}).get('RUL_PHONE', '')
        if '不' in t:
            return {'isPhone': 3}
        elif '一致' in t:
            return {'isPhone': 4}
        else:
            return {'isPhone': 2}
    else:
        return {'isPhone': 1}


def horse_face_score(score):
    if score.get('is_pass') is True:
        return {'faceScore': ""}

    if 'result' not in score:
        return {'faceScore': ""}
    else:
        score = score.get('result', {}).get(
            'MC_PI', {}).get('SCORE_IDENT', '')

        return {'faceScore': score}


def verifyinfo(response):
    """
    id_card: 简项身份核查
    score: 信用评分
    online: 手机在网时长
    face_score: 人脸验证
    身份认证信息
    """
    other_d = {
        'faceImg': '',
        'isBankNum': '',
    }
    # 这里面所有的信息都需要身份证
    id_card = response['id_num']
    if not id_card:  # 身份证不存在时
        mashang_d = {
            'faceScore': '',
            'isId': 1,
            'isPhone': 1
        }
        mashang_d.update(other_d)
        return mashang_d

    is_query = response['is_query']
    mashang_d = {}

    # 身份证认证
    if is_query.get('mashang_idcard', False) is True:  # 身份证
        if hasattr(response['mashang_idcard'], 'error'):
            mashang_d.update({
                'isId': 2
            })
        else:
            mashang_d.update({
                'isId': (response['mashang_idcard'] or {}).get('result', {}).get('MC_IDENT_IDS', {}).get('IDENT_ID', '')
            })
    else:
        mashang_d.update({
            'isId': 1
        })

    # 人脸认证
    if is_query.get('mashang_face', False) is True:
        if hasattr(response['mashang_online'], 'error'):
            mashang_d.update({'faceScore': 2})
        else:
            mashang_d.update({
                'faceScore': (response['mashang_face'] or {}).get('result', {}).get(
                    'MC_PI', {}).get('SCORE_IDENT', '')
            })
    else:
        mashang_d.update({'faceScore': ''})
    for key, value in mashang_d.items():
        if key == 'faceScore':
            continue
        if value not in [1, 2, 3, 4]:
            if '不' in value:
                mashang_d[key] = 3
            else:
                mashang_d[key] = 4
    mashang_d.update(other_d)
    # 综合得分

    score = response['mashang_score']
    if score is None:
        mashang_d.update({'score': -100})
    else:
        score = score.get('result', {}).get('MC_CRESCO', {}).get('RUL_SUM', '')
        try :
            score = int(score)
        except Exception:
            score = -100
        mashang_d.update({'score': score})
    project_logger.info('verify mashang data: %s ' % json.dumps(mashang_d))
    return mashang_d


def mashang_online(response):
    """手机在网时长"""
    j_d = response.get('result', {})
    return {
        'operator': j_d.get('MC_TECHK', {}).get('OPR_PHONE', ''),
        'phoneStatus': j_d.get('MC_TECHK', {}).get('RUL_PHONE', ''),
        'timeRange': j_d.get('MC_TETIME', {}).get('TIME_PHONE', '')
    }


def mashang_xinyongscore(response):
    """综合信用得分"""
    if response.get('is_pass', None) is True:
        return {'score': ''}

    if response.get('is_success') == 'F':
        return {'score': ''}
    j_d = response.get('result', {})
    return {
        'score': j_d.get('MC_CRESCO', {}).get('RUL_SUM', '')
    }


def change_sort(old_list, sort_key=None):
    """排序"""
    return sorted(old_list, key=operator.itemgetter(sort_key), reverse=True)


def dict_list_util(ret):
    """字典和列表有空数据全部改成×××"""

    if isinstance(ret, list):
        for i in ret:
            dict_list_util(i)

    if isinstance(ret, dict):
        for k, v in ret.items():
            if v == 'unknow' or v == '<undefined>' or\
                    v == '<unknown>' or v == '<null>' or v == 'unknown':
                ret[k] = ""
            if isinstance(ret[k], dict):
                dict_list_util(ret[k])

            if isinstance(ret[k], list):
                dict_list_util(ret[k])


def handler_date(data):
    """处理最近通话记录"""

    if isinstance(data, dict):
        if not data.get("$date", 0):
            return ""
        timeArray = time.localtime(data.get("$date", 0)/1000)
        otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
        return otherStyleTime
    else:
        return data


def operator_base_data(result):
    """运营商基本信息处理"""

    try:
        result = json.loads(result)
    except Exception as e:
        project_logger.info('[OPERATOR][RESULT|%s][ERROR|%s]', result, str(e))
        result = {}
    phoneInfo = result.get("phoneInfo", {})
    _phoneInfo = {
        "addr": phoneInfo.get("addr", ""),
        "balance": phoneInfo.get("balance", -100),
        "email": phoneInfo.get("email", ""),
        "firstCallDate": handler_date(phoneInfo.get("firstCallDate", "")),
        "inNetDate": phoneInfo.get("inNetDate", ""),
        "lastCallDate": handler_date(phoneInfo.get("lastCallDate", "")),
        "operator": phoneInfo.get("operator", ""),
        "pointValue": phoneInfo.get("pointValue", -100),
        "realName": phoneInfo.get("realName", ""),
        "vipLevel": phoneInfo.get("vipLevel", "")
    }
    consumeInfo = result.get("consumeInfo", [])
    _consumeInfo = change_sort([{
        "callTime": i.get("callTime", 0),
        "calledTime": i.get("calledTime", 0),
        "month": i.get("month", ""),
        "payMoney": i.get("payMoney", 0),
        "totalSmsNumber": i.get("totalSmsNumber", 0)
    } for i in consumeInfo], sort_key="month")
    deceitRisk = result.get("deceitRisk", {})

    def _fun(data):
        if data == "False" or data == "false" or data is False:
            return 0
        if data == "True" or data == "true" or data is True:
            return 1
        return -1

    _deceitRisk = {
        "calledByCourtNo": _fun(deceitRisk.get("calledByCourtNo", -1)),
        "longTimePowerOff": _fun(deceitRisk.get("longTimePowerOff", -1)),
        "phoneIsAuth": _fun(deceitRisk.get("phoneIsAuth", -1))
    }
    specialCallInfo = result.get("specialCallInfo", {})
    _specialCallInfo = change_sort([{
            "connTimes": i.get("connTimes", 0),
            "identityInfo": i.get("identityInfo", ""),
            "month": i.get("month", ""),
            "phoneNo": i.get("phoneNo", ""),
            "smsTimes": i.get("smsTimes", 0)
        } for i in specialCallInfo], sort_key="connTimes")

    resp = {
        "phoneInfo": _phoneInfo,
        "consumeInfo": _consumeInfo,
        "deceitRisk": _deceitRisk,
        "specialCallInfo": _specialCallInfo
    }
    dict_list_util(resp)
    return resp


def operator_msg_list(req, result):
    """运营商短信记录"""

    try:
        result = json.loads(result)
    except Exception as e:
        project_logger.info('[OPERATOR][RESULT|%s][ERROR|%s]', result, str(e))
        return [], 0
    page = req["page"]
    count = req["count"]
    messageRecordsInfo = [
        {"belongArea": i.get("belongArea", ""),
        "identifyInfo": i.get("identifyInfo", ""),
        "phoneNo": i.get("phoneNo", ""),
        "totalSmsNumber": i.get("totalSmsNumber", 0)
        } for i in result.get("messageRecordsInfo", [])
        if i.get("identifyInfo", "") or i.get("totalSmsNumber", 0) > 1
    ]
    response = change_sort(messageRecordsInfo, sort_key="totalSmsNumber")
    if req["isMark"] == 1:
        response = [i for i in response if i.get("identifyInfo", "")]
    resp =  response[(page-1)*count : page*count]
    dict_list_util(resp)
    return resp, len(response)


def operator_call_list(req, result):
    """运营商电话记录"""

    try:
        result = json.loads(result)
    except Exception as e:
        project_logger.info('[OPERATOR][RESULT|%s][ERROR|%s]', result, str(e))
        return [], 0
    page = req["page"]
    count = req["count"]
    callRecordsInfo = [
        {"belongArea": i.get("belongArea", ""),
        "callTimes": i.get("callTimes", 0),
        "calledTimes": i.get("calledTimes", 0),
        "connTime": i.get("connTime", 0),
        "connTimes": i.get("connTimes", 0),
        "identifyInfo": i.get("identifyInfo", ""),
        "phoneNo": i.get("phoneNo", "")
        } for i in result.get("callRecordsInfo", [])
        if i.get("identifyInfo", "") or i.get("connTimes", 0) > 1
    ]
    response = change_sort(callRecordsInfo, sort_key="connTimes")
    if req["isMark"] == 1:
        response = [i for i in response if i.get("identifyInfo", "")]
    resp = response[(page-1)*count : page*count]
    dict_list_util(resp)
    return resp, len(response)


def contact_area_list(req, result):
    """联系人区域分析"""

    try:
        result = json.loads(result)
    except Exception as e:
        project_logger.info('[OPERATOR][RESULT|%s][ERROR|%s]', result, str(e))
        return [], 0

    page = req["page"]
    count = req["count"]
    contactAreaInfo = result.get("contactAreaInfo", [])
    def _float(data):
        try:
            return str(round(float(data) * 100, 4)) + "%"
        except ValueError:
            return ""

    from app.capcha_report.util import UserExceptionAction
    UserExceptionAction.contract_record(result, req[''])


def handle_cellphone(response):
    """process channel cellphone"""

    _map = {
        1: 4,
        -1: 2,
        3: 2,
        2: 3,
        '1': 4,
        '-1': 2,
        '3': 2,
        '2': 3
    }
    _map2 = {'mobile': '移动', 'unicom': '联通', 'telecom': '电信'}

    if response:
        if response.get('code') == const.CODE:
            res_code = response.get('data', {}).get('res_code', 2)
            is_phone = _map.get(res_code, 2)
            operator = response.get('data', {}).get('res_operator', '')
            return {'isPhone': is_phone, 'operator': _map2.get(operator, '')}

    return {'isPhone': 1, 'operator': ''}



def time_strf(d):
    if isinstance(d, datetime.datetime):
        return d.strftime("%Y-%m-%d")
    if isinstance(d, int):
        timeArray = time.localtime(d)
        otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
        return otherStyleTime
    return d


def handle_undesirable_info(d):
    """ 公安不良信息 """
    is_target = 3

    # 第一种数据形式
    type_1, ret = {}, []
    if 'data' not in d:
        if 'case' in d:
            type_1['time'] = time_strf(d['case'])
        if 'result' in d:
            type_1['type'] = d['result']

        if 'time' in d:
            type_1['time'] = time_strf(d.get("time", ''))
        if 'type' in d:
            type_1['type'] = d.get("type") or ''
        if type_1.get("type"):
            is_target = 2
        return {
            'isTarget': is_target,
            'targetList': [type_1]
        }
    else:
        result_l = d.get('data', {})
        for i in result_l:
            ret.append({"type": i.get("type", ''), "time": i.get("time", ''), "detail": i.get("source", '')})
        if ret:
            is_target = 2
        return {
            'isTarget': is_target,
            'targetList': ret
        }


def user_contact_info_handle(d):
    """ 用户关联信息校验 """
    ret = {
        "idcardName": d.get("idcard_name", 1),    # 身份证关联姓名
        "idcardPhone": d.get("idcard_phone", 1),  # 身份证关联手机
        "phoneIdcard": d.get("phone_idcard", 1),  # 手机关联身份证
        "phoneName": d.get("phone_name", 1),      # 手机管理姓名
    }
    return ret


def user_queryed_info_handle(d):
    """ 用户个人信息被查询 """
    card = d.get("idcard_record", {"one_month": 1, "three_month": 1, 'six_month': 1, "one_year":1})
    phone = d.get("phone_record", {"one_month": 1, "three_month": 1, 'six_month': 1, "one_year":1})
    ret = {
        "idcard": {"oneMonth": card["one_month"], "threeMonth": card['three_month'],
                   "sixMonth": card['six_month'], "oneYear": card["one_year"]},
        "phone": {"oneMonth": phone["one_month"], "threeMonth": phone['three_month'],
                   "sixMonth": phone['six_month'], "oneYear": phone["one_year"]}
    }
    return  ret


def handle_import_contact(session, data, input_id):

    flag = True if data else False
    data = data.get('callback_operator', {}).get("data", {})
    # data = data.get('data', '')
    with session_scope(session) as sess:
        input_obj = sess.query(InputApply).filter_by(id=int(input_id)).first()
        rel, work, school = None, None, None
        last, ret = [], []
        if input_obj.home_mem_phone:
            rel = {
                'relation': input_obj.home_mem_relation or '',
                'phone': input_obj.home_mem_phone or '',
                "name": input_obj.home_mem_name or '',
                'type': '家庭联系人'
            }
            last.append(rel)
        if input_obj.work_contact_phone:
            work = {
                'relation': '同事',
                'phone': input_obj.work_contact_phone or '',
                'name': input_obj.work_contact_name or '',
                'type': '工作单位联系人'
            }
            last.append(work)
        if input_obj.school_contact_phone:
            school = {

                'relation': input_obj.school_contact_relation,
                'phone': input_obj.school_contact_phone,
                'name': input_obj.school_contact or '',
                'type': '学校联系人'
            }
            last.append(school)

        def count_handle(phone_n, data):
            """ 获取在某个电话的通话次数 """
            sum_, is_true = 0, 0

            for i in data:
                sum_ += 1
                if phone_n == i.get("peer_number", ""):
                    is_true += 1
            return sum_, is_true

        def intimacy_handle(d):
            if d == 0:
                return 0

            if 1 < d < 5:
                return 1
            if d < 100:
                return 2
            return 3

        def map_f(rele):
            nonlocal ret
            # one_month
            _, one_month = count_handle(rele.get('phone'), data.get("deceitRisk", {}).get("monthCallInfo", {}).get(
                "oneMonth", {}).get("callList", []) )
            # three month
            _, three_month = count_handle(rele.get('phone'), data.get("deceitRisk", {}).get("monthCallInfo", {}).get(
                "threeMonth", {}).get("callList", []))
            ret.append({
                "intimacy": intimacy_handle(three_month / 3.0),
                "name": rele.get('name', ''),
                "oneMonthTel": one_month,
                "relation": rele.get("relation", ""),
                "telphone": rele.get("phone", ""),
                "threeMonthTel": three_month,
                "type": rele.get("type")
            })
        list(map(map_f, last))
        if len(ret) == 0:
            return [{
                "intimacy": '',
                "name": '',
                "oneMonthTel": '',
                "relation": '',
                "telephone": '',
                "threeMonthTel": '',
                "type": ''
            }]
        else:
            if flag is False:
                l = []
                for ele in ret:
                    ele.update({'intimacy': '-', 'oneMonthTel': '-', 'threeMonthTel': '-'})
                    l.append(ele)
            else:
                l = ret
            return l


def handle_netloan_platforms(d):
    """ 网贷逾期多平台 """
    is_target = 3
    l = [{
        'overdueDay': i['overdue_days'],
        'overdueNum': i['debt_num'],
        'overdueTime': i['overdue_time'],
        'oweMoney': i['debt_amt'],
        'updateTime': i['update_time']
         } for i in d.get("data", [])]
    if l:
        is_target = 2
    return {
        'isTarget': is_target,
        'targetList': l
    }


def handle_netloan_risk(d):
    """ 网贷逾期风险校验 """
    if not d:
        d = {}
    is_target = 3
    l = [{'moneyRegion': i['amount_range'], 'riskType': i['risk_kind'],
          'tradeTime': i['trade_time']} for i in d.get("data", [])]
    if l:
        is_target = 2
    return {
        'isTarget': is_target,
        'targetList': l
    }


def blacklist_check_handle(d):
    i_target = 3
    if not d:
        d = {}
    if d.get("data"):
        i_target = 2
    return {
        "isTarget": i_target,
        "targetList": [{'isTarget': i['status'], 'targetContent': i['result']} for i in d.get("data", [])]
    }


def handle_obtain_riskinfocheck(d):
    """不良信息查询W1"""

    default = {'isTarget': 3, 'targetList': []}

    data = d.get('data', {}) or {}
    if not data:
        return default

    detail = data.get('detail', {}) or {}
    if not detail:
        return default

    checkDetail = detail.get('checkDetail', {}) or {}
    if not checkDetail:
        return default

    caseSource = checkDetail.get('caseSource', '') or ''
    caseTime = checkDetail.get('caseTime', '') or ''

    def __process_casetime(i):
        if 'null' in i:
            return '--'

        _map = {
            "[0,0.25)/": "3个月以内",
            "[0.25,0.5)/": "3个月-6个月以内",
            "[0.5,1)/": "6个月-1年以内",
            "[1,2)/": "1年-2年以内",
            "[2,5)/": "2年-5年以内",
            "[5,10)/": "5年-10年以内",
            "[10,15)/": "10年-15年以内",
            "[15,20)/": "15年-20年以内",
        }

        return _map.get(i, "--")

    caseTime = __process_casetime(caseTime)

    if not caseSource and not caseTime:
        return default

    return {
        'isTarget': 2,
        'targetList': [{'time': caseTime, 'detail': caseSource}]
    }


def handle_operator_phonetime(d):
    """手机在网时长W1"""

    data = d.get('data', {}) or {}

    if not data:
        return {
            "operator": "",
            "phoneStatus": -1,
            "timeRange": "--",
        }

    def t_handle(d):
        if d == 0:
            return "0-6个月"
        elif d == 1:
            return "6-12个月"
        elif d == 2:
            return "12-24个月"
        elif d == 3:
            return "24个月以上"
        else:
            return "--"

    return {
        'operator': data.get('operator', ''),
        'phoneStatus': -1,
        'timeRange': t_handle(data.get('resCode', '')),
    }


def handle_operator_multiplatform(response):
    """多平借贷W1"""

    default = "在网贷平台有注册登录行为"
    if response:
        if response.get("code") == const.CODE:
            plat_num = response.get("data").get("plat_num")
            target_list = []
            plat_list = response.get("data").get("plat_list")
            if plat_list:
                for i in plat_list:
                    if i.get("flag") == 1:
                        target_list.append(i.get("platfrom"))
            return {'isTarget': 1 if plat_num else 0, 'loanNum': plat_num, 'targetList': target_list, "name": default}
    return {'isTarget': 0, 'loanNum': 0, 'targetList': [], "name": ""}


def handle_overdue_b(response):

    if response and response.get("code") == const.CODE:
        result = [i for i in response.get("data").get("RESULTS", []) or [] if i.get("TYPE") in ["EMR012", "EMR013"]]

        def _process(r):
            data = r.get("DATA", []) or []

            return [{"overdueNum": i.get("COUNTS", "--"), "overdueTime": r.get("CYCLE", "--"), "oweMoney": i.get(
                "MONEY", "--")} for
                    i in
                    data]

        target_list = [_process(i) for i in result]
        target_list = [j for i in target_list for j in i]

        return {"isTarget": int(bool(target_list)), "targetList": target_list}

    return {"isTarget": 0, "targetList": []}


def handle_multiple_loan_apply_a(response):

    if response and response.get("code") == const.CODE:
        result = [i for i in response.get("data").get("RESULTS", []) or [] if i.get("TYPE") in ["EMR004"]]

        def _process(r):
            data = r.get("DATA", []) or []

            _dict = {
                "1": "银行",
                "2": "非银行",
            }

            def _loan_money(m):
                return m.strip() or "--"

            def _apply_time(t):
                try:
                    return datetime.datetime.strptime(t, "%Y/%m/%d %H:%M:%S").strftime("%Y-%m-**")
                except:
                    return "--"

            return [{"applyTime": _apply_time(i.get("APPLICATIONTIME", "--")), "applyMoney": i.get("APPLICATIONAMOUNT",
                                                                                              "--"),
                     "loanMoney": _loan_money(i.get("APPLICATIONRESULT", "--")), "applyType": _dict.get(i.get(
                    "P_TYPE"), "--")} for i in data]

        target_list = [_process(i) for i in result]
        target_list = [j for i in target_list for j in i]

        return {"isTarget": int(bool(target_list)), "targetList": target_list}

    return {"isTarget": 0, "targetList": []}


def handle_multiple_loan_register_b(response):

    if response and response.get("code") == const.CODE:
        result = [i for i in response.get("data").get("RESULTS", []) or [] if i.get("TYPE") in ["EMR002"]]

        bank_num = 0
        anti_bank_num = 0

        for r in result:
            data = r.get("DATA", []) or []

            for i in data:
                if i.get("P_TYPE") == "1":
                    bank_num += 1
                elif i.get("P_TYPE") == "2":
                    anti_bank_num += 1

        target_list = [
            {"platformNum": bank_num if bank_num else "--", "behavior": "在银行类平台有注册登录行为", "type": "银行类"},
            {"platformNum": anti_bank_num if anti_bank_num else "--", "behavior": "在网贷平台有注册登录行为", "type": "非银行类"}
        ]

        return {"isTarget": int(bool(sum((bank_num, anti_bank_num)))), "targetList": target_list}

    return {"isTarget": 0, "targetList": []}


def handle_multiple_loan_apply_b(response):

    if response and response.get("code") == const.CODE:

        def _process(r):

            _order = [
                "房地产金融",
                "一般消费分期平台",
                "互联网金融门户",
                "银行消费金融公司",
                "信用卡中心",
                "小额贷款公司",
                "第三方服务商",
                "P2P网贷",
                "大型消费金融公司",
            ]

            order = {key: i for i, key in enumerate(_order)}

            detail = r.get("item_detail", {}).get("platform_detail", [])
            pattern1 = re.compile("(\d)个月")
            pattern2 = re.compile("(\d)天")
            r1 = pattern1.match(r.get("item_name", ""))
            r2 = pattern2.match(r.get("item_name", ""))
            if r1:
                time_string = "近{0}个月".format(r1.groups()[0])
                time_num = int(r1.groups()[0]) * 30
            elif r2:
                time_string = "近{0}天".format(r2.groups()[0])
                time_num = int(r2.groups()[0])

            else:
                return

            res = {"itemList": []}

            def _dict(d):

                name, num = d.split(":")
                res["itemList"].append({
                    "name": name,
                    "count": int(num),
                })

            [_dict(i) for i in detail]
            res["itemList"].sort(key=lambda d: order.get(d['name'], 1000))
            res.update({"total": sum([i["count"] for i in res["itemList"]]), "timeNum": time_num, "time": time_string})

            return res

        result = [_process(i) for i in response.get("data").get("risk_items") if i.get("group") in ["多平台借贷申请检测"]]
        result = [i for i in result if i]
        result.sort(key=lambda x: x["timeNum"])

        return {"isTarget": int(bool(result)), "targetList": result}

    return {"isTarget": 0, "targetList": []}


def handle_overdue_c(response):

    if response and response.get("code") == const.CODE:

        risk_items = response.get("data").get("risk_items")

        def _process(t):

            if isinstance(t, dict):

                return {
                    "oweMoney": t.get("overdue_amount", "--"),
                    "overdueDay": t.get("overdue_day", "--"),
                    "overdueTime": "--",
                    "overdueNum": t.get("overdue_count", "--"),
                }

        result = [_process(j) for i in risk_items for j in i.get("item_detail", {}).get("overdue_details", []) if isinstance(i, dict)]

        return {"isTarget": int(bool(result)), "targetList": result}

    return {"isTarget": 0, "targetList": []}


def handle_financial_bad(response):

    def _process(item_name):
        """去掉内容中的敏感词汇"""
        if not item_name:
            return

        p = re.compile("^(.*)晟盾(.*)$")
        m = p.match(item_name)
        if m:
            return "".join(m.groups())
        else:
            return item_name

    if response and response.get("code") == const.CODE:

        result = [{"group": i.get("group"), "itemName": _process(i.get("item_name")), "level": i.get("risk_level")} for i in
                  response.get("data").get("risk_items") if i.get("group") in ["不良信息扫描", "客户行为检测"]]
        return {"isTarget": int(bool(result)), "targetList": result}

    return {"isTarget": 0, "targetList": []}


def handle_obtain_piccompare(response):

    if response and response.get("code") == const.CODE:
        result = response.get("data").get("similarity")
        if result:
            try:
                score = str(result[0] / 100.0)
                return {"faceScore": score}
            except:
                import traceback
                traceback.print_exc()

    return {"faceScore": ""}
