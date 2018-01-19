# -*- coding: utf-8 -*-
import random
import string
import time
import datetime
import hashlib

from decimal import Decimal
from urllib.parse import quote, urlencode

from flask.json import JSONEncoder
from flask import jsonify

from app.constants import Code
from app.config import Config
from app.core.logger import project_logger


def datetime2timestamp(sometime):
    """转换datetime为timestamp"""

    if not sometime:
        return

    return time.mktime(sometime.timetuple()) * 1000

def timestamp2datetime(stamp):
    """时间戳转datetime"""

    return datetime.datetime.fromtimestamp(stamp / 1000)

class CustomJSONEncoder(JSONEncoder):

    def default(self, obj):

        if isinstance(obj, datetime.datetime):
            return datetime2timestamp(obj)

        if isinstance(obj, Decimal):
            return int(obj)

        return JSONEncoder.default(self, obj)


def make_response(data=None, status=Code.SUCCESS, msg=""):
    if data is None:
        data = {}

    if not msg:
        msg = Code.MSG.get(status)

    return jsonify({
        'data': data,
        'code': status,
        'msg': msg,
    })


def generate_field_key(src):
    # if isinstance(src, str):
    #     src = src.encode("utf-8")
    # return base64.b64encode(src).decode('utf-8')
    return "".join(random.choice(string.ascii_lowercase) for _ in range(20))


def period2datetime(period):
    """时间段转datetime"""

    period_map = {
        'today': 1,
        'week': 7,
        'month': 30,
    }

    today = datetime.date.today() + datetime.timedelta(days=1)
    today = datetime.datetime.fromtimestamp(int(today.strftime('%s')))

    start = today - datetime.timedelta(period_map[period])
    return start, today


def querystring(url_m, data, method='GET', platform='api'):
    """请求sign 的计算,生成url"""

    secret = Config.SECRET
    now = str(time.time())
    data.update({'t': now})
    data.update({"app_key": Config.APPKEY})
    l = []
    for k in data:
        if k == 'sign':
            continue
        if data[k] is None:
            continue
        l.append(k + quote(data[k].encode('utf-8')))
    s = secret + ''.join(sorted(l)) + secret
    sign = hashlib.md5(s.encode("utf-8")).hexdigest()
    for k in data:
        if data[k] is None:
            continue
        data[k] = data[k].encode('utf-8')
    data.update({'sign': sign})
    if method == 'GET':
        uri_last = urlencode(data)
        if platform == "api":
            return Config.URI + url_m + uri_last
        else:
            return Config.TAOBAO_URI + url_m + uri_last
    else:
        if platform == "api":
            return Config.URI + url_m, data
        return Config.TAOBAO_URI + url_m, data


def time_change(data):
    """时间转换"""
    try:
        data = int(data)
    except ValueError:
        return 0
    if len(str(data)) == 6:
        return time.mktime(datetime.datetime.strptime(str(data), "%Y%m").timetuple()) * 1000
    return time.mktime(datetime.datetime.strptime(str(data), "%Y%m%d").timetuple()) * 1000


def time_change_phone(data):
    """手机活跃度综合校验"""
    if not data:
        return 0
    if data is None:
        return 0
    try:
        return time.mktime(datetime.datetime.strptime(str(data), "%Y.%m.%d").timetuple()) * 1000
    except ValueError:
        return 0


def sex_from_idcard(idcard):
    """身份证号计算性别"""

    def _is_male(n):
        return bool(int(n) % 2)

    return '男' if _is_male(idcard[-2]) else '女'


def age_from_idcard(idcard):
    """身份证号计算年龄"""

    if not idcard:
        return -100

    birth = idcard[6:14]
    birthday = datetime.datetime.strptime(birth, '%Y%m%d')
    now = datetime.datetime.now()

    return now.year - birthday.year


def dict_list_util(ret):
    """字典和列表有空数据全部改成×××"""

    if isinstance(ret, list):
        for i in ret:
            dict_list_util(i)

    if isinstance(ret, dict):
        for k, v in ret.items():
            if v == '-':
                ret[k] = ""
            if isinstance(ret[k], dict):
                dict_list_util(ret[k])

            if isinstance(ret[k], list):
                dict_list_util(ret[k])


def somedate2timestamp(year, month, day):
    """年月日转换为时间戳"""

    return int(datetime.datetime(year, month, day).strftime('%s')) * 1000


def save_to_cache(apply_number, data, uri):
    """保存数据"""

    project_logger.info('保存数据到缓存\t{0}\t{1}'.format(apply_number, uri))
    apply_number = int(apply_number)

    kw = {}
    for k, v in data.items():
        key = 'set__{0}_{1}'.format(uri, k)
        kw[key] = v
    from app.models import SearchCache

    SearchCache.objects(apply_number=apply_number).update(
        upsert=True,
        set__apply_number=apply_number,
        **kw
    )


def get_from_cache(apply_number, uri):

    from app.models import SearchCache
    apply_number = int(apply_number)
    from app.constants import CacheFields
    fields = CacheFields[uri]

    cache = SearchCache.objects(apply_number=apply_number).first()
    if cache:
        res = {}
        flag = 0
        for field in fields:
            try:
                f = '{0}_{1}'.format(uri, field)
                res[field] = getattr(cache, f)
                flag += 1
            except:
                pass

        if flag is 0:
            return

        project_logger.info('从缓存中取的数据\t{0}\t{1}'.format(apply_number, uri))
        return res

