# -*- coding: utf-8 -*-


from flask import Blueprint
from flask_restful import Api

from app.zmxy import views


zmxy = Blueprint("zmxy", __name__)
zmxy.add_url_rule("/auth", view_func=views.AuthView.as_view("auth"))
zmxy.add_url_rule("/api/getData/", view_func=views.GetDataView.as_view("getdata"))
