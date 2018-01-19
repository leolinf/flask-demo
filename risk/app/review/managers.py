# -*- coding: utf-8 -*-

import datetime

from ..models import InputApply
from ..constants import ApproveStatus, Code, ViewStatus, ViewLogTemp, InputApplyStatus, Status, LocalState
from ..config import Config
from ..databases import session_scope
import json
from ..models.sqlas import ReviewLog
from app.credit.utils import check_whether_self


class ReviewManager(object):

    def __init__(self, session, *args, **kwargs):

        self.session = session
        self.now = datetime.datetime.now()
        self.review_instance = None

    def _get_status_after_review(self, previous_status, steps, is_pass=False):
        """获取审批之后的状态"""

        if steps == 1 and previous_status in [ApproveStatus.FIRST_DOING, None]:
            status = ApproveStatus.SECOND_DOING
        elif steps == 2 and previous_status == ApproveStatus.SECOND_DOING:
            status = ApproveStatus.THIRD_DOING
        elif steps == 3 and previous_status == ApproveStatus.THIRD_DOING:
            status = ApproveStatus.PASS if is_pass else ApproveStatus.DENY
        else:
            status = previous_status

        return status

    def _get_status_after_locked(self, previous_status):
        """获取锁了之后的状态"""

        if previous_status in [ApproveStatus.WAITING, None]:
            status = ApproveStatus.FIRST_DOING
        elif previous_status == ApproveStatus.FIRST_DONE:
            status = ApproveStatus.SECOND_DOING
        elif previous_status == ApproveStatus.SECOND_DONE:
            status = ApproveStatus.THIRD_DOING
        else:
            status = previous_status

        return status

    def _record_view(self, review, steps, params, prestatus):
        """添加日志"""

        # 保存新的状态
        new_status = review.approve_status
        review.approve_status = prestatus

        operate_json = json.dumps(params)
        if steps == ViewStatus.VIEW_FIRST:
            review.first_view = operate_json
        elif steps == ViewStatus.VIEW_SECOND:
            review.second_view = operate_json
        elif steps == ViewStatus.VIEW_THIRD:
            review.third_view = operate_json

        tem_num = self.review_log_get_template_status(review, steps, params.get("isFinalPass", None))
        review.approve_status = new_status

        if tem_num == -3 or tem_num == -2:
            review.third_view = ""

        current_user = review.lock_user

        if tem_num == -2:
            view_log_obj = ReviewLog(
                params="",
                user_id=current_user.id,
                # username=current_user.username,
                create_time=self.now,
                input_apply_id=review.id,
                template_number=7
            )
        elif tem_num == -3:
            view_log_obj = ReviewLog(
                params="",
                user_id=current_user.id,
                # username=current_user.username,
                create_time=self.now,
                input_apply_id=review.id,
                template_number=5
            )
        else:
            view_log_obj = ReviewLog(
                params=operate_json,
                user_id=current_user.id,
                # username=current_user.username,
                create_time=self.now,
                input_apply_id=review.id,
                template_number=tem_num
            )

        if steps != 3:
            # with session_scope(self.session) as session:
                # session.add(review)
            self.session.add(view_log_obj)
        else:
            # self.session.add(review)
            self.session.add(view_log_obj)

    def check_is_locked(self, search_id, current_user):
        """给前端用的判断有没有锁"""

        now = self.now

        review = self.session.query(InputApply).get(search_id)
        if not review:
            return Code.SEARCH_NOT_EXIST

        if review.local_state == LocalState.WEB:
            lock = 1
            timeout = 0
            username = ''
        elif review.is_locked and review.lock_user_id == current_user.id:
            lock = 0
            username = current_user.username
            timeout = 0
        elif review.is_locked and review.lock_user_id != current_user.id:
            lock = 1
            timeout = 0
            username = review.lock_user.username
        elif not review.is_locked and review.lock_user_id == current_user.id and review.lock_time + datetime.timedelta(seconds=Config.LOCK_TIME) < now:
            lock = 0
            timeout = 1
            username = current_user.username

        elif not review.is_locked and review.lock_user_id == current_user.id and review.lock_time + datetime.timedelta(seconds=Config.LOCK_TIME) >= now:
            lock = 0
            timeout = 0
            username = current_user.username
        elif not review.is_locked and review.lock_user_id and review.lock_user_id != current_user.id:
            lock = 0
            timeout = 1
            username = review.lock_user.username
        else:
            lock = 0
            timeout = 0
            username = ''

        res = {
            'isBlocked': lock,
            'isTimeout': timeout,
            'status': review.approve_status,
            'username': username,
        }
        return res

    def add_lock(self, search_id, current_user):
        """加锁"""

        now = self.now

        credit = self.session.query(InputApply).get(search_id)
        if not credit:
            return Code.SEARCH_NOT_EXIST

        if not check_whether_self(credit):
            return Code.NOT_ALLOWED

        if credit.local_state == LocalState.WEB:
            return Code.NOT_ALLOWED

        next_status = self._get_status_after_locked(credit.approve_status)

        if not credit.is_locked or credit.lock_user_id == current_user.id:
            with session_scope(self.session) as session:
                credit.is_locked = 1
                credit.lock_time = now
                credit.lock_user_id = current_user.id
                credit.approve_status = next_status
                session.add(credit)

            return Code.SUCCESS
        else:
            return Code.UNABLE_LOCK

    def review(self, search_id, current_user, steps, params, is_pass=None):
        """
        审批
        :param steps: 审批步骤 1/2/3
        """

        now = self.now

        input_apply = self.session.query(InputApply).get(search_id)
        if not input_apply:
            return Code.SEARCH_NOT_EXIST

        if not check_whether_self(input_apply):
            return Code.NOT_ALLOWED

        if input_apply.local_state == 2:
            return Code.NOT_ALLOWED

        review = input_apply
        # 被别人锁了
        if review.is_locked and review.lock_user_id != current_user.id:
            return Code.ALREADY_LOCKED
        # 没有被锁
        elif not review.is_locked:
            return Code.NOT_LOCKED

        previous_status = review.approve_status
        next_status = self._get_status_after_review(previous_status, steps, is_pass)

        if steps == 3:
            review.is_locked = 0
        else:
            review.is_locked = 1

        review.lock_time = now
        review.lock_user_id = current_user.id
        review.approve_status = next_status
        review.approve_time = now
        review.approve_status = next_status
        review.approve_time = now
        self._record_view(review, steps, params, previous_status)

        if next_status == ApproveStatus.DENY:
            review.status = Status.APPROVEDENIED
            review.content = params.get("msg", "")
        if next_status == ApproveStatus.PASS:
            review.status = Status.WAITMERCH
            review.content = params.get("msg", "")

        self.session.add(review)
        self.review_instance = review

        return Code.SUCCESS, next_status

    def review_log_get_template_status(self, sea_obj, stage, pass__=None):

        ret = -1  # 表示最终的状态没有变
        if stage == ViewStatus.VIEW_BACK:
            if sea_obj.third_view:
                if json.loads(sea_obj.third_view).get('isFinalPass') == 1:
                    return -2
                else:
                    return -3
        elif stage == ViewStatus.VIEW_FIRST:
            if sea_obj.approve_status == ApproveStatus.FIRST_DOING:
                ret = 1  # 未初审 到 初审
        elif stage == ViewStatus.VIEW_SECOND:
            if sea_obj.approve_status == ApproveStatus.SECOND_DOING:
                ret = 2  # 已初审到 已复审
        elif stage == ViewStatus.VIEW_THIRD:
            if pass__ == 1 or pass__ == '1':
                if sea_obj.approve_status == ApproveStatus.THIRD_DOING:
                    ret = 3
            else:
                if sea_obj.approve_status == ApproveStatus.THIRD_DOING:
                    ret = 4

        return ret

    @staticmethod
    def get_status_after_unlock(previous_status):
        """获取解锁后的状态"""

        if previous_status == ApproveStatus.FIRST_DOING:
            status = ApproveStatus.WAITING
        elif previous_status == ApproveStatus.SECOND_DOING:
            status = ApproveStatus.FIRST_DONE
        elif previous_status == ApproveStatus.THIRD_DOING:
            status = ApproveStatus.SECOND_DONE
        else:
            status = previous_status

        return status
