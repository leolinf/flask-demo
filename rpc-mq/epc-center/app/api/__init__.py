# -*- coding = utf-8 -*-

from flask_restful import Api
from flask import Blueprint

from . import restfuls


api = Blueprint("api", __name__, url_prefix="/api")
api_api = Api(api)

api_api.add_resource(restfuls.CarStructureResource, "/get_car_structure")
