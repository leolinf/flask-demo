# -*- coding: utf-8 -*-

import copy
import time

from app.models.sqlas import InputApply

from .managers import CreditManager
from .handler import get_single_result
from app.core.functions import dict_list_util, save_to_cache
from app.models.mongos import SingleSearch
from app.constants import Code
from .pipeline import (
    tel_list_pipe
)
from .utils import check_whether_self


def cache_operator_view(session, req):
    """缓存运营商基本信息"""

    single_search = SingleSearch.objects(apply_number=req["id"]).first()

    if not single_search:
        return Code.SINGLE_NOT_EXIST

    if not check_whether_self(single_search):
        return Code.NOT_ALLOWED

    operator_data = single_search.operator_data
    if not operator_data:
        capcha_info = single_search.capcha_info
        if capcha_info:
            if capcha_info.get("status", 0) == 1 and capcha_info.get("token", None):
                return Code.SINGLE_NOT_READY

    operator_data = operator_data.get('callback_operator', {})
    result = {}
    # 基本信息
    phoneInfo = operator_data.get('data', {}).get('phoneInfo', {})
    baseInfo = operator_data.get('data', {}).get('baseInfo', {})
    def time_str_handler(d):
        if isinstance(d, int) and d == 0:
            return ''
        if len(d) == 8:
            return d[0:4] + '-' +d[4:6] + '-' + d[6:]
        return d


    from app.capcha_report.util import UserExceptionAction
    # 用户异常行为分析
    obj = UserExceptionAction(operator_data.get("data", {}))
    def cmcc(operator):
        if operator == "CHINA_MOBILE":
            return "中国移动"
        if operator == "CHINA_TELECOM":
            return "中国电信"
        if operator == "CHINA_UNICOM":
            return "中国联通"
        return ""

    phone_base_info = {
        "inNetDate": time_str_handler(phoneInfo.get("inNetDate", "")),
        "lastCallDate": time_str_handler(phoneInfo.get("lastCallDate", "")),
        "type": cmcc(phoneInfo.get("operator", "")),
        "realName": phoneInfo.get("realName", ""),
        "balance": phoneInfo.get("available_balance", -100) or -100,
        "attribute": baseInfo.get("phoneBelongArea", "") or "",
        "status": phoneInfo.get("state", 0) or 0,
        "averageConsume": obj.average_consume(operator_data.get("data", {}).get("historyFeeInfo", []))
    }
    result['phoneInfo'] = phone_base_info

    if isinstance(operator_data.get('data', ''), dict):
        flag = True
    else:
        flag = False

    # 风险号码标识记录分析
    result['riskNumTag'] = obj.risk_phone_analyze(operator_data.get('data'), flag)
    # 重要联系人通话分析
    input_obj = session.query(InputApply).filter_by(id=req["id"]).first()
    rel, work, school = None, None, None
    if not input_obj:
        return Code.SINGLE_NOT_EXIST

    that_day = single_search.create_time.strftime('%Y%m%d')

    result['abnormalBehavior'] = obj.user_exception_handler(operator_data.get('data', {}), flag, input_obj.token, that_day)

    if input_obj.home_mem_phone:
        rel = {
            'relation': input_obj.home_mem_relation or '',
            'phone': input_obj.home_mem_phone or '',
            "name": input_obj.home_mem_name or '',
            'type': '家庭联系人'
        }
    if input_obj.work_contact_phone:
        work = {
            'relation': '同事',
            'phone': input_obj.work_contact_phone or '',
            'name': input_obj.work_contact_name or '',
            'type': '工作单位联系人'
        }
    if input_obj.school_contact_phone:
        school = {
            'relation': input_obj.school_contact_relation,
            'phone': input_obj.school_contact_phone,
            'name': input_obj.school_contact or '',
            'type': '学校联系人'
        }

    result['importantConnAnalysis'] = obj.important_conn_analysis(
        operator_data.get('data', {}), rel, work, school, flag)

    #  联系人top5分析
    result['connTop5Analysis'] = obj.connection_top_analyze(operator_data.get('data', {}))

    # 趋势分析
    result['importantConnChart'] = obj.important_conn_chart(operator_data.get('data', {}), rel, work, school)

    # 本人通话区域TOP5分析
    result['callAreaTop5'] = obj.phone_region_top5(operator_data.get("data", {}))

    # 联系人区域TOP5分析
    result['connAreaTop5'] = obj.contract_area(operator_data.get('data', {}))

    # 通话时段分析
    result['callAnalysisData'] = obj.conversation_slot(operator_data.get('data', {}).get('deceitRisk', {}))
    save_to_cache(req['id'], result, 'operator_view')

    return result


def cache_search_result_view(session, req, ignore_not_ready=False):
    """缓存单条查询记录"""

    single_id = req['id']
    single_result = get_single_result(session, single_id, ignore_not_ready=ignore_not_ready)

    if single_result == 'not ready':
        return Code.SINGLE_NOT_READY

    if single_result == 'not exists':
        return Code.SINGLE_NOT_EXIST

    if single_result == 'not allowed':
        return Code.NOT_ALLOWED

    data = copy.deepcopy(single_result)
    dict_list_util(data)
    save_to_cache(single_id, data, 'search_result_view')
    return data


def cache_msg_record_view(session, req):

    single_search = SingleSearch.objects(apply_number=req["id"]).first()
    if not single_search:
        return Code.SINGLE_NOT_EXIST
    if not check_whether_self(single_search):
        return Code.NOT_ALLOWED

    from app.capcha_report.util import UserExceptionAction
    data = single_search.operator_data.get("callback_operator", {})

    count = -1 if req['token'] else req['count']
    result = UserExceptionAction.sms_record_analyze(
        data.get('data', {}).get("messageRecordsInfo", {}), req['isMark'], req['page'], count, apply_number=req['id'])

    return result


def cache_call_record_view(session, req):

    single_search = SingleSearch.objects(apply_number=req["id"]).first()
    if not single_search:
        return Code.SINGLE_NOT_EXIST
    if not check_whether_self(single_search):
        return Code.NOT_ALLOWED

    from app.capcha_report.util import UserExceptionAction
    data = single_search.operator_data.get("callback_operator", {})
    count = -1 if req['token'] else int(req['count'])
    result = UserExceptionAction.contract_record(data.get("data", {}).get("callRecordsInfo", {}),
                                        req['isMark'], int(req['page']), count, apply_number=req['id'])

    return result


def cache_tel_consume_view(session, req):

    single_search = SingleSearch.objects(apply_number=req["id"]).first()
    if not single_search:
        return Code.SINGLE_NOT_EXIST
    if not check_whether_self(single_search):
        return Code.NOT_ALLOWED
    result = tel_list_pipe(single_search.tel_record)
    save_to_cache(req['id'], result, 'tel_consume_view')

    return result


def cache_address_verify_view(session, req):

    credit_manager = CreditManager(session)

    res = credit_manager.get_address(req['id'])

    if res == 'not exist':
        return Code.SINGLE_NOT_EXIST

    save_to_cache(req['id'], res, 'address_verify_view')
    return res


def cache_token_status_view(session, req):

    obj = session.query(InputApply).get(req['id'])
    sin_obj = SingleSearch.objects(apply_number=req['id']).first()
    if obj and (not obj.token):
        res = {"operatorStatus": 0}
        save_to_cache(req['id'], res, 'token_status_view')
        social_token_status(obj, sin_obj, res)
        fund_token_status(obj, sin_obj, res)
        bank_report_status(obj, sin_obj, res)
        taobao_report_status(obj, sin_obj, res)
        return res

    if sin_obj and sin_obj.operator_data:
        res = {"operatorStatus": 2}
        save_to_cache(req['id'], res, 'token_status_view')
        social_token_status(obj, sin_obj, res)
        fund_token_status(obj, sin_obj, res)
        bank_report_status(obj, sin_obj, res)
        taobao_report_status(obj, sin_obj, res)
        return res

    if sin_obj and (not sin_obj.operator_data):
        res = {"operatorStatus": 1}
        social_token_status(obj, sin_obj, res)
        fund_token_status(obj, sin_obj, res)
        bank_report_status(obj, sin_obj, res)
        taobao_report_status(obj, sin_obj, res)
        return res

    res = {"operatorStatus": 0}
    save_to_cache(req['id'], res, 'token_status_view')
    social_token_status(obj, sin_obj, res)
    fund_token_status(obj, sin_obj, res)
    bank_report_status(obj, sin_obj, res)
    taobao_report_status(obj, sin_obj, res)
    return res


def social_token_status(obj, sin_obj, res):
    if obj and (not obj.social_security_id):
        status = {"socialStatus": 0}
        res.update(status)
        return

    if sin_obj and sin_obj.social_security_data:
        status = {"socialStatus": 2}
        res.update(status)
        return

    if sin_obj and (not sin_obj.social_security_data):
        status = {"socialStatus": 1}
        res.update(status)
        return

    status = {"socialStatus": 0}
    res.update(status)
    return


def fund_token_status(obj, sin_obj, res):
    if obj and (not obj.public_funds_id):
        status = {"fundStatus": 0}
        res.update(status)
        return

    if sin_obj and sin_obj.public_funds_data:
        status = {"fundStatus": 2}
        res.update(status)
        return

    if sin_obj and (not sin_obj.public_funds_data):
        status = {"fundStatus": 1}
        res.update(status)
        return

    status = {"fundStatus": 0}
    res.update(status)
    return


def bank_report_status(obj, sin_obj, res):

    if obj and (not obj.credit_investigation_id):
        status = {"bankReportStatus": 0}
        res.update(status)
        return

    if sin_obj and sin_obj.bank_report_data:
        status = {"bankReportStatus": 2}
        res.update(status)
        return
    if obj:
        last_time = time.mktime(obj.last_update.timetuple())
        now_time = int(time.time())
        if sin_obj and now_time - int(last_time) > 604800:
            status = {"bankReportStatus": 3}
            res.update(status)
            return
    if sin_obj and (not sin_obj.bank_report_data):
        status = {"bankReportStatus": 1}
        res.update(status)
        return

    status = {"bankReportStatus": 0}
    res.update(status)
    return


def taobao_report_status(obj, sin_obj, res):

    if obj and (not obj.tb_id):
        status = {"taobaoReportStatus": 0}
        res.update(status)
        return

    if sin_obj and sin_obj.taobao_data:
        status = {"taobaoReportStatus": 2}
        res.update(status)
        return
    if sin_obj and (not sin_obj.taobao_data):
        status = {"taobaoReportStatus": 1}
        res.update(status)
        return

    status = {"taobaoReportStatus": 0}
    res.update(status)
    return
