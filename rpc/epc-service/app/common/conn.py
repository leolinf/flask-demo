# -*- coding: utf-8 -*-

from pymongo import MongoClient

from app.config import Config

client = MongoClient(Config.UNIVERSAL_DB)
db_epc = client.epc


def epc_brand(origin):
    """查询品牌名称"""
    resp = db_epc.car_name.find_one({"origin": origin})
    if resp:
        return resp.get("brand"), resp.get("sorted")
    return "", ""
