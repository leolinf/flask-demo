# -*- coding: utf-8 -*-
from flask import Blueprint
from flask_restful import Api

from app.third_api import views


third_blue = Blueprint("third_api", __name__)
third_api = Api(third_blue)
third_api.add_resource(views.VerifyIdCardView, '/api/verify_idcard/')
third_api.add_resource(views.SendSmsView, '/api/verify_code/')
