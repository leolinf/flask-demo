# -*- coding: utf-8 -*-

class Config:

    PROJECT = "api_view"

    # 默认mongodb
    MONGO_DATABASE_URI = "mongodb://127.0.0.1:27017/data_market"
    MONGO_DATABASE_NAME = 'data_market'

    # 小时
    TIMES = 1000

    ENABLE_SENTRY = False
    SENTRY_DSN = 'https://787b781155724bb791acbf79d3639157:9d265b1cf3614dbb8cc3a2e69affeeff@sentry.io/179847'
