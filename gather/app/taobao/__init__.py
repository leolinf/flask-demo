# -*- coding: utf-8 -*-


from flask import Blueprint
from flask_restful import Api

from app.taobao import views


taobao = Blueprint("taobao", __name__)
taobao.add_url_rule("/tbauth/", view_func=views.TaobaoAuthView.as_view("tbauth"))
taobao.add_url_rule("/tblogin/", view_func=views.TaobaoLoginView.as_view("tblogin"))
taobao.add_url_rule("/tbresult/", view_func=views.TaobaoResultView.as_view("tbresult"))
taobao.add_url_rule("/tbcrawler/", view_func=views.TaobaoAuthCrawlerView.as_view("tbcrawler"))

# merch_api = Api(taobao)
# merch_api.add_resource(views.TaobaoAuthView, '/tbauth/')
# merch_api.add_resource(views.TaobaoLoginView, '/tblogin/')
# merch_api.add_resource(views.TaobaoResultView, '/tbresult/')
# merch_api.add_resource(views.TaobaoAuthCrawlerView, '/tbcrawler/')