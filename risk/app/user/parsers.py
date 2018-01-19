# -*- coding: utf-8 -*-
from flask_restful import reqparse, inputs


user_login_parse = reqparse.RequestParser(bundle_errors=True)
user_login_parse.add_argument('userName', type=str, required=True)
user_login_parse.add_argument('pwd', type=str, required=True)
user_login_parse.add_argument('userId', location='args', type=int)

module_parser = reqparse.RequestParser(bundle_errors=True)
module_parser.add_argument('id', type=str)
module_parser.add_argument('token', type=str)
module_parser.add_argument('userId', location='args', type=int)

pwd_parser = reqparse.RequestParser(bundle_errors=True)
pwd_parser.add_argument("newPwd", type=str, required=True)
pwd_parser.add_argument("oldPwd", type=str, required=True)
pwd_parser.add_argument("userName", type=str, required=True)
pwd_parser.add_argument('userId', location='args', type=int)
