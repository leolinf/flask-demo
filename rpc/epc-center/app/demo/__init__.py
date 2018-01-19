# -*- coding = utf-8 -*-

from flask_restful import Api
from flask import Blueprint

from . import restfuls


demo = Blueprint('demo', __name__)
demo_api = Api(demo)


demo_api.add_resource(restfuls.DemoResource, '/demo')
