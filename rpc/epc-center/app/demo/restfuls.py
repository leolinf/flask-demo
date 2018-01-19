# -*- coding = utf-8 -*-

from flask_restful import Resource
from flask import jsonify


class DemoResource(Resource):

    def get(self):
        import time
        time.sleep(6)

        return jsonify({"code": 10000})
