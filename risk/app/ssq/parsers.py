# -*- coding: utf-8 -*-

from flask_restful import reqparse


contract_parser = reqparse.RequestParser(bundle_errors=True)
contract_parser.add_argument('id', location='args', type=str, required=True)
contract_parser.add_argument('userId', location='args', type=int)

contract_callback = reqparse.RequestParser(bundle_errors=True)
contract_callback.add_argument('code', location='json', type=str)
contract_callback.add_argument('signID', location='json', type=str)
contract_callback.add_argument('userId', location='args', type=int)

contract_sign = reqparse.RequestParser(bundle_errors=True)
contract_sign.add_argument('userId', location='args', type=int)
contract_sign.add_argument('id', location='json', type=str, required=True)
contract_sign.add_argument('callback', location='json', type=str, required=True)
