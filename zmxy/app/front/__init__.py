from flask import Blueprint
from flask_restful import Api

from app.front.views import IndexView


front = Blueprint("front", __name__)
front.add_url_rule("/", view_func=IndexView.as_view("index"))
front.add_url_rule("/auth_form_data/", view_func=IndexView.as_view("data"))
front.add_url_rule("/auth_data_detail/", view_func=IndexView.as_view("detail"))
