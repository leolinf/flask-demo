# -*- coding: utf-8 -*-

from functools import wraps

import requests
from geventhttpclient import URL, HTTPClient
from gevent import getcurrent

from app.config import Config
from app.core.logger import project_logger
from urllib.parse import urlencode


class HttpClientStatus(object):
    def __init__(self, client, flag, indent):
        self.__client = client
        self.__flag = flag
        self.__indent = indent

    @property
    def client(self):
        return self.__client

    def status(inst):
        if inst.__indent is not None and inst.__flag is False:
            # 协程没有结束,但是__flag提示可用,状态有误
            raise RuntimeError('indent is running, but the __flag is Flase')
        if inst.__indent is None and inst.__flag is True:
            raise RuntimeError('indent is over, but the __flag is True')
        if inst.__indent is None and inst.__flag is False:
            return True
        else:
            return False

    def status_to_used(self):
        self.__flag = True
        self.__flag = getcurrent()

    def status_to_unuse(self):
        self.__flag = False
        self.__flag = None



class HttpPool:
    pool = {}

    @classmethod
    def initial_pool(cls, urls):
        if (not isinstance(urls, list)) and (not isinstance(urls, tuple)):
            raise RuntimeError('urls should be instance of list or tuple')
        for url in urls:
            cls.add_url(url)

    @classmethod
    def add_url(self, url):
        if isinstance(url, URL):
            encode_url = url
        else:
            encode_url = URL(url)
        key = encode_url.host, encode_url.port
        ret = HttpPool.pool.get(key, None)
        http = HttpClientStatus(
            HTTPClient.from_url(encode_url,  connection_timeout=10,network_timeout=30, concurrency=20),
            False,
            None)
        if ret is None:
            HttpPool.pool.update({key: [http]})
        else:
            HttpPool.pool[key].append(http)
        return http

    @classmethod
    def get_client(self, url):
        encode_url = URL(url)
        client_key = encode_url.host, encode_url.port
        if client_key not in HttpPool.pool:
            http_stat = self.add_url(encode_url)
            return http_stat
        else:
            http_stats = HttpPool.pool.get(client_key, [])
            for http in http_stats:
                # print("status", http.status())
                if http.status() is True:
                    return http
            # 已经建立的缓存池被使用完, 需要开辟新的空间
        http_stat = self.add_url(encode_url)
        return http_stat

HttpPool.initial_pool([
    Config.URL,
    Config.URI,
    Config.FACE_URL
])


class __PostResponse(object):
    __instance = None
    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = object.__new__(cls)
            return cls.__instance
        else:
            return cls.__instance

    def __init__(self, status, text):
        self.__status = status
        self.__text = text

    @property
    def status_code(self):
        return self.__status
    @property
    def text(self):
        return self.__text


def async_request(url, data=None, method='get', http_client=None, headers=None, dont_dump=False):
    if http_client is None:
        http_client = HttpPool.get_client(url).client
    if method =='get' or method == 'GET':
        try:
            if headers:
                response = http_client.get(url, headers=headers)
            else:
                response = http_client.get(url)

            content = response.read().decode('utf-8')
        except Exception as e:
            project_logger.warn('\nurl %s exception %s' %(url, str(e)))
            return '{}'
        if response.status_code == 200:
            return content
        else:
            project_logger.warn('url:%s status_code: %s is not 200, \
                conent: %s' %(url, response.status_code, content))
            return '{}'
    elif method == 'post' or method == 'POST':
        if not headers:
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            if isinstance(data, dict) and not dont_dump:
                data = urlencode(data)
                response = http_client.post(url, body=data, headers=headers)
                content = response.read().decode('utf-8')
            else:
                response = requests.post(url, data=data)
                content = response.text
        except Exception as e:
            import traceback
            traceback.print_exc()
            return __PostResponse(200, '{}')
        if response.status_code == 200 and dont_dump:
            return content
        if response.status_code == 200:
            return __PostResponse(response.status_code, content)
        else:
            project_logger.warn('url:%s status_code: %s is not 200, \
                conent: %s' %(url, response.status_code, content))
            return __PostResponse(200, '{}')
