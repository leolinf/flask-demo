# -*- coding = utf-8 -*-

from flask_restful import Resource

from app.api import parser
from app.api.service import ServiceProxy
from app.common.auth import auth_required
from app.common.constant import Code
from app.common.helper import make_response, view_method_memoize


class CarStructureResource(Resource):

    @auth_required
    @view_method_memoize()
    def get(self):

        req = parser.car_structure_parser.parse_args(strict=True)

        service = ServiceProxy(req.copy())

        if service.invalid:
            return make_response(code=Code.SUCCESS_NOT_DATA)

        res = service.get_car_structure()

        if res is service.error:
            return make_response(code=Code.SERVERS_ERROR)

        if res is service.result_invalid:
            return make_response(code=Code.SUCCESS_NOT_DATA)

        return make_response(data=res)
