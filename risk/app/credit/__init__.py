# -*- coding: utf-8 -*-

from flask import Blueprint
from flask_restful import Api

from .views import (
    TelConsumeView, EnterpriseView, SearchResultView,
    CreditListView, OperatorView, MsgRcoredView,
    CallRcoredView, ContactAreaView,
    ConfirmView, RiskEvaluationView,
    InputApplyShowView, CapchaToken,
    TokenStatusView, AddressVerifyView,
    AddressSaveView, PdfDownlaodView,
    JavaView, SocialToken, FundToken, BankToken,
    SocialResultView, PublicFundResultView,
    BankReportView, TaobaoView, TaobaoReportView,
    BreakRuleView)


credit = Blueprint('credit', __name__)
credit_wrap = Api(credit)

credit_wrap.add_resource(CreditListView, '/api/search_list/')

credit_wrap.add_resource(TelConsumeView, '/api/credit/consume/')
# credit_wrap.add_resource(EnterpriseView, '/api/credit/enterprise/')
credit_wrap.add_resource(OperatorView, '/api/credit/operator/base/')
credit_wrap.add_resource(MsgRcoredView, '/api/credit/operator/msg/')
credit_wrap.add_resource(CallRcoredView, '/api/credit/operator/call/')
# credit_wrap.add_resource(ContactAreaView, '/api/credit/operator/area/')
credit_wrap.add_resource(SearchResultView, '/api/credit/search_result/', endpoint='credit_detail')
credit_wrap.add_resource(ConfirmView, "/api/credit/query/") # 进件查询
credit_wrap.add_resource(RiskEvaluationView, "/api/risk_evaluation/")
credit_wrap.add_resource(InputApplyShowView, "/api/Into_pieces/")
credit_wrap.add_resource(TokenStatusView, "/api/capcha/operator_status/")
credit_wrap.add_resource(AddressVerifyView, "/api/credit/address_check/")
credit_wrap.add_resource(AddressSaveView, "/api/credit/address_save/")
credit_wrap.add_resource(PdfDownlaodView, "/api/presentation_pdf/")
credit_wrap.add_resource(JavaView, "/api/basic", endpoint='java_basic')
credit_wrap.add_resource(JavaView, "/api/search", endpoint='java_search')
credit_wrap.add_resource(JavaView, "/api/area_selector", endpoint='java_area_selector')
credit_wrap.add_resource(JavaView, "/api/confirm_task", endpoint='confirm_task')

# 运营商魔蝎回调接口
credit_wrap.add_resource(CapchaToken, '/api/capcha/token/')
# 社保魔蝎回调接口
credit_wrap.add_resource(SocialToken, '/api/social/token/')
# 公积金回调接口
credit_wrap.add_resource(FundToken, "/api/fund/token/")
# 人行回调接口
credit_wrap.add_resource(BankToken, "/api/bankreport/token/")
# 淘宝授权回调接口
credit_wrap.add_resource(TaobaoView, "/api/taobaoreport/token/")

# 社保前端调用
credit_wrap.add_resource(SocialResultView, '/api/credit/social/')
# 公积金前端调用
credit_wrap.add_resource(PublicFundResultView, "/api/credit/fund/")
# 人行前端调用
credit_wrap.add_resource(BankReportView, "/api/credit/bankreport/")
# 淘宝调用
credit_wrap.add_resource(TaobaoReportView, "/api/credit/taobaoreport/")

#credit_wrap.add_resource(InputApplyShowView, "/apitest/Into_pieces/")
#credit_wrap.add_resource(CreditBlock, '/api/credit/block/')
#credit_wrap.add_resource(FirstReview, '/api/first_examine/')
#credit_wrap.add_resource(SecondReview, '/api/re_examine/')
#credit_wrap.add_resource(ThirdReview, '/api/last_examine/')

# 系统自动校验
credit_wrap.add_resource(BreakRuleView, "/api/system_check")
