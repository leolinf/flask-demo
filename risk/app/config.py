# -*- coding: utf-8 -*-

class Config:
    PROJECT = 'risk'
    LOGGING_LEVEL = 'DEBUG'
    ENABLE_SENTRY = ""
    MONGODB_URI = "mongodb://192.168.0.187/risk?replicaSet=risk"
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:123456@127.0.0.1:3306/risk'
    SQLALCHEMY_POOL_SIZE = 2
    SQLALCHEMY_MAX_OVERFLOW = 2
    SQLALCHEMY_POOL_RECYCLE = 50
    SECRET_KEY = '2resrfiudrshjiubdgriubgdawe2r234'
