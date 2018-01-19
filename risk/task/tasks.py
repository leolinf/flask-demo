# -*- coding: utf-8 -*-

import datetime
import requests
import logging
import time

from celery import group
from celery.utils.log import get_task_logger
from sqlalchemy import and_
from sqlalchemy.orm import scoped_session

from app import celery
from app.models import Uploading, InputApply
from app.models.mongos import SingleSearch
from app.databases import session_scope, Session
from app.config import Config
from app.review.managers import ReviewManager
from app.constants import ApproveStatus, CreditUri, SearchStatus
from app.monitor.utils import single_monitor
from app.core.utils import send_tz, send_yzm
from app.core.functions import querystring
from app.credit.managers import RiskManager
from app.credit.handler import new_get_is_break

logger = get_task_logger(__name__)


@celery.task(bind=True)
def unlock_period(self):
    """定期解锁审批"""

    now = datetime.datetime.now()
    then = now - datetime.timedelta(seconds=Config.LOCK_TIME)

    with session_scope() as session:
        reviews = session.query(InputApply).filter(and_(
            InputApply.is_locked==True,
            InputApply.lock_time < then,
            InputApply.approve_status.in_([ApproveStatus.FIRST_DOING, ApproveStatus.SECOND_DOING, ApproveStatus.THIRD_DOING]),
        )).all()
        s = group([unlock_review.s(i.id) for i in reviews])
        s.apply_async(queue=Config.UNLOCK_QUEUE)


@celery.task(bind=True)
def unlock_review(self, review_id):
    """解锁某一审批"""

    logger.info('unlocking number: {0}'.format(review_id))

    try:
        with session_scope() as session:
            credit = session.query(InputApply).get(review_id)
            review = credit

            next_status = ReviewManager.get_status_after_unlock(review.approve_status)

            review.is_locked = 0
            review.approve_status = next_status
            session.add(review)
    except Exception as e:
        raise self.retry(exc=e)


@celery.task(name='single_credit')
def single_credit(search_id, company_id, *args, **kw):
    """ 查询报告 """
    from app.credit.utils import search_credit
    logger.info("credit: {} , query param is: {}".format(
        search_id, str(kw)))
    search_credit(search_id, company_id, *args, **kw)


@celery.task(bind=True)
def monitor_single(self, phone, name, id_num, monitor_id, is_batch=False):

    try:
        monitor = single_monitor(phone, name, id_num, monitor_id)
    except Exception as e:
        raise self.retry(exc=e)

    if is_batch:
        Uploading.objects(user_id=monitor.user_id, upload_type='B').update(
            inc__doing=-1,
            inc__success=1,
        )


@celery.task(bind=True)
def send_sign_url(self, content, mobile):
    """发送签署合同链接"""
    try:
        r = send_tz(Config.DDY_APIKEY, content, mobile, send_tz_uri=Config.DDY_TZURI, sms_host=Config.DDY_SMSHOST)
    except Exception as e:
        raise self.retry(exc=e, countdown=30)

    if r['code'] != 1:
        raise self.retry(exc=Exception(r['msg']), countdown=30)


@celery.task(bind=True)
def send_sms(self, mobile, code, template):
    """发送短信验证码"""

    logger.info('发送<<{0}>>到{1}'.format(template, mobile))

    try:
        r = send_yzm(Config.DDY_APIKEY, template, mobile, send_tz_uri=Config.DDY_YZMURI, sms_host=Config.DDY_SMSHOST)
    except Exception as e:
        raise self.retry(exc=e, countdown=30)

    if r['code'] != 1:
        raise self.retry(exc=Exception(r['msg']), countdown=30)


@celery.task(bind=True)
def capcha_info_token(self, apply_number, phone, token, auth_token):

    retry = False
    with session_scope() as session:
        input_apply = session.query(InputApply).get(apply_number)
        if input_apply.search_status != SearchStatus.DONE:
            retry = True
    if retry:
        raise self.retry(countdown=10, max_retries=12, exc=Exception('{0}信用报告还没有查询完'.format(apply_number)))
    index = 0
    response = {}
    url = querystring(CreditUri.MOJIEOPERATOR, {"token": token, "phone": phone, "auth_token": auth_token})
    while index <= 3:
        try:
            response = requests.get(url, timeout=20).json()
            break
        except Exception as e:
            time_now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            logging.warning('GET TOKEN DATA [TIME|%s] [URL|%s] [error|%s]', time_now, url, str(e))
            index += 1
            time.sleep(1)

    SingleSearch.objects(apply_number=apply_number).update(
        upsert=True,
        set__operator_data={"callback_operator": response},
        set__apply_number=apply_number,
    )

    search = SingleSearch.objects(apply_number=apply_number).first()
    score = search.mashang_score.get('result', {}).get('MC_CRESCO', {}).get('RUL_SUM')

    s = scoped_session(Session)
    with session_scope(s) as session:

        input_apply = session.query(InputApply).get(apply_number)
        risk_manager = RiskManager(session)
        is_break_rule = new_get_is_break(risk_manager.get_conclusion(apply_number))
        input_apply.is_break_rule = is_break_rule
        input_apply.operator = 2

        SingleSearch.objects(apply_number=apply_number).update(
            set__is_break_rule=is_break_rule,
        )

        # 马上评分所有信息都有才去伪造分
        if all([search.name, search.id_num, search.bank_num, search.phone]):
            score = risk_manager.modify_score(apply_number, score, phone)
            input_apply.score = score

        session.merge(input_apply)

    s = scoped_session(Session)
    with session_scope(s) as session:
        # 缓存
        from app.credit.forcache import cache_operator_view, cache_msg_record_view, cache_call_record_view, cache_token_status_view, cache_search_result_view, cache_address_verify_view

        cache_operator_view(session, {'id': apply_number})
        cache_msg_record_view(session, {'id': apply_number, 'page': 1, 'count': 10, 'isMark': 0, 'token': None})
        cache_call_record_view(session, {'id': apply_number, 'page': 1, 'count': 10, 'isMark': 0, 'token': None})
        cache_token_status_view(session, {'id': apply_number})
        cache_search_result_view(session, {'id': apply_number})
        cache_address_verify_view(session, {'id': apply_number})


@celery.task()
def social_info_token(apply_number, phone, token, auth_token):
    index = 0
    url = querystring(CreditUri.MOJIESOCIAL, {"taskId": token, "token": auth_token})
    logging.warning("social{0}:{1}:{2}".format(apply_number, token, auth_token))
    while index <= 3:
        try:
            response = requests.get(url, timeout=20).json()
            logging.warning("social{0}".format(response))
            break
        except Exception as e:
            logging.warn('[URL|%s] [error|%s]', url, str(e))
            index += 1
            time.sleep(1)

    SingleSearch.objects(apply_number=apply_number).update(
        upsert=True,
        set__social_security_data=response,
        set__apply_number=apply_number,
    )


@celery.task()
def social_detail_token(apply_number, phone, token, auth_token):
    index = 0
    url_original = querystring(CreditUri.MOJIESOCIALORIGNAL, {"taskId": token, "token": auth_token})
    logging.warning("social{0}:{1}:{2}".format(apply_number, token, auth_token))
    while index <= 3:
        try:
            resp = requests.get(url_original, timeout=20).json()
            logging.warning("OLD|social{0}".format(resp))
            break
        except Exception as e:
            logging.warn('[URL|%s] [error|%s]', url_original, str(e))
            index += 1
            time.sleep(1)

    SingleSearch.objects(apply_number=apply_number).update(
        upsert=True,
        set__social_security_original=resp,
        set__apply_number=apply_number,
    )


@celery.task()
def public_fund_token(apply_number, taskId, token):

    index = 0
    url = querystring(CreditUri.MOJIEFUND, {"taskId": taskId, "token": token})
    logging.warning("fund{0}:{1}:{2}".format(apply_number, taskId, token))
    while index <= 3:
        try:
            response = requests.get(url, timeout=20).json()
            logging.warning("OLD|fund{0}".format(response))
            break
        except Exception as e:
            logging.warning("[URL|{}] [ERROR|{}]".format(url, str(e)))
            index += 1
            time.sleep(1)

    SingleSearch.objects(apply_number=apply_number).update(
        upsert=True,
        set__public_funds_data=response,
        set__apply_number=apply_number,
    )


@celery.task()
def public_detail_token(apply_number, taskId, token):

    index = 0
    url_original = querystring(CreditUri.MOJIEFUNDORIGNAL, {"taskId": taskId, "token": token})
    logging.warning("fund{0}:{1}:{2}".format(apply_number, taskId, token))
    while index <= 3:
        try:
            resp = requests.get(url_original, timeout=20).json()
            logging.warning("fund{0}".format(resp))
            break
        except Exception as e:
            logging.warning("[URL|{}] [ERROR|{}]".format(url_original, str(e)))
            index += 1
            time.sleep(1)

    SingleSearch.objects(apply_number=apply_number).update(
        upsert=True,
        set__public_funds_original=resp,
        set__apply_number=apply_number,
    )


@celery.task()
def bank_report_data(apply_number, taskId, token):

    index = 0
    url = querystring(CreditUri.MOJIEBANKREPORT, {"taskId": taskId, "token": token})
    logging.warning("@@@@@@@@@bank{0}".format(url))
    logging.warning("bank{0}:{1}:{2}".format(apply_number, taskId, token))
    response = {}
    while index <= 3:
        try:
            response = requests.get(url, timeout=20).json()
            break
        except Exception as e:
            logging.warning("[URL|{}] [ERROR|{}]".format(url, str(e)))
            index += 1
            time.sleep(1)

    SingleSearch.objects(apply_number=apply_number).update(
        upsert=True,
        set__bank_report_data=response,
        set__apply_number=apply_number,
    )
