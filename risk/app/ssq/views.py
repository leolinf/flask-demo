# -*- coding: utf-8 -*-
import logging

from flask import redirect, g
from flask_login import current_user
from sqlalchemy.orm import scoped_session

from app.core.utils import short_url
from ..bases import BaseView
from ..databases import Session
from ..core.functions import make_response
from ..constants import Code
from .parsers import contract_parser, contract_callback, contract_sign
from .managers import BestsignManager
from app.core.logger import trace_view, class_logger


class ContractPreview(BaseView):

    def get(self):
        """合同预览"""

        req = contract_parser.parse_args()
        sign_id = req['id']
        session = scoped_session(Session)

        bestsign_manager = BestsignManager(session)

        res = bestsign_manager.preview_contract(sign_id)
        session.remove()
        if res == 'not exists':
            return make_response(status=Code.LOAN_NOT_EXIST)

        return make_response({"url": res})


class ContractSign(BaseView):

    def get(self):
        """合同签署"""

        req = contract_parser.parse_args()
        input_apply_id = req['id']
        session = scoped_session(Session)

        bestsign_manager = BestsignManager(session)

        res = bestsign_manager.sign_contract(input_apply_id)

        if res == 'not exists':
            return make_response(status=Code.LOAN_NOT_EXIST)

        try:
            bestsign_manager.session.commit()
        except Exception as e:
            logging.error(e)
            bestsign_manager.session.rollback()
            session.remove()
            return make_response(status=Code.SYSTEM_ERROR)

        session.remove()

        return make_response({"url": res})


class ContractDownload(BaseView):

    def get(self):
        """合同下载"""

        req = contract_parser.parse_args()
        sign_id = req['id']
        session = scoped_session(Session)

        bestsign_manager = BestsignManager(session)

        res = bestsign_manager.downloan_contract(sign_id)
        session.remove()

        if res == 'not exists':
            return make_response(status=Code.LOAN_NOT_EXIST)

        return make_response({"url": res})


@trace_view
@class_logger
class ContractCallback(BaseView):

    def post(self):
        """合同签署玩回调"""

        req = contract_callback.parse_args()

        signid = req['signID']
        code = req['code']

        session = scoped_session(Session)

        bestsign_manager = BestsignManager(session)

        res = bestsign_manager.close_contract(signid, code)

        if res == 'not exists':
            session.remove()
            return make_response(status=Code.LOAN_NOT_EXIST)

        try:
            bestsign_manager.session.commit()
        except Exception as e:
            logging.error(e)
            bestsign_manager.session.rollback()
            return make_response(status=Code.SYSTEM_ERROR)
        finally:
            bestsign_manager.session.remove()

        return make_response()


@trace_view
@class_logger
class ContractGetUrl(BaseView):

    def post(self):
        """签署合同的接口，接收参数id为订单id"""

        req = contract_sign.parse_args()

        input_apply_id = req['id']
        callback = req['callback']

        session = scoped_session(Session)
        bestsign_manager = BestsignManager(session)
        try:
            res = bestsign_manager.for_java_to_sign_contract(input_apply_id, callback)
        except Exception as e:
            logging.exception(e)
            bestsign_manager.session.rollback()
            session.remove()
            return make_response(status=Code.SIGN_OVER_TIME)

        if res == 'not exists':
            session.remove()
            return make_response(status=Code.LOAN_NOT_EXIST)

        if res == 'no sign':
            session.remove()
            return make_response(status=Code.SYSTEM_ERROR)

        res = short_url(res)
        try:
            bestsign_manager.session.commit()
        except Exception as e:
            logging.error(e)
            bestsign_manager.session.rollback()
            session.remove()
            return make_response(status=Code.SYSTEM_ERROR)

        session.remove()
        return make_response(data={"signUrl": res})
