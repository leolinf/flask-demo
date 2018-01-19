# -*- coding: utf-8 -*-

import requests
import time
import operator
from itertools import groupby

from app.constants import CreditUri, TelPrice
from app.config import Config
from app.core.logger import project_logger
from app.core.functions import querystring, time_change
from app.core.aes import AESHelper


def request(url):
    """处理请求"""
    try:
        resp = requests.get(url, timeout=Config.TIMEOUT)
        return resp.json()
    except requests.exceptions.Timeout:
        return None
    except Exception:
        return None


def tel_list(*args):
    """电商消费记录"""
    enc = AESHelper(Config.SECRET)
    url = querystring(CreditUri.TELURL_BASICS, {"enc_m": enc.encrypt(args[0])})
    start_time = time.time()
    response = request(url)
    project_logger.info("[GET][TEL_LIST][DAIZHONG][RESPONSE|%s][TIME|%s][REQUEST|%s]", response, time.time()-start_time, args)
    if response:
        if response.get("code") == TelPrice.CODE:
            info_list = response.get("data").get("info_list")
            if info_list:
                tels = []
                tel_list = sorted(info_list, key=operator.itemgetter("purchase_time"))
                for k, v in groupby(tel_list, operator.itemgetter("purchase_time")):
                    data = list(v)
                    tels.append({"timestamp": time_change(k), "dealNum": len(data),
                                "buyNum": round(sum(float(i.get("price")) for i in data), 2)})
                return tels
    return []


def sync_search(*args):
    """综合反欺诈接口数据"""
    params = {"enc_m": args[0]}
    if args[1]:
        params.update({"iname": args[1]})
    if args[2]:
        params.update({"cardNum": args[2]})
    url = querystring(CreditUri.SYNTHESIS, params)
    start_time = time.time()
    response = request(url)
    project_logger.info("[GET][SYNTHESIS][DAIZHONG][RESPONSE|%s][TIME|%s][REQUEST|%s]", response, time.time()-start_time, args)
    if response:
        if response.get("code") == TelPrice.CODE and response.get("data"):
            break_num = 0
            data = response.get("data").get("info_list")
            # 电商黑名单
            eBusinessDanger = data.get("elec_info").get("elec_data")
            _eBusinessDanger = {"isTarget": 0, "targetNum": 0, "targetList": []}
            if eBusinessDanger:
                elec_info = [{
                    "title": i.get("title"),
                    "orderTime": time_change(i.get("buytime")),
                    "keyword": i.get("keywords")} for i in eBusinessDanger]
                _eBusinessDanger = {"isTarget": 1, "targetNum": len(elec_info),
                                    "targetList": elec_info}
                break_num += 1
            # 信息平台清单
            infoDanger = data.get("message_info").get("info_data")
            _infoDanger = {"isTarget": 0, "targetNum": 0, "targetList": []}
            if infoDanger:
                info_data = [{
                    "content": i.get("title"),
                    "keyword": i.get("keywords")} for i in infoDanger]
                _infoDanger= {"isTarget": 1, "targetNum": len(info_data),
                                    "targetList": info_data}
                break_num += 1
            # 网贷预期黑名单
            anOverBlack = data.get("inter_info").get("inter_data")
            _anOverBlack = {"isTarget":
                -1 if data.get("inter_info").get("inter_overdue") == 0 else 0,
                "targetList": []
            }
            if anOverBlack:
                inter_data = [{"loanTime": time_change(i["borrow_date"]),
                         "loanStage": i["borrow_nper"],
                         "loanMoney": i["time_out_interest"],
                         "overDay": i["time_out_days"]} for i in anOverBlack]
                _anOverBlack = {"isTarget": 1, "targetList": inter_data}
                break_num += 1
            # 多平台借贷
            multipleLoan = data.get("multi_borrow").get("plat_list")
            _multipleLoan= {"isTarget": 0, "targetList": [],
                            "loanNum": 0}
            if multipleLoan:
                loanNum = data.get("multi_borrow").get("plat_num")
                target_list = []
                for i in data.get("multi_borrow").get("plat_list"):
                    if i.get("flag") == 1:
                        target_list.append({"name": i.get("platfrom")})
                _multipleLoan = {"isTarget": 1 if target_list else 0, "targetList": target_list,
                                 "loanNum": loanNum}
                if target_list:
                    break_num += 1
            # 失信人名单
            noFaithList = data.get("faith_info").get("faith_data")
            _noFaithList = {"isTarget":
                -1 if data.get("faith_info").get("faith_overdue") == 0 else 0,
                "targetList": []
            }
            if noFaithList:
                faith_info  = [{"court": i["courtName"],
                        "performance": i["performance"],
                        "detailAction": i['duty'],
                        "registerTime": i["regDate"],
                        "registerNum": i["caseCode"]}for i in noFaithList]
                _noFaithList = {"isTarget": 1, "targetList": faith_info}
                break_num += 1
            # 手机标注黑名单
            phoneMarkBlackList = data.get("phone_black").get("phone_data")
            _phoneMarkBlackList = {"isTarget": 0, "targetList": []}
            if phoneMarkBlackList:
                phone_list = []
                cache = False
                for i in phoneMarkBlackList:
                    tag = i.get("tag")
                    amount = i.get("amount")
                    if tag:
                        phone_list.append({"markNum": amount, "markType": tag})
                        if u'公司' not in tag and amount:
                            cache = True
                if cache:
                    break_num += 1
                _phoneMarkBlackList = {"isTarget": 1 if cache else 0,
                                       "targetList": phone_list}
            # 手机活跃度综合
            _phoneRelative = data.get("device_info").get("device_data")
            if _phoneRelative:
                _phoneRelative.pop("phone")
                cache = -1 if all([v < 3 for v in _phoneRelative.values()]) else 1
                _phoneRelative["isTarget"] = cache
                if cache == 1:
                    break_num += 1
            else:
                _phoneRelative = {"isTarget": 0}
            # 社交平台黑名单
            socialDanger = data.get("social_info").get("social_data")
            _socialDanger = {"isTarget": 0, "targetList": [],
                             "attentionList": [], "targetNum": 0}
            if socialDanger:
                social_info = []
                for i in socialDanger:
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
                attentionList = '|'.join([i.get("finance_weibonames") for i in socialDanger if i.get("finance_weibonames")])
                _attentionList = [{"name": i} for i in set(attentionList.split("|")) if i]
                social_list = []
                for social in social_info:
                    if any(social.values()):
                        social_list.append(social)
                hit = len(social_list)
                _socialDanger = {"isTarget": 1 if social_list else 0, "targetList": social_list,
                                 "attentionList": _attentionList, "targetNum": hit}
                if social_list:
                    break_num += 1
            return {"eBusinessDanger": _eBusinessDanger,
                    "infoDanger": _infoDanger,
                    "loanOverTimeBlackList": _anOverBlack,
                    "multipleLoan": _multipleLoan,
                    "noFaithList": _noFaithList,
                    "phoneMarkBlackList": _phoneMarkBlackList,
                    "phoneRelative": _phoneRelative,
                    "socialDanger": _socialDanger,
                    "break_num": break_num}
    break_num = 0
    _eBusinessDanger = {"isTarget": 0, "targetNum": 0, "targetList": []}
    _infoDanger = {"isTarget": 0, "targetNum": 0, "targetList": []}
    _multipleLoan= {"isTarget": 0, "targetList": [], "loanNum": 0}
    _phoneMarkBlackList = {"isTarget": 0, "targetList": []}
    _phoneRelative = {"isTarget": 0}
    _socialDanger = {"isTarget": 0, "targetList": [], "attentionList": [], "targetNum": 0}
    if len(params) > 1:
        _anOverBlack = {"isTarget": 0, "targetList": []}
        _noFaithList = {"isTarget": 0, "targetList": []}
    else:
        _anOverBlack = {"isTarget": -1, "targetList": []}
        _noFaithList = {"isTarget": -1, "targetList": []}
    return {"eBusinessDanger": _eBusinessDanger,
            "infoDanger": _infoDanger,
            "loanOverTimeBlackList": _anOverBlack,
            "multipleLoan": _multipleLoan,
            "noFaithList": _noFaithList,
            "phoneMarkBlackList": _phoneMarkBlackList,
            "phoneRelative": _phoneRelative,
            "socialDanger": _socialDanger,
            "break_num": break_num}
