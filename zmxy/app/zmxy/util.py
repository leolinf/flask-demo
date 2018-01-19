# -*- coding: utf-8 -*-

import requests
import json
import time
import hashlib
import urllib
import urllib.parse
from app.config import Config

uri = Config.API_URL

secret = Config.APP_SECRET


def gen_sign(secret, data):

    now = str(int(time.time()))

    data.update({'t': now, 'app_key': Config.APP_KEY})

    l = []
    for k in data:
        if k == 'sign':
            continue
        l.append(k + urllib.parse.quote(data[k], safe=''))

    s = secret + ''.join(sorted(l)) + secret
    return hashlib.md5(s.encode()).hexdigest()


def querystring(data):

    sign = gen_sign(secret, data)
    for k in data:
        data[k] = data[k].encode('utf-8')
    data.update({'sign': sign})
    return urllib.parse.urlencode(data)


def zmxy_auth(name, idCard, phone):
    d = {
        'name': name,
        "appId": "1003622",
        'idCard': idCard,
        'phone': phone,
        'identityType': "2"
    }
    url = '%s/v2/zhima_credit/auth/?%s'%(uri, querystring(d))
    return request_data(url)


def score(params, params_sign):
    d = {
        'params': params,
        'params_sign': params_sign,
        "appId": "1003622",
    }
    url = '%s/v2/zhima_credit/score/?%s'%(uri, querystring(d))
    return request_data(url)


def watchlist(params, params_sign):
    d = {
        'params': params,
        'params_sign': params_sign,
        "appId": "1003622",
    }
    url = '%s/v2/zhima_credit/watchlist/?%s'%(uri, querystring(d))
    return request_data(url)


def request_data(url):
    return requests.get(url, timeout=20).json()
