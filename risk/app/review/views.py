# -*- coding: utf-8 -*-
import json
import logging

import datetime
from flask import g, current_app, request
from sqlalchemy.orm import scoped_session

from app import Session
from app.core.logger import trace_view
from app.bases import BaseResource
from app.core.functions import make_response
from app.constants import Code, ApproveStatus, Status, ReceiveType
from app.databases import session_scope
from app.review import parsers
from .parsers import (
    lock_parser, first_review, second_review, third_review
)
from .managers import ReviewManager
from app.loan.managers import LoanManager
from app.constants import ViewLogTemp, InputApplyStatus
from app.review.parsers import review_log_parse
from app.models.sqlas import ReviewLog, InputApply, NewReviewLog
from app.core.managers import SyncManager
from app.user.function import current_user, login_required


class CheckLockView(BaseResource):

    @login_required
    def get(self):
        """判断是否被锁"""

        req = lock_parser.parse_args()
        search_id = req['id']

        session = scoped_session(Session)
        review_manager = ReviewManager(session)
        res = review_manager.check_is_locked(search_id, current_user)
        session.remove()
        if isinstance(res, int):
            return make_response(status=res)

        return make_response(res)


class AddLockView(BaseResource):

    @login_required
    def get(self, *args, **kwargs):
        """给审核加锁"""

        req = lock_parser.parse_args()
        search_id = req['id']

        session = scoped_session(Session)
        review_manager = ReviewManager(session)
        status = review_manager.add_lock(search_id, current_user)
        session.remove()

        return make_response(status=status)


@trace_view
class FirstApproveView(BaseResource):

    @login_required
    def post(self):
        """初审"""

        req = first_review.parse_args()
        search_id = req['id']

        next_status = None

        session = scoped_session(Session)
        review_manager = ReviewManager(session)
        result = review_manager.review(search_id, current_user, 1, req.copy())
        if isinstance(result, tuple):
            status, next_status = result
        else:
            status = result
        if status != Code.SUCCESS:
            review_manager.session.rollback()
            review_manager.session.remove()
            return make_response(status=status)

        try:
            review_manager.session.commit()
        except Exception as e:
            logging.error(e)
            review_manager.session.rollback()
            review_manager.session.remove()
            return make_response(status=Code.SYSTEM_ERROR)

        SyncManager.credit_approve_status(search_id, next_status)

        session.remove()
        return make_response(status=status)


@trace_view
class SecondApproveView(BaseResource):

    @login_required
    def post(self):
        """复审"""

        req = second_review.parse_args()
        search_id = req['id']

        next_status = None

        session = scoped_session(Session)
        review_manager = ReviewManager(session)
        result = review_manager.review(search_id, current_user, 2, req.copy())
        if isinstance(result, tuple):
            status, next_status = result
        else:
            status = result
        if status != Code.SUCCESS:
            review_manager.session.rollback()
            review_manager.session.remove()
            return make_response(status=status)

        try:
            review_manager.session.commit()
        except Exception as e:
            logging.error(e)
            review_manager.session.rollback()
            review_manager.session.remove()
            return make_response(status=Code.SYSTEM_ERROR)

        SyncManager.credit_approve_status(search_id, next_status)
        session.remove()
        return make_response(status=status)


@trace_view
class ThirdApproveView(BaseResource):

    @login_required
    def post(self):
        """终审"""

        req = third_review.parse_args()
        search_id = req['id']
        isFinalPass = req['isFinalPass']

        next_status = None

        session = scoped_session(Session)
        review_manager = ReviewManager(session)
        result = review_manager.review(search_id, current_user, 3, req.copy(), isFinalPass)
        if isinstance(result, tuple):
            status, next_status = result
        else:
            status = result
        if status != Code.SUCCESS:
            review_manager.session.rollback()
            review_manager.session.remove()
            return make_response(status=status)

        # input_apply = g.session.query(InputApply).get(search_id)

        # 被拒绝了请求就结束了
        if isFinalPass not in [1, "1"]:
            # input_apply.approve_status = ApproveStatus.DENY
            # input_apply.status = Status.APPROVEDENIED
            # g.session.add(input_apply)
            try:
                review_manager.session.commit()
            except Exception as e:
                review_manager.session.rollback()
                current_app.logger.error(e)
                return make_response(status=Code.SYSTEM_ERROR)
            finally:
                review_manager.session.remove()

            SyncManager.credit_approve_status(search_id, next_status, review_manager.now)
            return make_response()

        # 通过的话就要加入贷后监控和生成合同

        # input_apply.approve_status = ApproveStatus.PASS
        # input_apply.status = Status.WAITMERCH
        # g.session.add(input_apply)
        loan_manager = LoanManager(review_manager.session)
        status = loan_manager.add_loan(review_manager.review_instance, current_user, request)

        if status != Code.SUCCESS:
            loan_manager.session.rollback()
            loan_manager.session.remove()
        else:
            try:
                loan_manager.session.commit()
            except Exception as e:
                loan_manager.session.rollback()
                current_app.logger.error(e)
                return make_response(status=Code.SYSTEM_ERROR)
            finally:
                loan_manager.session.remove()

        SyncManager.credit_approve_status(search_id, next_status, review_manager.now)
        return make_response(status=status)


class ReviewLogView(BaseResource):
    """
    获取审核日志
    url: /api/approve_log/
    """
    @login_required
    def get(self):

        req = review_log_parse.parse_args(strict=True)
        session = scoped_session(Session)
        history_list = session.query(ReviewLog).filter_by(input_apply_id=req['id']).order_by(ReviewLog.create_time.desc())
        if not history_list:
            session.remove()
            return make_response(data={"approveList": []})

        data, tmp_list = [], []

        for history in history_list:
            if history.user_id:
                username = history.user.username
            else:
                username = "系统"
            t_n = history.template_number
            if t_n != -1 and t_n not in tmp_list:
                tmp_list.append(t_n)
                data.append({
                    "content": ViewLogTemp.TEMPLATE[t_n],
                    "time": history.create_time,
                    'user': username,
                })
        session.remove()
        return make_response(data={"approveList": data})


class ReviewContentView(BaseResource):
    """
    获取某个阶段的审核内容
    /api/check_content/
    """
    @login_required
    def get(self):
        from app.databases import session_scope
        from app.review.parsers import review_content
        import json

        req = review_content.parse_args(strict=True)
        result = None
        session = scoped_session(Session)
        with session_scope(session) as session:
            obj = session.query(InputApply).get(req['id'])
            if not obj:
                return make_response(status=Code.SEARCH_NOT_EXIST)
            if req['stage'] == 1:
                result = json.loads(obj.first_view) if obj.first_view else {}
            elif req['stage'] == 2:
                result = json.loads(obj.second_view) if obj.second_view else {}
            elif req['stage'] == 3:
                result = json.loads(obj.third_view) if obj.third_view else {}
        return make_response(data=result)


class SaveApproveView(BaseResource):
    """
    v2.2起保存审核内容
    /api/save_approve
    """

    @login_required
    def post(self):

        req = parsers.save_approve_parser.parse_args(strict=True)

        input_apply_id = req["id"]
        content = req["content"]
        status = req["status"]
        next_status = ApproveStatus.PASS if status else ApproveStatus.DENY

        now = datetime.datetime.now()

        session = scoped_session(Session)
        input_apply = session.query(InputApply).get(input_apply_id)
        if not input_apply:
            return make_response(status=Code.SEARCH_NOT_EXIST)

        log = NewReviewLog(
            input_apply_id=input_apply_id,
            user_id=current_user.id,
            create_time=now,
            params=json.dumps(content),
        )
        if status == 0:
            input_apply.approve_status = ApproveStatus.DENY
            input_apply.status = Status.APPROVEDENIED

        else:
            input_apply.approve_status = ApproveStatus.PASS
            loan_manager = LoanManager(session)
            resp = loan_manager.add_loan(input_apply)
            if resp != Code.SUCCESS:
                session.rollback()
                session.remove()
                return make_response(status=resp)

        session.add(log)
        session.add(input_apply)
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            logging.exception(e)
            return make_response(status=Code.SYSTEM_ERROR)

        SyncManager.credit_approve_status(input_apply_id, next_status, now)

        return make_response()


class GetApproveView(BaseResource):
    """
    v2.2起获取审核内容
    /api/get_approve
    """

    @login_required
    def get(self):

        req = parsers.get_approve_parser.parse_args(strict=True)

        input_apply_id = req["id"]

        session = scoped_session(Session)
        with session_scope(session) as session:
            log = session.query(NewReviewLog).filter(NewReviewLog.input_apply_id == input_apply_id).one_or_none()

            if not log:
                return make_response(data={
                    "content": "",
                    "approveTime": -1,
                    "username": "",
                })

            try:
                content = json.loads(log.params)
            except:
                content = {}

            data = {
                "content": content,
                "approveTime": log.create_time,
                "username": log.username if log.username else "",
            }

        return make_response(data=data)
