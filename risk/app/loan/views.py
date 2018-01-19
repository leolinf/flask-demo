# -*- coding: utf-8 -*-

from flask import g
from sqlalchemy.orm import scoped_session

from app import Session
from ..bases import BaseResource
from ..core.functions import make_response
from ..constants import Code
from .parsers import loan_list, loan_detail
from .managers import LoanManager
from app.user.function import login_required, current_user


class LoanListView(BaseResource):

    @login_required
    def post(self):
        """借款管理列表"""

        req = loan_list.parse_args()
        page = req['page']
        count = req['count']
        timeSort = req['loanSort']
        searchNum = req['searchNum']
        status = req['loanStatus']
        merchantName = req["merchantName"]

        session = scoped_session(Session)
        loan_manager = LoanManager(session)

        loans, total = loan_manager.get_list(
            current_user.company_id,
            offset=(page - 1) * count,
            limit=count,
            searchNum=searchNum,
            status=status,
            timeSort=timeSort,
            merchantName=merchantName,
        )
        session.remove()

        return make_response(data={
            'loanList': loans,
            'total': total,
        })


class LoanDetailView(BaseResource):

    @login_required
    def get(self):
        """借款详情"""

        req = loan_detail.parse_args()

        loan_id = req['id']
        session = scoped_session(Session)
        loan_manager = LoanManager(session)

        res = loan_manager.get_detail(loan_id)
        session.remove()
        if res == 'not exists':
            return make_response(status=Code.LOAN_NOT_EXIST)
        if res == 'not allowed':
            return make_response(status=Code.NOT_ALLOWED)

        return make_response(res)
