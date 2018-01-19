#coding: utf-8
"""
图片权限问题
"""
# import sys
# sys.path.append("../")
# sys.path.append("../../")
import redis
import random
from sqlalchemy.orm import scoped_session
import string
import datetime
from functools import wraps
import json
import traceback
from functools import reduce
from app.databases import Session
from flask import request, current_app, g
from flask_login.config import EXEMPT_METHODS
from app.models.sqlas import InputApply
import os
from app.config import Config
from Crypto.Cipher import AES
import logging

from werkzeug.local import LocalProxy
from flask_login import AnonymousUserMixin
from app.models import User


def get_current_user():

    user_id = request.args.get('userId')

    try:
        session = scoped_session(Session)
    except Exception as e:
        logging.exception(e)
        g.error = str(e)
        session.remove()
        return AnonymousUserMixin()

    try:
        user = session.query(User).filter(User.id == user_id).one_or_none()
    except Exception as e:
        logging.exception(e)
        g.error = str(e)
        session.remove()
        return AnonymousUserMixin()

    if not user:
        g.error = None
        return AnonymousUserMixin()

    g.session = session
    g.user = user

    return user


current_user = LocalProxy(lambda: getattr(g, "user", AnonymousUserMixin()))


def wrapper(func):
    @wraps(func)
    def decator(self, *args, **kwargs):
        index, e = 0, None
        while index < 3:
            try:
                if self.redis_cli is None:
                    raise RuntimeError("redis has not init, please run the self.init_connect")
                return func(self, *args, **kwargs)
            except Exception as ex:
                traceback.print_exc()
                e = ex
                index += 1
        if index == 3:
            raise e
    return decator


class ImgController:
    COOKIE_KEY = 'consumer_financial_cookie_keys'
    def __init__(self, redis_cli=None, cookie_key=None):
        self.redis_cli = redis_cli
        self.cookie_key = cookie_key or self.COOKIE_KEY


    def init_connect(self, kw):
        print("redis",kw['REDIS_HOST'], kw['REDIS_PORT'], kw['REDIS_DB'])
        self.redis_cli = redis.StrictRedis(host=kw['REDIS_HOST'], port=kw['REDIS_PORT'], db=kw['REDIS_DB'], password=kw['REDIS_PASSWORD'])

    def get_keys(self):
        """ 获取所有没有过期的key """
        all_keys = self.redis_cli.smembers(self.cookie_key)
        return all_keys

    def get_key_value(self, key):
        return self.redis_cli.get(key)

    @wrapper
    def img_set_key(self, user_id, company_id, length=16, time_out=24):
        expire_t = datetime.timedelta(hours=time_out)
        key = None
        while True:
            key = random.sample(string.ascii_letters, length)
            key = reduce(lambda s, x: s + x, key)

            ret = self.redis_cli.sadd(self.cookie_key, key)
            if ret == 1:
                break
        value = json.dumps({"userId": user_id, "companyId": company_id})
        assert self.redis_cli.set(key, value, ex=expire_t) == 1
        return key

    def set_cookie(self, resp, cookie):
        resp.set_cookie("ctoken".encode("utf-8"), value=cookie)
        return resp


class Single(type):

    def __init__(self, *args, **kwargs):
        self.__instance = {}

    def __call__(self, *args, **kwargs):
        pid = os.getpid()
        if pid in self.__instance:
            return self.__instance[pid]
        else:
            obj = super().__call__(*args, **kwargs)
            self.__instance[pid] = obj
            return obj


class MyCrypt():
    length = 16
    time_expire = 24

    def __init__(self, key, redis_cli):
        self.key = key
        self.mode = AES.MODE_CBC
        self.redis_cli = redis_cli

    def myencrypt(self, text):
        import random
        import string
        result = ''.join(random.sample(string.ascii_letters, self.length))
        expire_at = datetime.timedelta(hours=self.time_expire)
        print("\n\n********************set ", result, '\n\n')
        assert self.redis_cli.set(result, text, ex=expire_at) == 1
        return result.encode('utf-8')


    def mydecrypt(self, text):
        ret = self.redis_cli.get(text)
        if isinstance(ret, bytes):
            ret = ret.decode("utf-8")
        return ret


class TokenAuth(metaclass=Single):
    """
    uwsgi启动的时候的lazy_app参数需要加上

    """
    AES1 = 'this is a key123'
    AES2 = 'this is an IV456'

    redis_name = 'PDF_DOWNLOAD'
    key = 'abcdefghjklmnopq'
    time_expire = 3600*10

    # aes_obj = #AES.new(AES1, AES.MODE_CBC, AES2)

    def __init__(self, time_expire=None):
        self.__redis_cli = redis.StrictRedis(
            host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=Config.REDIS_DB,
            password=Config.REDIS_PASSWORD)
        self.time_expire =  time_expire or self.time_expire
        self.aes_obj = MyCrypt(self.__class__.key, self.__redis_cli)

    def encode_key(self, data):
        if isinstance(data, dict):
            data = json.dumps(data)

        # return self.aes_obj.encrypt(data)
        return self.aes_obj.myencrypt(data)

    def authority(self, data):
        if data is None:
            return False

        if isinstance(data, str):
            data = data.encode("utf-8")
        session = getattr(g, 'session', None)
        if session is None:
            session = scoped_session(Session)
            g.session = session

        try:
            data_str = self.aes_obj.mydecrypt(data)
            print("\n\nafter decode", data_str)
            decode_data = json.loads(data_str)
            if not self.redis_query(data):
                return False

            input_obj = session.query(InputApply).filter_by(id=int(decode_data.get("id", "-1"))).first()
            if input_obj and input_obj.input_user.company_id == str(decode_data.get("company_id")):
                return True
            return False
        except Exception as ex:
            logging.error("error info %s" % (str(ex)))
            return False

    def get_redis_query_name(self, data):
        return data

    def redis_query(self, data):
        """ """
        key =self.get_redis_query_name(data)
        return self.__redis_cli.get(key)

    def redis_set(self, data):
        # expire_at = datetime.timedelta(hours=self.time_expire)
        aft_code = self.encode_key(data)


def custom_login_required(func):
    """ 针对信用报告pdf下载所做的权限控制 """
    auth_obj = TokenAuth()

    @wraps(func)
    def decorated_view(*args, **kwargs):
        nonlocal auth_obj

        if request.method in EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif current_app.login_manager._login_disabled:
            return func(*args, **kwargs)
        elif not current_user.is_authenticated:
            if request.method == 'GET' or request.method== 'get': 
                token = request.args.get("token")
            else:
                token = request.json.get("token")
            print("\n\n all token ", token)
            if auth_obj.authority(token):
                return func(*args, **kwargs)

            return current_app.login_manager.unauthorized()

        return func(*args, **kwargs)

    return decorated_view


def login_required(func):
    """python端作为透传而不是server以后的登录限制"""

    @wraps(func)
    def wrapper(*args, **kwargs):

        path = request.path

        no_need_login = [
            "/api/merchant/",
            "/api/credit/query/",
        ]

        user = get_current_user()

        if path not in no_need_login and not user.is_authenticated:
            return current_app.login_manager.unauthorized()

        return func(*args, **kwargs)
    return wrapper
