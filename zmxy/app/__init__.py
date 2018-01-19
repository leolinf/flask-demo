# -*- coding: utf-8 -*-

from mongoengine import connect
from flask import Flask

from .config import Config


def create_app(config=None):

    app = Flask(
        Config.PROJECT,
        template_folder='templates',
        static_folder='static',
    )
    config_app(app, config)
    config_database(app)
    config_blueprints(app)

    return app


def config_app(app, config):

    app.config.from_object(Config)
    if config:
        app.config.from_object(config)


def config_blueprints(app):
    """蓝图注入"""

    from app.zmxy import zmxy
    from app.front import front
    app.register_blueprint(zmxy)
    app.register_blueprint(front)


def config_database(app):

    connect(
        db=app.config['MONGO_DATABASE_NAME'],
        host=app.config['MONGO_DATABASE_URI'],
        connect=False,
    )
