# -*- coding: utf-8 -*-

from flask_restful import reqparse


loan_list = reqparse.RequestParser(bundle_errors=True)
loan_list.add_argument('count', location='json', type=int, default=10)
loan_list.add_argument('page', location='json', type=int, default=1)
loan_list.add_argument('searchNum', location='json', type=str)
loan_list.add_argument('merchantName', location='json', type=int)
loan_list.add_argument('loanSort', location='json', type=int, )
loan_list.add_argument('loanStatus', location='json', type=int, default=-1)
loan_list.add_argument('userId', location='args', type=int)

loan_detail = reqparse.RequestParser(bundle_errors=True)
loan_detail.add_argument('id', location='args', type=int, required=True)
loan_detail.add_argument('userId', location='args', type=int)

change_loan = reqparse.RequestParser(bundle_errors=True)
change_loan.add_argument('id', location='json', required=True, type=int)
change_loan.add_argument('loanStatus', location='json', type=int, required=True, choices=(1, 0))
change_loan.add_argument('userId', location='args', type=int)
