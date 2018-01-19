# -*- coding: utf-8 -*-

import datetime
import copy
import json
import logging

from gevent import Greenlet
import gevent
import random

from BestSignAPI import errorCode
from flask import g
from werkzeug.utils import import_string

from app.models.mongos import SingleSearch, InterfaceStat
from app.models.sqlas import Merchant, Company, InputApply, ReviewLog, CompanyRule, NewReviewLog
from app.constants import TelPrice, SearchStatus, Status, ApproveStatus
from app.core.functions import datetime2timestamp
from app.credit import census
from app.databases import session_scope, Session
from app.engine.engine import Engine

from .handler import new_get_is_break
from .report import (
    tel_batch, portait_active, credit_telrisklist, credit_manyplatcheck,
    credit_phoneblack, credit_phonedevicecheck, credit_newsplatrisk,
    credit_phonemsgcheck, credit_socialblacklist, channel_idcard,
    channel_bankby3, credit_netblacklist, credit_person, address_getbymobile,
    firm_info, credit_shixin, firm_court, firm_zhixing, firm_judgment,
    operator_black, channel_name_card_account, address_match
)
from .managers import RiskManager
from .interface import CreditInterface
from app.user.function import current_user


def search_credit(search_id, company_id, func_list, *args, **kwargs):
    """查询单条信用报告"""

    func_list_exec = [import_string('app.credit.report:%s' % func_str) for func_str in func_list]
    result_dict = {}
    pool = []
    # for func in func_list_exec:
    #     result_dict.update(func(**kwargs))
    # pool = gevent.pool.Pool(len(func_list_exec))
    for func in func_list_exec:
        pool.append(Greenlet.spawn(func, **kwargs))

    # 如果输入了家庭联系人，工作联系人，学校联系人，还要分别查
    for i in ['school', 'work', 'home']:
        key = i + '_phone'
        if not kwargs[key]:
            continue
        k = copy.deepcopy(kwargs)
        k['flag'] = i
        k['phone'] = kwargs[key]
        if 'credit_telrisklist' in func_list:
            pool.append(Greenlet.spawn(credit_telrisklist, **k))
        if 'credit_newsplatrisk' in func_list:
            pool.append(Greenlet.spawn(credit_newsplatrisk, **k))
        if 'credit_socialblacklist' in func_list:
            pool.append(Greenlet.spawn(credit_socialblacklist, **k))
    if kwargs["work_address"] and 'address_match' in  func_list:
        k = copy.deepcopy(kwargs)
        k["address"] = kwargs["work_address"]
        k['flag'] = 'work'
        pool.append(Greenlet.spawn(address_match, **k))

    gevent.joinall(pool)
    for ret in pool:
        try:
            result_dict.update(ret.value)
        except:
            import traceback
            traceback.print_exc()

    # 电商高位清单
    e_business_danger = result_dict.get('credit_telrisklist')
    # 多平台借贷
    multiple_loan = result_dict.get('credit_manyplatcheck')
    # 手机关联过账户
    phone_relate = result_dict.get("credit_phonedevicecheck")
    # 信息平台危清单
    info_dangers = result_dict.get("credit_newsplatrisk")
    # 网贷逾期黑名单
    loan_over_time_blacklist = result_dict.get("credit_netblacklist")
    # 社交平台高位清单
    social_dangers = result_dict.get("credit_socialblacklist")
    # 失信黑名单
    no_faith_list = result_dict.get("credit_person")
    # 手机标注黑名单
    phone_mark_blaklist = result_dict.get("credit_phoneblack")
    # 手机活跃度综合校验
    phone_verify = result_dict.get("credit_phonemsgcheck")
    # 天行银行卡三要素
    isBankNum = result_dict.get("channel_bankby3")
    # 小视数据接口
    name_idcard_account = result_dict.get("channel_name_card_account")
    # 天行身份认证
    isId = result_dict.get('channel_idcard')
    # 地址信息查询
    address_info = result_dict.get('address_getbymobile')

    # 马上负面信息借口
    mashang_negative = result_dict.get("mashang_negative", {})
    # 马上失信详情
    mashang_shixin = result_dict.get("mashang_shixin", {})
    # 马上简项身份核查
    mashang_idcard = result_dict.get("mashang_idcard", {})
    # 马上信用评分
    mashang_score = result_dict.get("mashang_score", {})
    # 马上逾期信息
    mashang_overdue = result_dict.get("mashang_overdue", {})
    # 小视在网时长
    mashang_online = CreditInterface.online_time_check(result_dict.get("mashang_online", {}))
    # 马上综合反欺诈
    mashang_credit = result_dict.get("mashang_credit", {})
    # 人脸验证, 马上
    youla_face = result_dict.get("youla_face", {})
    # 人脸验证, 优拉
    mashang_face = result_dict.get("mashang_face", {})

    # 新的在网时长17/3/19
    cellphone = result_dict.get("cellphone_get", {})
    # 公安不良信息
    undesirable_info = result_dict.get("undesirable_info", {})

    # 网贷 逾期多平台
    channel_netloanblacklist = result_dict.get("net_loan_overdue_platforms", {})
    # 网贷风险校验
    channel_riskinfocheck = result_dict.get("net_loan_risk_check", {})
    # 黑名单校验
    blacklist_check = result_dict.get("blacklist_check_query", {})

    e_business_danger_home = result_dict.get('credit_telrisklist_home')
    e_business_danger_work = result_dict.get('credit_telrisklist_work')
    e_business_danger_school = result_dict.get('credit_telrisklist_school')

    info_danger_home = result_dict.get('credit_newsplatrisk_home')
    info_danger_work = result_dict.get('credit_newsplatrisk_work')
    info_danger_school = result_dict.get('credit_newsplatrisk_school')

    social_danger_home = result_dict.get('credit_socialblacklist_home')
    social_danger_work = result_dict.get('credit_socialblacklist_work')
    social_danger_school = result_dict.get('credit_socialblacklist_school')

    address_match_result = result_dict.get('address_match')
    address_match_result_work = result_dict.get('address_match_work')

    # 手机在网时长W1
    operator_phonetime_result = result_dict.get('operator_phonetime')
    # 不良信息W1
    obtain_riskinfocheck_result = result_dict.get('obtain_riskinfocheck')
    # 多平台借贷W1
    operator_multiplatform_result = result_dict.get('operator_multiplatform')

    overdue_b = result_dict.get("obtain_loanintegration")
    multiple_loan_apply_a = result_dict.get("obtain_loanintegration")
    multiple_loan_register_b = result_dict.get("obtain_loanintegration")
    multiple_loan_apply_b = result_dict.get("obtain_loanriskinquiry")
    overdue_c = result_dict.get("obtain_loanriskinquiry")
    financial_bad = result_dict.get("obtain_loanriskinquiry")
    obtain_piccompare = result_dict.get("obtain_piccompare")

    is_break_data = copy.deepcopy(result_dict)
    # 先查一次库
    single_search = SingleSearch.objects(apply_number=search_id).first()
    # 用户关联信息校验
    user_contact_info = CreditInterface.user_contact_info_check(
        result_dict.get("user_contact_info", {}))
    # 用户被查询记录
    user_queryed_info = CreditInterface.user_queryed_info_check(
        result_dict.get("user_queryed_info", {}))

    def check_data(new_result, result):
        """检查数据是否需要覆盖"""
        if not result:
            return new_result
        if result.get("code") == TelPrice.CODE:
            return result
        return new_result

    # 企业相关数据
    if single_search.enterprise:
        enterprise = {
            "Court": check_data(result_dict.get("firm_court"), single_search.enterprise.get("Court")),
            "Judgment": check_data(result_dict.get("firm_judgment"), single_search.enterprise.get("Judgment")),
            "ShiXing": check_data(result_dict.get("credit_shixin"), single_search.enterprise.get("ShiXing")),
            "ZhiXing": check_data(result_dict.get("firm_zhixing"), single_search.enterprise.get("Zhixing")),
            "baseInfo": check_data(result_dict.get("firm_info"), single_search.enterprise.get("baseInfo")),
        }
    else:
        enterprise = {
            "Court": result_dict.get("firm_court"),
            "Judgment": result_dict.get("firm_judgment"),
            "ShiXing": result_dict.get("credit_shixin"),
            "ZhiXing": result_dict.get("firm_zhixing"),
            "baseInfo": result_dict.get("firm_info")
        }
    # 金融用户画像, 电商购物记录
    if single_search.tel_record:
        tel_record = {
            "portait_data": check_data(result_dict.get("portait_active"),
                                    single_search.tel_record.get("portrait_data")),
            "phone_list": check_data(result_dict.get("tel_batch"),
                                    single_search.tel_record.get("phone_list")),
        }
    else:
        tel_record = {
            "portait_data": result_dict.get("portait_active"),
            "phone_list": result_dict.get("tel_batch")
        }

    # 更新库
    SingleSearch.objects(apply_number=search_id).update(
        set__address_info=check_data(address_info, single_search.address_info),
        set__e_business_danger=check_data(e_business_danger, single_search.e_business_danger),
        set__multiple_loan=check_data(multiple_loan, single_search.multiple_loan),
        set__phone_relative=check_data(phone_relate, single_search.phone_relative),
        set__info_danger=check_data(info_dangers, single_search.info_danger),
        set__loan_over_time_blacklist=check_data(loan_over_time_blacklist, single_search.loan_over_time_blacklist),
        set__no_faith_list=check_data(no_faith_list, single_search.no_faith_list),
        set__phone_mark_blaklist=check_data(phone_mark_blaklist, single_search.phone_mark_blaklist),
        set__phone_verify=check_data(phone_verify, single_search.phone_verify),
        set__social_danger=check_data(social_dangers, single_search.social_danger),
        set__is_bank_num = check_data(isBankNum, single_search.is_bank_num),
        set__is_person = check_data(isId, single_search.is_person),
        set__name_idcard_account = check_data(name_idcard_account, single_search.name_idcard_account),
        set__tel_record=tel_record, # 企业相关数据
        set__enterprise=enterprise, # 电商相关数据
        set__e_business_danger_home=e_business_danger_home,
        set__e_business_danger_work=e_business_danger_work,
        set__e_business_danger_school=e_business_danger_school,
        set__info_danger_home=info_danger_home,
        set__info_danger_work=info_danger_work,
        set__info_danger_school=info_danger_school,
        set__social_danger_home=social_danger_home,
        set__social_danger_work=social_danger_work,
        set__social_danger_school=social_danger_school,
        set__address_match=address_match_result,
        set__address_match_work=address_match_result_work,
        set__channel_cellphone=CreditInterface.cellphone_check(cellphone),
        set__undesirable_info=CreditInterface.undesirable_info(undesirable_info),
        set__youla_face=youla_face,
        set__channel_netloanblacklist = CreditInterface.net_loan_platforms(
            channel_netloanblacklist or {}),
        set__channel_riskinfocheck=CreditInterface.net_net_loan_risk_check(
            channel_riskinfocheck or {}),
        set__blacklist_check=CreditInterface.blacklist_check(blacklist_check or {}),
        set__user_contact_info=user_contact_info,
        set__user_queryed_info=user_queryed_info,
        set__operator_phonetime_data=operator_phonetime_result,
        set__obtain_riskinfocheck_data=obtain_riskinfocheck_result,
        set__operator_multiplatform_data=operator_multiplatform_result,
        set__overdue_b=overdue_b,
        set__multiple_loan_apply_a=multiple_loan_apply_a,
        set__multiple_loan_register_b=multiple_loan_register_b,
        set__multiple_loan_apply_b=multiple_loan_apply_b,
        set__overdue_c=overdue_c,
        set__financial_bad=financial_bad,
        set__obtain_piccompare=obtain_piccompare,
    )

    kw = dict(
            mashang_negative=mashang_negative,
            mashang_shixin=mashang_shixin,
            mashang_idcard=mashang_idcard,
            mashang_score=mashang_score,
            mashang_overdue=mashang_overdue,
            mashang_online=mashang_online,
            mashang_credit=mashang_credit,
            mashang_face=mashang_face,
            mashang_phone=mashang_online
    )

    single_inst = SingleSearch.objects(apply_number=search_id).first()
    single_inst.update_repeat(**kw)
    # 在进行统计的时候, 需要对手机实名认证
    # result_dict.update({'mashang_phone': mashang_online})
    # 接口调用记录
    # interface_stat(result_dict, single_inst.company_id, single_inst.merchant_num)
    # 写入mysql, 更改状态
    score = handle_face_score(mashang_score, obtain_piccompare)

    with session_scope() as session:

        input_apply = session.query(InputApply).get(search_id)

        # 如果不运营商授权，要计算是否违规
        if not input_apply.token:
            risk_manager = RiskManager(session)
            is_break_rule = new_get_is_break(risk_manager.get_conclusion(search_id))
            input_apply.is_break_rule = is_break_rule
            SingleSearch.objects(apply_number=search_id).update(
                set__is_break_rule=is_break_rule,
            )
            # 如果不运营商授权并且信息填齐了，要伪造评分的
            if all([single_inst.name, single_inst.id_num, single_inst.bank_num, single_inst.phone]):
                score = risk_manager.modify_score(search_id, score, single_inst.phone)
                input_apply.score = score

    with session_scope() as session:
        input_apply = session.query(InputApply).get(search_id)

        # 缓存
        from .forcache import cache_search_result_view, cache_tel_consume_view, cache_address_verify_view, cache_token_status_view
        cache_search_result_view(session, {'id': search_id}, ignore_not_ready=True)
        cache_tel_consume_view(session, {'id': search_id})
        cache_address_verify_view(session, {'id': search_id})
        cache_token_status_view(session, {'id': search_id})
        session.merge(input_apply)

    with session_scope() as session:
        input_apply = session.query(InputApply).get(search_id)
        input_apply.search_status = SearchStatus.DONE
        input_apply.status = Status.APPROVING
        session.merge(input_apply)

    with session_scope() as session:
        # 拒绝引擎
        input_apply = session.query(InputApply).get(search_id)
        search = SingleSearch.objects(apply_number=search_id).first()
        rule = session.query(CompanyRule).filter(CompanyRule.company_id == input_apply.company_id).one_or_none()

        if rule:
            resp = False
            if rule.deny_rule:
                # 自动拒绝
                engine = Engine(rule.deny_rule, input_apply, search)
                resp = engine.evaluate()
                logging.info("自动拒绝的结果是\t{0}".format("拒绝" if resp else "不拒绝"))

                if resp:
                    input_apply.status = Status.APPROVEDENIED
                    input_apply.approve_status = ApproveStatus.AUTO_DENY
                    session.add(input_apply)
                    history = NewReviewLog(input_apply_id=search_id, create_time=datetime.datetime.now(), username="admin")
                    session.add(history)

            if rule.pass_rule and not resp:
                # 自动通过
                engine = Engine(rule.pass_rule, input_apply, search)
                resp = engine.evaluate()
                logging.info("自动通过的结果是\t{0}".format("通过" if resp else "不通过"))

                if resp:
                    input_apply.approve_status = ApproveStatus.PASS
                    input_apply.approve_status = ApproveStatus.AUTO_PASS
                    from app.loan.managers import LoanManager
                    loan_manager = LoanManager(session)
                    loan_manager.add_loan(input_apply)
                    session.add(input_apply)
                    history = NewReviewLog(input_apply_id=search_id, create_time=datetime.datetime.now(), username="admin")
                    session.add(history)


def handle_face_score(mashang_score, obtain_piccompare):
    if obtain_piccompare:
        from app.credit.pipeline import handle_obtain_piccompare
        score = handle_obtain_piccompare(obtain_piccompare)["faceScore"]
        return score
    elif mashang_score:
        return mashang_score.get('result', {}).get('MC_CRESCO', {}).get('RUL_SUM')
    return ""

# 这个没有用了
# def interface_stat(result, company_id, merchant_num=None):
#     """统计接口调用情况"""
#
#     now = datetime.datetime.now()
#     today = datetime2timestamp(datetime.date.today()) / 1000
#
#     session = Session()
#     company = session.query(Company).get(company_id)
#     if not company:
#         return
#     company_name = company.name
#     merchant = session.query(Merchant).get(merchant_num)
#     if merchant:
#         merchant_name = merchant.name
#     else:
#         merchant_name = ''
#
#     # 只引入census, 保持其命名空间独立, 因为mashang_all 使用了globals()函数
#     mashang_l = census.mashang_all(result, company_id)
#
#     interface_list = [
#         # {
#         #     'module_name': 'telBatch',
#         #     'func_name': 'tel_batch',
#         #     'is_success': 1,
#         #     'is_target': 0,
#         # },
#     ]
#     interface_list.extend(mashang_l)
#
#     for i in interface_list:
#         if not i:
#             continue
#
#         i.update({
#             'company_id': company.id,
#             'company_name': company_name,
#             'merchant_num': merchant_num,
#             'merchant_name': merchant_name,
#             'create_time': now,
#             'date': today,
#         })
#
#         InterfaceStat(**i).save()


def response_to_json(response):
    if type(response) is bytes:
        response = response.decode('utf-8')
    resp_json = json.loads(response)
    return resp_json


def call_api_ok(response):
    resp_json = response_to_json(response)
    return_code = resp_json['response']['info']['code']
    if return_code != 100000:
        raise AssertionError(errorCode.ERROR_CODE.get(return_code))
    else:
        return True


def check_whether_self(obj, current_user=current_user):
    """判断obj(input_apply, input_search)是不是当前用户所在公司的"""
    # company_id = getattr(current_user, 'company_id', None)
    # if company_id is None:
    #     return True

    # return company_id == obj.company_id
    return True
