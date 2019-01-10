# -*- coding = utf-8 -*-

from app.config import Config
from pymongo import MongoClient


conn = MongoClient(host=Config.NISSAN_MONGO_URL, connect=False)
db = conn.nissan
