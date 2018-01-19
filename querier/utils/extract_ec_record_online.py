# coding:utf-8

import time
import datetime as dt
from datetime import datetime

from .extract_dir import cat_map
from .data import (get_online_records_by_tid, gen_dec_refers_by_kv,
                   basic_tag, get_online_tags_by_tid)
from .handler import get_tbid_from_nick


def chg_date(datestr):
    """将日期改为7天以前,只取yymm"""
    a = datestr
    timeArray = datetime.strptime(a, "%Y%m%d")
    timeStamp = int(time.mktime(timeArray.timetuple()))
    dateArray = datetime.utcfromtimestamp(timeStamp)
    sevenDayAgo = dateArray - dt.timedelta(days=7)
    res = sevenDayAgo.strftime("%Y-%m-%d")
    return res[:4] + res[5:7]


def extract_online_records_by_kv(k, v, company=None):
    """
    征信接口调用
    参数 k:"tel" ,v:一个手机号
    返回数据:
    json: tel(未加密), 商品id, 购买时间, 商品title, 品牌, 价格, 发货地.
    """
    refers = gen_dec_refers_by_kv(k, v)
    if not company:
        if len(refers) == 0:
            refers = get_tbid_from_nick(v)
    if len(refers) == 0:
        return None

    res = []
    for refer in refers:
        wlid, k2, tb, k4 = refer[:4]
        records = get_online_records_by_tid(tb)

        for j in records:
            item_info = {
                "tel": v,
                "item_id": j["item_id"],
                "purchase_time": chg_date(j["date"]),
                "item_title": j["title"],
                "item_brand": j["brand"],
                "price": j["price"],
                "seller_location": j["seller_loc"],
                "category_name": cat_map.get(j['root_cat_id'], '-')
            }
            res.append(item_info)
    return res


def user_tag_record(table, telno):
    """数据集市用户画像接口(金融用户画像)"""

    #通过手机号查询到邮箱和用户的电商信息id
    refers = gen_dec_refers_by_kv(table, telno)
    if len(refers) == 0:
        refers = get_tbid_from_nick(telno)
    res = []
    basic_list = []
    if refers:
        m_ref_cnt = len(refers)
        for refer in refers:
            wlid, k2, tb, k4 = refer[:4]

            records = get_online_records_by_tid(tb)
            base_data = basic_tag(tb, telno)
            if base_data:
                basic_list.append(base_data)

            for j in records:
                item_info = {
                    "cat_id": j["cat_id"],
                    "brand": u'其他' if j["brand"] == "-" else j['brand'].decode("utf-8").split("/", 1)[-1],
                    "price": j["price"],
                    "root_cat_id": j['root_cat_id'],
                    "bc_type": j.get("bc_type", ""),
                    "purchase_time": chg_date(j["date"]),
                }
                res.append(item_info)
        if basic_list:
            basic = max(basic_list, key=lambda x: x["sum"])
            basic.pop("sum")
        else:
            basic = None
        return res, basic, m_ref_cnt
    return None, None, 0


def cal_all_perform_data(org_tags):

    level = int(org_tags["info:L"]) - 1
    usertags = org_tags["info:user"]
    usertags = sorted(map(lambda x: [x.split("_")[0], float(x.split("_")[1])], usertags.strip().split("|")), cmp=lambda x, y: cmp(x[1], y[1]), reverse=True) if usertags != "" else []
    usertags = map(lambda x: x[0], usertags)
    if "需细分" in usertags:
        usertags.remove("需细分")
    if "待产" in usertags:
        usertags.remove("待产")
    if "细分" in usertags:
        usertags.remove("细分")
    tftags = org_tags["info:tf"]
    wordcloud = map(lambda x: {"name": x.split("_")[0], "value": round(float(x.strip().split("_")[1]) * 100, 2)}, tftags.strip().split("|")) if tftags != "" else []
    return {
        "consumerlevel": level,
        "tags": usertags[:5],
        "wordcloud": wordcloud
    }


def tel_tag_record(table, telno):
    """电商标签调用提供给用户画像使用"""

    #通过手机号查询到邮箱和用户的电商信息id
    refers = gen_dec_refers_by_kv(table, telno)
    if len(refers) == 0:
        refers = get_tbid_from_nick(telno)
    res = []
    if refers:
        for refer in refers:
            wlid, k2, tb, k4 = refer[:4]
            org_tags = get_online_tags_by_tid(tb)
            res.append(cal_all_perform_data(org_tags))
        return res
    return None
