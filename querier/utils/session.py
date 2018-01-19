# -*- coding: utf-8 -*-

import happybase
from pymongo import MongoClient

from settings import (
    mongo_refer_db, mongo_uri, mongo_portrait_db,
    thrift_server_ip, thrift_server_port, mongo_uri_down
)

conn_refer = MongoClient(mongo_uri, connect=False)
db = conn_refer[mongo_refer_db]

conn = MongoClient(mongo_uri_down, connect=False)
portrait = conn[mongo_portrait_db]

hbase_pool = happybase.ConnectionPool(
    size=10, host=thrift_server_ip,
    port=thrift_server_port, timeout=5000
)
