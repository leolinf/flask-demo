from flask import Blueprint
from flask_restful import Api

from app.front.views import IndexView


front = Blueprint("front", __name__)
front.add_url_rule("/", view_func=IndexView.as_view("index"))