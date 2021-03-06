import logging
import logging.config

from time import time
from functools import wraps

from flask import request
from flask.views import MethodView


conf = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': ('[%(asctime)s.%(msecs).03d] [%(levelname)s] '
                       '[pid|%(process)d] [%(name)s:%(lineno)d] %(message)s'),
            'datefmt': '%m-%d %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
    },
    'loggers': {
        'app': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True
        },
    }
}
logging.config.dictConfig(conf)
levelnames = logging._levelNames

# create logger
project_logger = logging.getLogger('app')


def class_logger(cls):
    cls.logger = project_logger.getChild(cls.__name__)
    return cls


def update_record(record, level, msg, *args):
    record.levelno = level
    record.levelname = levelnames[level]
    record.msg = msg
    record.args = args
    ct = time()
    record.created = ct
    record.msecs = (ct - long(ct)) * 1000


def trace_view(level=logging.INFO):
    def wrapper(view):
        for method in view.methods:
            method = method.lower()
            setattr(view, method, trace_method(level)(getattr(view, method)))
        return view
    if isinstance(level, int):
        return wrapper
    else:
        assert issubclass(level, MethodView), level
        view, level = level, logging.INFO
        return wrapper(view)


def trace_method(level=logging.INFO):
    def wrapper(func):
        assert level in levelnames, level
        co = func.func_code
        record = logging.LogRecord(
            '', level, co.co_filename, co.co_firstlineno, '', (), None,
            co.co_name
        )
        @wraps(func)
        def _(self, *args, **kwargs):
            class_name, method = self.__class__.__name__, request.method
            data = {
                'args': request.args,
                'form': request.form,
                'json': request.get_json()
            }
            peer, user = request.remote_addr, request.remote_user

            record.name = self.logger.name
            update_record(
                record, level,
                u'[view|%s][method|%s][peer|%s][user|%s] [request|%r]',
                class_name, method, peer, user, data
            )
            self.logger.handle(record)

            try:
                resp = func(self, *args, **kwargs)
            except BaseException as ex:
                update_record(
                    record, logging.ERROR,
                    u'[view|%s][method|%s][peer|%s][user|%s] [exception|%r]',
                    class_name, method, peer, user, ex
                )
                self.logger.handle(record)
                raise

            update_record(
                record, level,
                u'[view|%s][method|%s][peer|%s][user|%s] [response|%r]',
                class_name, method, peer, user, resp
            )
            self.logger.handle(record)
            return resp
        return _
    if isinstance(level, int):
        return wrapper
    else:
        assert callable(level)
        func, level = level, logging.INFO
        return wrapper(func)
