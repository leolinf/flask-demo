# -*- coding = utf-8 -*-

import logging
from functools import wraps

import time


# def exec_time(func):
#     """统计执行时间"""
#
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#
#         start_time = time.time()
#
#         resp = func(*args, **kwargs)
#
#         logger = logging.getLogger(func.__name__)
#         logger.info("{0}.{1}\t耗时{2}秒".format(func.__module__, func.__name__, time.time() - start_time))
#
#         return resp
#     return wrapper


def exec_time(fun, brand):

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            res = func(*args, **kwargs)
            logging.info("[{}|{}][TIME|{}]".format(fun, brand, time.time()-start_time))
            return res
        return wrapper
    return decorator


class AttrDict(dict):

    def __init__(self, *args, **kwargs):

        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

