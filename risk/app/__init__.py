# -*- coding: utf-8 -*-

import logging.config

from sqlalchemy import create_engine
from mongoengine import connect
from flask_login import AnonymousUserMixin
from flask import Flask, g, redirect, request, url_for, session
from celery import Celery
import datetime

from .config import Config
from .extensions import login_manager, sentry
from .databases import Session
from .constants import Code
from .core.functions import CustomJSONEncoder, make_response
from app.user.function import current_user


celery = Celery(
    __name__,
    broker=Config.CELERY_BROKER_URL,
    include=['task.tasks'],
)


def create_app(conf=None):

    app = Flask(
        Config.PROJECT,
        template_folder='templates',
        static_folder='static',
    )
    app.permanent_session_lifetime = datetime.timedelta(days=1)
    app.json_encoder = CustomJSONEncoder
    app.url_map.strict_slashes = False

    config_session(app)
    config_app(app, conf)
    config_logger()
    config_database(app)
    config_extension(app)
    config_blueprints(app)
    config_celery(app)

    return app


def config_session(app):
    """ update session to update session_cookie """
    @app.after_request
    def update_session_after_request(response):
        session.permanent = True
        return response


def config_app(app, config):

    app.config.from_object(Config)
    if config:
        app.config.from_object(config)


def config_blueprints(application):

    from app.loan import loan
    application.register_blueprint(loan)
    from app.review import review
    application.register_blueprint(review)
    from app.ssq import ssq
    application.register_blueprint(ssq)
    from app.credit import credit
    application.register_blueprint(credit)
    from app.merch.urls import merch_blue
    application.register_blueprint(merch_blue)
    from app.apply_table.urls import apply_blue
    application.register_blueprint(apply_blue)
    from app.statistics import statistics
    application.register_blueprint(statistics)
    from app.user.urls import user_blue
    application.register_blueprint(user_blue)
    from app.monitor import monitor
    application.register_blueprint(monitor)
    from app.third_api.urls import third_blue
    application.register_blueprint(third_blue)


class CusAnonymousUserMixin(AnonymousUserMixin):
    cus_variable = 1


def config_extension(app):

    login_manager.init_app(app)

    if Config.ENABLE_SENTRY:
        sentry.init_app(app, dsn=Config.SENTRY_DSN)

    @login_manager.unauthorized_handler
    def unauthorized():
        need_to_redirect_paths = [
        ]
        if request.path in need_to_redirect_paths:
            return redirect(url_for('front.signin'))

        if getattr(g, "error", None):
            msg = "mysql error"
            return make_response(status=Code.NEED_LOGIN, msg=msg)

        if getattr(current_user, 'cus_variable', None) == 1:
            return make_response(status=Code.VALID_ACCOUNT)
        else:
            return make_response(status=Code.NEED_LOGIN)


def config_database(app):

    engine = create_engine(
        app.config['SQLALCHEMY_DATABASE_URI'],
        pool_size=app.config['SQLALCHEMY_POOL_SIZE'],
        max_overflow=app.config['SQLALCHEMY_MAX_OVERFLOW'],
        pool_recycle=app.config['SQLALCHEMY_POOL_RECYCLE'],
    )
    # engine.pool._use_threadlocal = True
    Session.configure(bind=engine)

    connect(
        db=app.config['MONGODB_DB'],
        host=app.config['MONGODB_HOST'],
        port=app.config['MONGODB_PORT'],
        username=app.config['MONGODB_USERNAME'],
        password=app.config['MONGODB_PASSWORD'],
        connect=False,
    )


def config_logger():
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


def config_celery(app):

    celery.config_from_object(app.config)

    celery.conf.update(
        CELERY_TIMEZONE='Asia/Chongqing',
        CELERYBEAT_SCHEDULE={
            'unlock': {
                'task': 'task.tasks.unlock_period',
                'schedule': Config.UNLOCK_PERIOD,
                'options': {
                    'queue': Config.UNLOCK_QUEUE,
                },
            },
        },
    )
