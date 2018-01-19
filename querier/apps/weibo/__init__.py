from flask import Blueprint


weibo = Blueprint('weibo', __name__)


from . import urls
