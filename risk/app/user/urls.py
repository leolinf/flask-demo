# -*- coding: utf-8 -*-

from flask import Blueprint
from flask_restful import Api

from app.user import views


user_blue = Blueprint('user', __name__)
user_api = Api(user_blue)


user_api.add_resource(views.UserLoginView, '/api/sign_in/')
user_api.add_resource(views.LoginOutView, "/api/sign_out/")
user_api.add_resource(views.CompanyInfoView, '/api/company_infor/')
user_api.add_resource(views.CompanyModuleList, '/api/company/module_list/')
user_api.add_resource(views.SwitchList, '/api/company/switch_list/')
# user_api.add_resource(views.ChangePwd, '/api/change_pwd/')
user_api.add_resource(views.CheckHealth, "/checkhealth")
