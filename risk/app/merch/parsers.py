# -*- encoding: utf-8 -*-

from flask_restful import reqparse
from werkzeug.datastructures import FileStorage

from .validators import baseinfo_validator, applytable_validator

merch_add = reqparse.RequestParser(bundle_errors=True)
merch_add.add_argument('baseInfo', location='json', type=dict, required=True)
merch_add.add_argument('id', location='json', type=str)
merch_add.add_argument('applyTable', location='json', type=list)
merch_add.add_argument('userId', location='args', type=int)

upload_parser = reqparse.RequestParser(bundle_errors=True)
upload_parser.add_argument('attachment', location='files', type=FileStorage)
upload_parser.add_argument('type', location='form', type=int)
upload_parser.add_argument('userId', location='args', type=int)

merchant_list_parser = reqparse.RequestParser(bundle_errors=True)
merchant_list_parser.add_argument('count', location='args', type=int, default=10)
merchant_list_parser.add_argument('page', location='args', type=int, default=1)
merchant_list_parser.add_argument('merchantName', location='args', type=str)
merchant_list_parser.add_argument('signSort', location='args', type=int, choices=(1, 2, 3))
merchant_list_parser.add_argument('userId', location='args', type=int)

merchant_detail_parser = reqparse.RequestParser(bundle_errors=True)
merchant_detail_parser.add_argument('id', location='args', type=str, required=True)
merchant_detail_parser.add_argument('time', location='args', type=str)
merchant_detail_parser.add_argument('userId', location='args', type=int)

merchant_file_parser = reqparse.RequestParser(bundle_errors=True)
merchant_file_parser.add_argument('id', location='args', type=str, required=True)
merchant_file_parser.add_argument('userId', location='args', type=int)

merchant_status_parser = reqparse.RequestParser(bundle_errors=True)
merchant_status_parser.add_argument('id', location='json', type=str, required=True)
merchant_status_parser.add_argument('status', location='json', type=int, required=True, choices=(1, 0))
merchant_status_parser.add_argument('userId', location='args', type=int)
