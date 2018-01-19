# -*- coding: utf-8 -*-

from flask import Blueprint


usertags = Blueprint("usertags", __name__)

from . import urls
