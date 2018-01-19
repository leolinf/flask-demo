# -*- encoding: utf-8 -*-
import sys
sys.path.append("../")

import time
import hashlib
import urllib
import requests

from settings import timeout, app_secret, app_key, uri

from framework.logger import project_logger
from .data import gen_tbid_nick


def gen_sign(secret, data):

    now = str(time.time())

    data.update({'t': now, 'app_key': app_key}),

    l = []
    for k in data:
        if k == 'sign':
            continue
        l.append(k + urllib.quote(data[k].encode('utf-8')))

    s = secret + ''.join(sorted(l)) + secret
    return hashlib.md5(s).hexdigest()


def querystring(data):
    sign = gen_sign(app_secret, data)
    for k in data:
        data[k] = data[k].encode('utf-8')
    data.update({'sign': sign})
    return urllib.urlencode(data)


def request_data(url):
    try:
        response = requests.get(url, timeout=timeout).json()
    except Exception as e:
        project_logger.warn("[REQUEST][ERROR|%s]", str(e))
        return None
    return response

def get_tbid_from_nick(enc_m):
    d = {'enc_m': enc_m}
    url = '%s/address/analysis/get/?%s'%(uri, querystring(d))
    result = request_data(url)
    project_logger.info("[GET][REPONSE|%s]", str(result))
    if result:
        if result.get("code") == 1200:
            info_list = result.get("data", {}).get("info_list", [])
            for info in info_list:
                if info.get("buyerAlipayNo", "") == enc_m:
                    return gen_tbid_nick(info.get("buyerNick"))
    return []


if __name__ == "__main__":
    get_tbid_from_nick(sys.argv[1])
