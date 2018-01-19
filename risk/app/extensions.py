# -*- coding: utf-8 -*-

from flask_login import LoginManager
from raven.contrib.flask import Sentry


login_manager = LoginManager()
sentry = Sentry()
