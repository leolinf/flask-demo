# -*- coding = utf-8 -*-


class Config:

    PROJECT = "epc-center"

    LOGGING_LEVEL = "DEBUG"

    BLUEPRINTS = (
        "app.demo:demo",
        "app:api:api",
    )

    EXTENSIONS = (
        "app.extensions:cache",
    )

    TEXPIRE = 36000

    MONGODB_URI = "mongodb://127.0.0.1:27017/epc-center"

    NAMEKO_AMQP_URI = "amqp://guest:guest@127.0.0.1:27017/epc-center"

    #################
    # 缓存
    #################
    CACHE_TYPE = "redis"
    CACHE_REDIS_URL = "redis://127.0.0.1:6379/10"
    CACHE_KEY_PREFIX = "{0}{1}".format(PROJECT, "-")
    CACHE_DEFAULT_TIMEOUT = 10

    #################
    # 七牛的参数
    #################
    QINIU_ACCESS_KEY = ""
    QINIU_SECRET_KEY = ""
    QINIU_BUCKET_NAME = ""
    QINIU_DOMAIN = ""

    #################
    # 微服务地址
    #################

    TIMEOUT = 10

    # 方法名  与微服务约定好 必须一样
    NAMEKO_CAR_STRUCTURE = "structure_get"
    NAMEKO_CAR_PARTS = "parts_get"
    NAMEKO_CAR_STRUCTURE_INFO = "structure_info"
    NAMEKO_CAR_PARTS_INFO = "parts_info"
    NAMEKO_CAR_FUZZY_QUERY = "fuzzy_query"
    NAMEKO_CAR_MODEL_SEARCH = "model_structure_info"
    NAMEKO_CAR_MODEL = "car_model"
    NAMEKO_CAR_ALL_PARTS_INFO = "all_parts_info"

    # 丰田 nameko
    NAMEKO_SERVICE_TOYOTA = "toyota"
    # 现代 nameko
    NAMEKO_SERVICE_HYUNDAI = "hyundai"
    # 大众 nameko
    NAMEKO_SERVICE_VOLKSWAGEN = "volkswagen"
    # 本田 nameko
    NAMEKO_SERVICE_HONDA = "honda"
    # 日产 nameko
    NAMEKO_SERVICE_NISSAN = "nissan"
