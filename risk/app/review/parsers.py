# -*- coding: utf-8 -*-

from flask_restful import reqparse


lock_parser = reqparse.RequestParser()
lock_parser.add_argument('id', location='args', type=int, required=True)
lock_parser.add_argument('userId', location='args', type=int)

first_review = reqparse.RequestParser(bundle_errors=True)
first_review.add_argument('id', location='json', type=int, required=True)
first_review.add_argument('attachmentRealness', location='json', type=int, required=True, choices=(0, 1, 2, 3, 4))
first_review.add_argument('attachmentWholeness', location='json', type=int, required=True, choices=(0, 1, 2, 3, 4))
first_review.add_argument('commodityDownPayment', location='json', type=int, required=True, choices=(0, 1, 2, 3, 4))
first_review.add_argument('commodityPrice', location='json', type=int, required=True, choices=(0, 1, 2, 3, 4))
first_review.add_argument('companyBlackList', location='json', type=int, required=True, choices=(0, 1, 2, 3, 4))
first_review.add_argument('historyRecord', location='json', type=int, required=True, choices=(0, 1, 2, 3, 4))
first_review.add_argument('inRequest', location='json', type=int, required=True, choices=(0, 1, 2, 3, 4))
first_review.add_argument('phoneRelative', location='json', type=int, required=True, choices=(0, 1, 2, 3, 4))
first_review.add_argument('content', location='json', type=str)
first_review.add_argument('userId', location='args', type=int)

second_review = reqparse.RequestParser(bundle_errors=True)
second_review.add_argument('id', location='json', type=int, required=True)
second_review.add_argument('closeness', location='json', type=int, required=True, choices=(0, 1, 2, 3, 4))
second_review.add_argument('commodityInfo', location='json', type=int, required=True, choices=(0, 1, 2, 3, 4))
second_review.add_argument('companyRealness', location='json', type=int, required=True, choices=(0, 1, 2, 3, 4))
second_review.add_argument('emphasizeRepayment', location='json', type=int, required=True, choices=(0, 1, 2, 3, 4))
second_review.add_argument('familyInfo', location='json', type=int, required=True, choices=(0, 1, 2, 3, 4))
second_review.add_argument('identityInfo', location='json', type=int, required=True, choices=(0, 1, 2, 3, 4))
second_review.add_argument('isWorking', location='json', type=int, required=True, choices=(0, 1, 2, 3, 4))
second_review.add_argument('jobRealness', location='json', type=int, required=True, choices=(0, 1, 2, 3, 4))
second_review.add_argument('liveAddress', location='json', type=int, required=True, choices=(0, 1, 2, 3, 4))
second_review.add_argument('plasticSergeryHospital', location='json', type=int, required=True, choices=(0, 1, 2, 3, 4))
second_review.add_argument('relative', location='json', type=int, required=True, choices=(0, 1, 2, 3, 4))
second_review.add_argument('relativeRealness', location='json', type=int, required=True, choices=(0, 1, 2, 3, 4))
second_review.add_argument('workInfo', location='json', type=int, required=True, choices=(0, 1, 2, 3, 4))
second_review.add_argument('content', location='json', type=str)
second_review.add_argument('userId', location='args', type=int)


third_review = reqparse.RequestParser(bundle_errors=True)
third_review.add_argument('id', location='json', type=int, required=True)
third_review.add_argument('isFinalPass', location='json', type=int, required=True, choices=(1, 0))
third_review.add_argument('isLogic', location='json', type=int, required=True, choices=(1, 0))
third_review.add_argument('isPass', location='json', type=int, required=True, choices=(1, 0))
third_review.add_argument('isRepay', location='json', type=int, required=True, choices=(1, 0))
third_review.add_argument('content', location='json', type=str)
third_review.add_argument('msg', location='json', type=str)
third_review.add_argument('userId', location='args', type=int)


review_log_parse = reqparse.RequestParser(bundle_errors=True)
review_log_parse.add_argument('id', type=str, required=True)
review_log_parse.add_argument('userId', location='args', type=int)

# 获取详细审核内容
review_content = reqparse.RequestParser(bundle_errors=True)
review_content.add_argument('id', type=int, required=True)
review_content.add_argument('stage', type=int, required=True)
review_content.add_argument('userId', location='args', type=int)

# 保存审核内容
save_approve_parser = reqparse.RequestParser()
save_approve_parser.add_argument("id", type=int, required=True, location="json")
save_approve_parser.add_argument("content", type=dict, required=True, location="json")
save_approve_parser.add_argument("status", type=int, required=True, location="json", choices=(1, 0))
save_approve_parser.add_argument('userId', location='args', type=int)

# 获取审核内容
get_approve_parser = reqparse.RequestParser()
get_approve_parser.add_argument("id", type=int, required=True, location="args")
get_approve_parser.add_argument('userId', location='args', type=int)
