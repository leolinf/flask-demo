# -*- coding: utf-8 -*-

from flask import Blueprint
from flask_restful import Api

from .views import (
    ContractDownload, ContractSign, ContractPreview, ContractCallback, ContractGetUrl
)


ssq = Blueprint('ssq', __name__)
ssq_wrap = Api(ssq)


ssq.add_url_rule('/api/loan/contract/preview/', view_func=ContractPreview.as_view('contract_preview'))
ssq.add_url_rule('/api/loan/contract/sign/', view_func=ContractSign.as_view('contract_sign'))
ssq.add_url_rule('/api/loan/contract/down/', view_func=ContractDownload.as_view('contract_down'))
ssq.add_url_rule('/api/loan/contract/callback/', view_func=ContractCallback.as_view('contract_callback'))
ssq.add_url_rule('/api/loan/contract/get_url/', view_func=ContractGetUrl.as_view('contract_geturl'))
