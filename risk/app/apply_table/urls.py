# -*- coding: utf-8 -*-


from flask import Blueprint
from flask_restful import Api

from app.apply_table import views


apply_blue = Blueprint('apply_table', __name__)
apply_api = Api(apply_blue)

apply_api.add_resource(views.AddApplyTable, '/api/post_application/')
apply_api.add_resource(views.GetApplyListView, "/api/application_list/")
apply_api.add_resource(views.GetDefaultConfig, "/api/application_config/")
apply_api.add_resource(views.GetRecomdmendView, "/api/recommend_application/")
apply_api.add_resource(views.GetApplyTableDetailView, "/api/application/")
apply_api.add_resource(views.CustomConfigView, "/api/custom_config/")
