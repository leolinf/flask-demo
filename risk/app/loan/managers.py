# -*- coding: utf-8 -*-

import json
import logging

import requests
from sqlalchemy import and_, or_
from flask import request, url_for

from ..models import (
    InputApply, BestsignContract,
    SmsTemplate, LoanPayHistory, Merchant,
    LoanRepayPlan, InputApplyUpload, MerchantGoods)
from ..constants import Code, ServiceType, InputApplyStatus, LoanStatus, Status, ReceiveType
from ..ssq.managers import BestsignManager
from ..config import Config
from ..core.utils import short_url
from app.credit.utils import check_whether_self
from app.user.function import current_user


class LoanManager(object):
    def __init__(self, session):

        self.session = session

    def _check_contract(self, current_user):
        """判断是否有上上签合同业务"""

        company = current_user.company
        return company.if_online_sign_contract

    @staticmethod
    def ask_java_to_sign(input_apply_id):
        """调用java接口去签合同"""

        url = "{0}/api/orderCheckPy?orderNum={1}&status=1&sigin=zjektnxhsamzyqirsmzj24".format(
            Config.JAVA_MERCHANT, input_apply_id)

        try:
            resp = requests.get(url, timeout=10)
            resp_json = resp.json()
            logging.info("ask_java_to_sign, json:{0}".format(resp_json))
        except Exception as e:
            logging.error("ask_java_to_sign, error:{0}".format(e))
            return Code.SYSTEM_ERROR

        if resp_json.get("code") in [10000, 50014, 50004]:
            return Code.SUCCESS
        else:
            return Code.SYSTEM_ERROR

    def add_loan(self, review, current_user=None, request=request):
        """加入借款管理"""

        input_apply = review

        ##############################
        if input_apply.company.if_online_sign_contract:
            input_apply.status = Status.WAITSIGN
            resp = self.ask_java_to_sign(input_apply.id)

            if resp != Code.SUCCESS:
                return resp

        elif input_apply.merchant.product.recieve_type in [ReceiveType.CLIENT, ReceiveType.BANDANYUAN]:
            input_apply.status = Status.WAITMERCH

        else:
            input_apply.status = Status.WAITLOAN

        self.session.add(input_apply)

        return Code.SUCCESS

    def get_list(self, company_id, offset=0, limit=10, searchNum=None, timeSort=None, status=None, merchantName=None):
        """获取借款列表"""

        ##########
        # 筛选
        ##########

        available_status = [Status.WAITSIGN, Status.WAITLOAN, Status.ENDLOAN, Status.LOANDENIED, Status.LOANSUCCESS,
                            Status.LOANFAILED, Status.WAITMERCH, Status.MERCHDENIED, Status.LOANING,
                            Status.WAITUPLOADPIC, Status.ENDUPLOADPIC]

        loan_status = [LoanStatus.DONE, LoanStatus.OVERDUE, LoanStatus.REFUNDING]

        match = (
            InputApply.company_id == company_id,
            InputApply.status.in_(available_status),
        )

        # 筛选手机号或身份证
        if searchNum:
            match += (or_(
                InputApply.phone.like('%{0}%'.format(searchNum)),
                InputApply.idcard.like('%{0}%'.format(searchNum)),
                InputApply.id.like('%{0}%'.format(searchNum)),
                InputApply.name.like('%{0}%'.format(searchNum)),
                Merchant.name.like('%{0}%'.format(searchNum)),
            ),)

        if status in loan_status:
            match += (
                InputApply.loan_status == status,
            )
        elif status in available_status:
            match += (
                InputApply.status == status,
            )

        if merchantName:
            match += (
                Merchant.id == merchantName,
            )

        ##########
        # 排序
        ##########

        order = ()

        if timeSort == 1:
            order += (InputApply.create_time,)
        elif timeSort == 2:
            order += (InputApply.create_time.desc(),)
        else:
            order += (InputApply.create_time,)

        triples = self.session.query(InputApply, LoanPayHistory, Merchant) \
            .outerjoin(LoanPayHistory, InputApply.id == LoanPayHistory.input_apply_id) \
            .outerjoin(Merchant, InputApply.merchant_id == Merchant.id) \
            .filter(and_(*match)).order_by(*order)
        total = triples.count()
        triples = triples.offset(offset).limit(limit).all()

        def _detail(triple):
            loan, history, merchant = triple
            res = {
                'id': str(loan.id),
                'idCard': loan.idcard if loan.idcard else '--',
                'intoNumber': str(loan.id),
                'intoTime': loan.create_time,
                'loanNumber': loan.loan_money,
                'loanStatus': loan.status,
                'name': loan.name,
                'telphone': loan.phone,
                'accountMoney': history.account_money if history else "",
                'valueDate': history.value_date if history else "",
                'merchantName': merchant.name if merchant else "",
                "instalments": loan.instalments,
            }
            return res

        return list(map(_detail, triples)), total

    def get_detail(self, loan_id):
        """获取借款详情"""

        loan = self.session.query(InputApply, LoanRepayPlan, LoanPayHistory, InputApplyUpload, MerchantGoods).outerjoin(
            LoanRepayPlan, InputApply.id == LoanRepayPlan.input_apply_id).outerjoin(
            LoanPayHistory, InputApply.id == LoanPayHistory.input_apply_id).outerjoin(
            InputApplyUpload, InputApply.id == InputApplyUpload.input_apply_id).outerjoin(
            MerchantGoods, InputApply.interest_id == MerchantGoods.id).filter(
            InputApply.id == loan_id).all()
        if not loan:
            return 'not exists'

        loan, plan, history, upload, goods = loan[0]

        if not check_whether_self(loan):
            return 'not allowed'

        bestsign_contract = loan.bestsign_contract

        if upload:
            try:
                img_list = json.loads(upload.photo_url)
            except:
                logging.error("保存的photo_url是\t{0}".format(upload.photo_url))
                img_list = []

            photo_num = upload.serial_number

        else:
            img_list = []
            photo_num = ""

        if goods:
            describes = goods.describes
        else:
            describes = ""

        res = {
            'applyMoneys': loan.loan_money if loan.loan_money else '0',
            'idCard': loan.idcard,
            'instalments': loan.instalments,
            'intoNumber': str(loan.id),
            'name': loan.name,
            'product': loan.product_name,
            'repayNumber': loan.each_month_repay if loan.each_month_repay else '0',
            'signId': bestsign_contract.signid if bestsign_contract else '',
            "status": loan.status,
            'telphone': loan.phone,
            "bankNum": loan.bank_num,
            "merchantName": loan.merchant.name,
            "repayMethod": loan.merchant.product.repay_type,
            "intoTime": loan.apply_time,
            "repayPerMonth": loan.each_month_repay,
            "loanTime": history.value_date if history else "",
            "phoneNum": photo_num,
            "imgList": img_list,
            "describes": describes,
        }

        return res
