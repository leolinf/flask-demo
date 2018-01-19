# -*- coding: utf-8 -*-

import datetime
from settings import (
    mongo_refer_record, mongo_weibo_info,
    mongo_weibo_key, mongo_weibo_link,
    mongo_weibo_vip, mongo_weibo_fri,
    weibo_userinfo, weibo_career,
    weibo_education, weibo_tag,
    weibo_basicinfo, credit_tel_risk,
    weibo_age_gender
)

from .session import db, portrait


def authenticate(appkey, secret):
    '''用户验证'''

    return db.user.find_one({'username': appkey, 'password': secret})

def weibo_basic_info(wid):
    """微博用户基本信息"""

    return db[weibo_basicinfo].find_one({"id": wid})

def weibo_user_info(wid):
    """微博用户基本信息"""

    return db[weibo_userinfo].find_one({"id": wid})

def weibo_edu(wid):
    """教育信息"""

    return db[weibo_education].find_one({"id": wid})

def weibo_age_sex(phone):
    """教育信息"""

    return db[weibo_age_gender].find_one({"cell": str(phone)})

def weibo_user_career(wid):
    """微博工作信息"""

    return db[weibo_career].find_one({"id": wid})

def weibo_user_tag(wid):
    """微博标签"""

    return db[weibo_tag].find_one({"id": wid})

def credit_phone_risk(phone):
    """电商高位清单"""

    return list(db[credit_tel_risk].find({"phone": phone}))

def get_weibo_info(wid):
    '''weibo baseinfo message'''

    return portrait[mongo_weibo_info].find_one({"weibo_id": wid}, {"_id": 0})


def get_weibo_info_all(wid):
    '''weibo baseinfo message all'''

    return list(portrait[mongo_weibo_info].find({"weibo_id": {"$in": wid}}, {"_id": 0}).sort([("weibo_pagerank", -1)]))


def get_weibo_key(wid):
    '''weibo user keywords'''

    return portrait[mongo_weibo_key].find_one({"user_id": str(wid)}, {"_id": 0})

def get_weibo_link(wid):
    '''weibo friends link'''

    return portrait[mongo_weibo_link].find_one({"weibo_id": wid}, {"_id": 0})

def get_weibo_link_all(wid):
    '''weibo friends link all'''

    return list(portrait[mongo_weibo_link].find({"weibo_id": {"$in": wid}}, {"_id": 0}))

def get_weibo_fri(wid):
    '''weibo baseinfo message'''

    return list(portrait[mongo_weibo_fri].find({"ID": {"$in": wid}}, {"_id": 0}))

def get_weibo_vip(wid):
    '''weibo vip baseinfo message'''

    return list(portrait[mongo_weibo_vip].find({"id": {"$in": wid}}, {"_id": 0, "id": 1,
                                               "name": 1,"gender": 1, "province": 1,
                                               "city": 1, "location": 1,
                                               "followers_count": 1, "description": 1,
                                               "profile_image_url": 1 }))

def record(appkey, request):
    '''调用记录'''

    now = datetime.datetime.now()
    path = request.path
    params = request.args
    db[mongo_refer_record].insert({
        'app_key': appkey,
        'create_time': now,
        'interface': path,
        'params': params
    })
