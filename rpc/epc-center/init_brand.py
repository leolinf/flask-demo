#! /usr/bin/env python
# -*- coding = utf-8 -*-

import json
import logging
import uuid

import qiniu
import requests

from app import create_app
from app.models import BrandByFirstLetter, Brand
from app.config import Config


def upload_to_qiniu(pic, name):

    try:
        r = requests.get(pic, timeout=5)
    except Exception as e:
        logging.error("处理 {0} 的时候出错了 {1}".format(name, e))
        return ""

    q = qiniu.Auth(Config.QINIU_ACCESS_KEY, Config.QINIU_SECRET_KEY)

    key = str(uuid.uuid4())
    token = q.upload_token(Config.QINIU_BUCKET_NAME, key)
    qiniu.put_data(token, key=key, data=r.content)

    return "{0}/{1}".format(Config.QINIU_DOMAIN, key)


def process_brand(brand):
    brand["logo"] = upload_to_qiniu(brand["logo"], brand["brandname"])
    return brand


def main():

    filename = "carbrand.info.20170913"

    with open(filename) as f:
        while True:
            line = f.readline()
            if not line:
                break

            line = json.loads(line)

            first_letter = line["FirstLetter"]
            real_brand_list = []
            for brand in line["BrandList"]:
                real_brand_list.append(process_brand(brand))
                Brand(brand_name=brand["brandname"], brand_id=brand["brandid"]).save()

            BrandByFirstLetter(first_letter=first_letter, brand_list=real_brand_list).save()


if __name__ == '__main__':
    create_app()
    main()
