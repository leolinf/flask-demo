# -*- coding: utf-8 -*-

from mongoengine import connect
from flask import Flask

from .config import Config
from .extensions import sentry


def create_app(config=None):

    app = Flask(
        Config.PROJECT
    )
    config_app(app, config)
    config_database(app)
    config_extension(app)
    config_blueprints(app)

    return app


def config_app(app, config):

    app.config.from_object(Config)
    if config:
        app.config.from_object(config)


def config_blueprints(app):
    """蓝图注入"""

    from app.taobao import taobao
    from app.front import front
    app.register_blueprint(taobao, url_prefix="/api")
    app.register_blueprint(front)


def config_extension(app):

    if Config.ENABLE_SENTRY:
        sentry.init_app(app, dsn=Config.SENTRY_DSN)


def config_database(app):

    connect(
        db=app.config['MONGO_DATABASE_NAME'],
        host=app.config['MONGO_DATABASE_URI'],
        connect=False,
    )
