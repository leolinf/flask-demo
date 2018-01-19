# -*- coding: utf-8 -*-

from flask import Blueprint
from flask_restful import Api

from . import views


loan = Blueprint('loan', __name__)
loan_wrap = Api(loan)


loan_wrap.add_resource(views.LoanListView, '/api/loan/list/')
loan_wrap.add_resource(views.LoanDetailView, '/api/loan/detail/')
