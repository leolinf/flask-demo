# -*- coding = utf-8 -*-

from flask_restful import reqparse

from app.common.constant import Params


base_parser_get = reqparse.RequestParser()
base_parser_get.add_argument(Params.SIGN, location="args", required=True, type=str)
base_parser_get.add_argument(Params.TIMESTAMP, location="args", required=True, type=float)
base_parser_get.add_argument(Params.APPKEY, location="args", required=True, type=str)

base_parser_post = reqparse.RequestParser()
base_parser_post.add_argument(Params.SIGN, location="json", required=True, type=str)
base_parser_post.add_argument(Params.TIMESTAMP, location="json", required=True, type=float)
base_parser_post.add_argument(Params.APPKEY, location="json", required=True, type=str)
