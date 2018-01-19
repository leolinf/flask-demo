# coding:utf-8

import json
import happybase
from time import time

from settings import (
    refer_aes_key, mongo_refer_table, record_table,
    basic_table, tags_table, weibo_fri, thrift_server_down,
    portrait_v2, mongo_refer_nick
)

from .aeshelper import AESHelper as aes
from .session import db, hbase_pool
from framework.logger import project_logger

def init_env():
    conn = happybase.Connection(host=thrift_server_down, port=9087)
    return conn


# 根据k-v查询返回refers
def gen_dec_refers_by_kv(key, value):
    start_time = time()
    refers_limit = 4

    a = aes(refer_aes_key)
    enc_value = a.encrypt(value)
    # 设置limit 防止库中异常匹配超大返回
    users = db[mongo_refer_table].find({key: enc_value}).limit(refers_limit)

    referls = []
    for user in users:
        wlid = str(user["_id"])
        referls.append([
            wlid[0:8] + wlid[14:],
            a.decrypt(user["tel"]),
            a.decrypt(user["TB"]),
            a.decrypt(user["QQ"]),
            a.decrypt(user["email"]),
            a.decrypt(user["QQWB"]),
            a.decrypt(user["snwb"])
        ])

    project_logger.info("[GET|MONGODB][TIME:%s]", time()-start_time)
    return referls

def gen_tbid_nick(nick):
    """查询优啦结合数据库的数据"""

    start_time = time()
    refers_limit = 1
    # 设置limit 防止库中异常匹配超大返回
    users = db[mongo_refer_nick].find({"nick": nick}).limit(refers_limit)
    referls = []
    for user in users:
        referls.append([
            '',
            '',
            str(user.get("id","") or ""),
            '',
            '',
            '',
            ''
        ])

    project_logger.info("[GET|MONGODB][TIME:%s][REFERLS|%s]", time()-start_time, referls)
    return referls


# 构造record数据统一返回接口
# return [record(json),...]
def get_online_records_by_tid(tid):
    # 设置返回限制 防止过大数据返回
    start_time = time()
    record_limit = 500
    def gen_record_obj(record):
        '''
        {
            "info:item": "item_id|seller_loc|title|sku",
            "info:v": "date|cat_id|root_cat_id|brand|price|bc_type"
        }
        '''
        infols = record["info:item"].split("|")
        vls = record["info:v"].split("|")
        return {
            "item_id": infols[0],
            "seller_loc": infols[1],
            "title": infols[2],
            "sku": infols[3],
            "date": vls[0],
            "cat_id": vls[1],
            "root_cat_id": vls[2],
            "brand": vls[3],
            "price": vls[4],
            "bc_type": vls[5]
        }
    org_data = []
    try:
        with hbase_pool.connection() as conn:
            table_record = conn.table(record_table)
            start = tid + '_'
            for k, v in table_record.scan(row_prefix=start, limit=record_limit):
                org_data.append(gen_record_obj(v))
        project_logger.info("[GET|TEL][TIME:%s]", time()-start_time)
        return org_data
    except Exception as e:
        project_logger.info("[GET][TEL][error_message|%s]", e)
        return org_data


def basic_tag(taobaoid, telno):
    """user basic_tag find"""
    start_time = time()
    try:
        with hbase_pool.connection() as conn:
            _basic_tag = conn.table(basic_table)
            data = _basic_tag.row(taobaoid)
    except Exception as e:
        project_logger.info("[GET][BASE_TAG][error_message|%s]", e)
        return {}
    project_logger.info("[GET|BASE_TAG][TIME:%s]", time()-start_time)
    if not data:
        return {}
    def cnt(num):
        try:
            raw = int(num) / 200
        except ValueError:
            return '0-200'
        return str(raw * 200) +"-"+ str((raw +1)* 200)
    def _fun(age):
        try:
            if int(age) > 16 and int(age) < 60:
                return age
            elif int(age) < 16:
                return "<16"
            elif int(age) > 60:
                return ">60"
            else:
                return ""
        except ValueError:
            return ""

    return {
        "enc_m": telno,
        "basic_city": data.get("info:city").decode("utf-8"),
        "basic_gender": u'女' if data.get("info:gender") else u'男',
        "basic_age": _fun(data.get("info:age")),
        "sum": int(data.get("info:sum")),
        "consume_auth": data.get("info:auth"),
        "consume_VIP": data.get("info:v_level"),
        "consume_sumlevel": data.get("info:sum_level"),
        "consume_year": str(int(float(data.get("info:year")))) if data.get("info:year") else '',
        "consume_act": data.get("info:ac_score"),
        "consume_count": cnt(data.get("info:cnt")),
        "favor_feedrate": data.get("info:f_rate") + '%' if data.get("info:f_rate") else ""
    }


def get_online_tags_by_tid(tid):

    start_time = time()
    try:
        with hbase_pool.connection() as conn:
            table_tags = conn.table(tags_table)
            org_tags = table_tags.row(tid)
            if org_tags == {}:
                org_tags = {"info:L": "1", "info:tf": "", "info:user": ""}
        project_logger.info("[GET|TEL_TAG][TIME:%s]", time()-start_time)
        return org_tags
    except Exception as e:
        project_logger.info("[GET][TEL_TAG][error_message|%s]", e)
        return {"info:L": "0", "info:tf": "", "info:user": ""}


def get_weibo_tags_by_tid(weibo_id):

    start_time = time()
    try:
        with hbase_pool.connection() as conn:
            table_tags = conn.table(weibo_fri)
            org_tags = table_tags.row(weibo_id)
            if org_tags != {}:
                return json.loads(org_tags['fri:v']).get("ids")

        project_logger.info("[GET|WEIBO_TAG][TIME:%s]", time()-start_time)
        return []
    except Exception as e:
        project_logger.info("[GET][WEIBO_TAG][error_message|%s]", e)
        return []


def get_shop_list(phone_num):

    hbase_conn = init_env()
    start_time = time()
    try:
        #with hbase_pool.connection() as conn:
        table_tags = hbase_conn.table(portrait_v2)
        shop_list = {}
        shop_tags = table_tags.row(phone_num)
        if shop_tags:
            shop_list["m_bfifty_cnt_ratio"] = shop_tags["info:b50_num_ratio"]
            shop_list["m_rt_cat_num"] = shop_tags["info:root_cat_id_num"]
            shop_list["m_avg_month_cnt"] = shop_tags["info:avg_cnt"]
            shop_list["m_std_month_cnt"] = shop_tags["info:std_cnt"]
            shop_list["m_general_ratio"] = shop_tags["info:avg_price_ratio"]
            shop_list["m_bfifty_price_ratio"] = shop_tags["info:b50_ratio"]
            shop_list["m_avg_month_price"] = shop_tags["info:avg_price"]
            shop_list["m_brand_num"] = shop_tags["info:brand_id_num"]
            shop_list["m_cnt_ratio_list"] = shop_tags["info:cnt_ratio_list"]
            shop_list["m_price_ratio_list"] = shop_tags["info:price_ratio_list"]
            shop_list["m_pur_month_num"] = shop_tags["info:buy_month"]
            shop_list["m_std_month_price"] = shop_tags["info:std_price"]
            shop_list["m_b_price_ratio"] = shop_tags["info:b_bc_price_ratio"]
            shop_list["m_b_cnt_ratio"] = shop_tags["info:b_bc_type_num_ratio"]
            shop_list["m_pur_price_sum"] = shop_tags["info:total_price"]
            shop_list["m_brand_price_ratio"] = shop_tags["info:brand_effec_price_ratio"]
            shop_list["m_brand_cnt_ratio"] = shop_tags["info:brand_effec_num_ratio"]
            shop_list["m_ref_cnt"] = shop_tags.get("info:abnormal_cnt")
            shop_list["m_abnormal_cnt"] = shop_tags.get("info:ref_ec_cnt")
        def _fun(x):
            if shop_list[x] == '-':
                shop_list[x] = ''
        map(_fun, shop_list)
        shop_list["m_cnt_ratio_list"] = shop_tags["info:cnt_ratio_list"].split(":")
        shop_list["m_price_ratio_list"] = shop_tags["info:price_ratio_list"].split(":")
        project_logger.info("[GET|SHOPLIST][TIME:%s]", time()-start_time)
        if shop_list["m_pur_month_num"] == '//N':
            return {}
        return shop_list
    except Exception as e:
        project_logger.info("[GET][SHOPLIST][error_message|%s]", e)
        return {}
