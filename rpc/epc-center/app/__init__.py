# -*- coding = utf-8 -*-

import logging.config

from flask import Flask
from werkzeug.utils import import_string
from mongoengine import register_connection

from app.config import Config


def create_app():

    app = Flask(
        Config.PROJECT,
        template_folder='templates',
        static_folder='static'
    )

    config_mongodb()
    config_blueprints(app)
    config_logging()
    config_extensions(app)

    return app


def config_blueprints(app):

    for i in Config.BLUEPRINTS:
        bp = import_string(i)
        app.register_blueprint(bp)


def config_mongodb():

    register_connection('default', host=Config.MONGODB_URI, connect=False)


def config_logging():

    config_dict = {
        'version': 1,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'default': {
                'formatter': 'standard',
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            '': {
                'handlers': ['default'],
                'level': Config.LOGGING_LEVEL,
                'propagate': True
            },
        }
    }

    logging.config.dictConfig(config_dict)


def config_extensions(app):

    for i in Config.EXTENSIONS:
        ext = import_string(i)
        ext.init_app(app)
