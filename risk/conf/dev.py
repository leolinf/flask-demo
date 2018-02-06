# -*- coding: utf-8 -*-

import datetime


class Config:

    PROJECT = 'credit'

    SECRET_KEY = 'axdvno;qwjhefuiohasdf;kjase'
    BCRYPT_SALT = 'anti-fraud'

    LOGGING_LEVEL = "INFO"

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@127.0.0.1:3306/riskctrl22?charset=utf8'
    SQLALCHEMY_POOL_SIZE = 80
    SQLALCHEMY_POOL_RECYCLE = 1800
    SQLALCHEMY_MAX_OVERFLOW = 20

    MONGODB_DB = 'riskctrlpy'
    MONGODB_HOST = '127.0.0.1'
    MONGODB_PORT = 27017
    MONGODB_USERNAME = ''
    MONGODB_PASSWORD = ''

    # 百度地图的key
    BAIDU_AK = ""

    # CELERY_BROKER_URL = 'redis://127.0.0.1:6379/3'
    CELERY_BROKER_URL = 'amqp://guest:guest@127.0.0.1/riskctrlpy'
    CELERY_RESULT_BACKEND = 'redis://127.0.0.1:6379/3'

    # 外接口调用白名单
    API_WHITE_LIST = []

    # api接口查询
    URI = ''
    TAOBAO_URI = ''
    SECRET = ''
    APPKEY = ''
    TIMEOUT = 10

    # 马上正式的配置
    URL = ''
    FACE_URL = ''
    ENCRYPT_KEY = ''
    PARTNER = ''
    SIGNKEY = ''
    SENTRY_DSN = ''
    VERSION = '2.0'
    SIGN_TYPE = 'SHA1'
    CHARSET = 'UTF-8'
    METHOD = ''

    # 运营商对接的配置项
    CAPCHA_TOKEN_URL = ''
    APIX_KEY = ''

    # 队列
    UNLOCK_QUEUE = 'unlock_q'
    MONITOR_QUEUE = 'monitor_q'
    SMS_QUEUE = 'sms_q'
    ANTI_QUEUE = 'anti_q'

    # 锁的过期时间
    LOCK_TIME = 60 * 10
    # 扫描锁过期的周期
    UNLOCK_PERIOD = 2
    # 七牛配置
    QINIU_ACCESS_KEY = ""
    QINIU_SECRET_KEY = ""
    QINIU_BUCKET_NAME = ""
    QINIU_BUCKET_DOMAIN = ""

    # 上上签信息
    SSQ_URL = ''
    SSQ_MID = ''
    SSQ_PRIVATE_KEY = """"""
    SSQ_NAME = ''
    SSQ_MOBILE = ''
    SSQ_USERTYPE = ''
    SSQ_SIGNIMAGETYPE = ''
    SSQ_USERFILETYPE = '1'
    SSQ_FILETYPE = 'pdf'
    SSQ_EMAIL = ''

    # REDIS
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_PASSWORD = ''
    REDIS_DB = '0'

    # 叮咚云
    DDY_APIKEY = ''
    DDY_SMSHOST = ''
    DDY_TZURI = ''
    DDY_YZMURI = ''

    # 查询配置
    REPEAT_NUM = ''
    CREDIT_DOMAIN = ''
    ENABLE_SENTRY = ''

    # 高德地图key
    GD_KEY = ''
    # java微服务的域名
    JAVA_HOST = ''

    # pdf下载的地址
    PDF_URL = ''

    FILE_SERVER_TOKEN = ""
    REMEMBER_COOKIE_DURATION = datetime.timedelta(seconds=1)
    SESSION_REFRESH_EACH_REQUEST = True
    MOJIE_TOKEN = ''
    JAVA_MERCHANT = ""
