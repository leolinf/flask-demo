# -*- coding: utf-8 -*-

import time
from dateutil import parser
from datetime import datetime

from weibo_key import weibo_keywords
from utils.data import gen_dec_refers_by_kv
from utils.auth import (
    weibo_user_info, weibo_user_tag,
    weibo_edu, weibo_user_career,
    weibo_basic_info, weibo_age_sex
)

def time_change(data):
    """处理时间"""
    if data == '-' or data == '\\N' or data == '':
        return -1
    return time.mktime(datetime.strptime(str(data), "%Y%m").timetuple()) * 1000

def mktime_change(data):
    """处理出生日期时间"""
    if data == '-' or data == '\\N' or data == '':
        return -1
    try:
        mktime_time = time.mktime(datetime.strptime(str(data), "%Y-%m-%d").timetuple()) * 1000
    except ValueError:
        return -1
    return mktime_time

def change_reg_time(data):
    """处理注册时间"""

    if data == '-' or data == '\\N' or data == '':
        return -1
    return time.mktime(parser.parse(str(data)).timetuple()) * 1000

def change_career_time(data):
    """处理工作开始时间和结束时间"""

    if data == '-' or data == '\\N' or data == '' or data == 0 or data == 9999:
        return -1
    return time.mktime(datetime.strptime(str(data), "%Y").timetuple()) * 1000


def dict_list_util(ret):
    """字典和列表有空数据全部改成×××"""

    if isinstance(ret, list):
        for i in ret:
            dict_list_util(i)

    if isinstance(ret, dict):
        for k, v in ret.items():
            if v == '-' or v == '\\N' or v == ' ':
                ret[k] = ''
            if isinstance(ret[k], dict):
                dict_list_util(ret[k])
            if isinstance(ret[k], list):
                dict_list_util(ret[k])


def consume_info_util(consume_infos):
    """处理电商标签"""
    info_list = {}
    consume_tag = []
    if consume_infos:
        for i in [j for i in consume_infos for j in i.get("tags")]:
            consume_tag.append(i)
    info_list["population_label"] = consume_tag
    return info_list


def consume_list_util(consume_list):
    """处理电商消费列表"""

    if not consume_list:
        return []
    def _fun(v):
        if v == '-' or v == '\\N' or v == '':
            return 0
        try:
            return float(v)
        except ValueError:
            return 0

    return [{"purchase_time": time_change(i.get("purchase_time")),
             "category_name": i.get("category_name"),
             "brand_name": i.get("item_brand"), "price": _fun(i.get("price")),
             "item_id": i.get("item_id"), "title": i.get("item_title")} for i in consume_list]


def get_age(gender_age):
    if not gender_age:
        return ""
    data = gender_age.get("birthyear")
    try:
        return str(datetime.now().year - int(data)) + u'年'
    except:
        return ""


def get_sex(gender_age):
    if not gender_age:
        return ""
    data = gender_age.get("gender")
    try:
        return "m" if data == "0" else "f"
    except:
        return ""


def base_info(phone):
    """处理微博基本信息"""
    gender_age = weibo_age_sex(phone)
    refers = gen_dec_refers_by_kv('tel', str(phone))
    if not refers:
        if gender_age:
            return {"base_info": {"gender": get_sex(gender_age), "birthday": get_age(gender_age), "img": ""},
                    "weibo_info": {}, "work_info": [], "education_info": []}
        return {"base_info": {}, "weibo_info": {},
                "work_info": [], "education_info": []}
    weibo_id = set([i[-1] for i in refers])
    for wid in weibo_id:
        if wid == "None":
            if gender_age:
                return {"base_info": {"gender": get_sex(gender_age), "birthday": get_age(gender_age), "img": ""},
                        "weibo_info": {}, "work_info": [], "education_info": []}
            return {"base_info": {}, "weibo_info": {},
                    "work_info": [], "education_info": []}
        info = weibo_user_info(int(wid))
        tag = weibo_user_tag(int(wid))
        career_info = weibo_user_career(int(wid))
        edu_info = weibo_edu(int(wid))
        basic_info = weibo_basic_info(int(wid))
        if info:
            ## 基础信息处理
            base_info = {}
            base_info["gender"] = get_sex(gender_age)
            if basic_info:
                base_info["birthday"] = get_age(gender_age)
                base_info["img"] = info.get("avatar_large")
            else:
                base_info["birthday"] = ""
            weibo_info = {}
            weibo_info["registration_time"] = change_reg_time(info.get("created_at"))
            weibo_info["nick_name"] = info.get("screen_name")
            weibo_info["friends_amount"]= info.get("bi_followers_count")
            weibo_info["fans_amount"] = info.get("friends_count")
            weibo_info["follow_amount"] = info.get("followers_count")
            weibo_info["weibo_amount"] = info.get("statuses_count")
            weibo_info["keywords"] = weibo_keywords(wid)
            if tag:
                ## 标签处理
                weibo_info["personal_label"] = tag.get("tag") if tag.get("tag") else []
            else:
                weibo_info["personal_label"] = []
        else:
            if gender_age:
                base_info = {"gender": get_sex(gender_age), "birthday": get_age(gender_age), "img": ""}
            else:
                base_info = {}
            weibo_info = {}
        ## 工作信息处理
        if career_info:
            work_info = [{"company": i.get("company"),
                          "end": change_career_time(i.get("end", -1)),
                          "start": change_career_time(i.get("start", -1)),
                          "departmend": i.get("department")} for i in career_info.get("career")]
        else:
            work_info = []
        # 教育信息处理
        if edu_info:
            education_info = [{"school": i.get("school"), "major": i.get("department"),
                               "education": i.get("type") if i.get("type") else -1,
                               "admission_time": i.get("year") if i.get("year") else -1} for i in edu_info.get("education")]
        else:
            education_info = []
        return {"base_info": base_info, "weibo_info": weibo_info,
                "work_info": work_info, "education_info": education_info}
