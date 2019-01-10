# -*- coding = utf-8 -*-


class Config:

    PROJECT = "epc-service"
    LOGGING_LEVEL = "DEBUG"
    # 对应的数据库链接地址
    NISSAN_MONGO_URL = ""

    # rpc rabbitmq地址
    AMQP_URI = "amqp://guest:guest@127.0.0.1:5672/epc-center"

    # 图片地址
    IMG_URL = 'xxx'
    #################
    # 微服务地址
    #################
    CAR_NISSAN = 'nissan'
