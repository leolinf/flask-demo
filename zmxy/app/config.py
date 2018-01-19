# -*- coding: utf-8 -*-

class Config:

    PROJECT = "zmxy"

    # 默认mongodb
    MONGO_DATABASE_URI = "mongodb://127.0.0.1/data_market"
    MONGO_DATABASE_NAME = 'data_market'
    # 数据集市
    API_URL = 'http://127.0.0.1:8080'
    APP_KEY = "123"
    APP_SECRET = "zmhyvz86tu75n0o0i14f868t"
    ZMXY_AUTH = "/v2/zhima_credit/auth/"
    ZMXY_SCORE = "/v2/zhima_credit/score/"
    ZMXY_WATCHLIST = "/v2/zhima_credit/watchlist/"
