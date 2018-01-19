# -*- encoding: utf-8 -*-

import grequests

from app.models.mongos import SingleSearch, PhoneAddress, IdcardAddress
from app.models.sqlas import InputApply
from app.constants import SearchStatus, CreditAuth
from app.core.logger import project_logger
from app.core.functions import datetime2timestamp, sex_from_idcard, age_from_idcard

from .pipeline import (
    address_search, tel_risk, info_danger, loan_over, many_plat,
    no_faith, phone_mark_black, phone_active, phone_relative,
    social_danger, mashang_online, mashang_credit, mashang_negative,
    mashang_overdue, bank_three, horse_idcard, horse_online,
    horse_score, horse_face_score, channel_idcard, name_idcard_account,
    handle_cellphone, handle_undesirable_info, handle_netloan_platforms,
    handle_netloan_risk, blacklist_check_handle, user_contact_info_handle,
    user_queryed_info_handle, handle_operator_phonetime, handle_obtain_riskinfocheck,
    handle_operator_multiplatform, handle_overdue_b,
    handle_multiple_loan_apply_a, handle_multiple_loan_register_b, handle_overdue_c, handle_multiple_loan_apply_b,
    handle_financial_bad, handle_obtain_piccompare)
from app.config import Config
from app.apply_config.phone_type import get_phone_type


def generate_img_url(single_id, img_type=str(1)):
    """根据singleSearch的id生成对应的图片地址
    目前只有一张图片所以默认给1
    """
    return {'faceImg': '/api/images/{img_type}/{single_id}.jpg'.format(
        img_type=img_type, single_id=single_id)}


def get_single_result(session, single_id, ignore_not_ready=False):
    """获取单条查询记录"""
    from .utils import check_whether_self

    single_search = SingleSearch.objects(apply_number=single_id).first()
    input_apply = session.query(InputApply).filter(InputApply.id==single_id).first()

    if not single_search or not input_apply:
        return 'not exists'

    if not check_whether_self(input_apply):
        return 'not allowed'

    if input_apply.search_status != SearchStatus.DONE and not ignore_not_ready:
        return 'not ready'

    phone_address = PhoneAddress.objects(phone=input_apply.phone[:7]).first()
    idcard_address = IdcardAddress.objects(idcard=input_apply.idcard[:6]).first()

    basic_info = {
        'bankNum': input_apply.bank_num,
        'idCard': input_apply.idcard,
        'name': input_apply.name,
        'phone': input_apply.phone,
        'age': age_from_idcard(input_apply.idcard) if input_apply.idcard else None,
        'reportTime': datetime2timestamp(input_apply.create_time),
        'sex': sex_from_idcard(input_apply.idcard) if input_apply.idcard else None,
        'number': single_id,
        "phoneAddress": phone_address.address if phone_address else "",
        "idcardAddress": idcard_address.address if idcard_address else "",
    }
    # 地址信息处理
    addressInfo = address_search(single_search.address, single_search.address_info)
    # 电商高位清单
    e_business_danger = tel_risk(single_search.e_business_danger)
    # 信息平台高位清单
    info_dangers = info_danger(single_search.info_danger)
    # 网贷逾期黑名单
    loan_over_time_blacklist = loan_over(single_search.loan_over_time_blacklist)
    # 多平台借贷
    multiple_loan = many_plat(single_search.multiple_loan)
    # 个人失信黑名单
    no_faith_list = no_faith(single_search.no_faith_list)
    # 手机号标注黑名单
    phone_mark_blaklist = phone_mark_black(single_search.phone_mark_blaklist)
    # 手机关联多账户
    phone_relatives = phone_relative(single_search.phone_relative)
    # 手机活跃度综合校验
    phone_verify = phone_active(single_search.phone_verify)
    # 社交平台高位清单
    social_dangers = social_danger(single_search.social_danger)
    # 天行身份认证
    channel_idcard_data = channel_idcard(single_search.is_person)
    # 天行银行卡三要素认证
    channel_bankby3 = bank_three(single_search.is_bank_num)
    # 小视银行卡三要素
    name_idcard_account_data = name_idcard_account(single_search.name_idcard_account)
    # 马上失信
    horse_shixin = None
    # 手机在网时长
    online_time = mashang_online(single_search.mashang_online)
    # 第三方综合反欺诈
    third_anti_fraud = mashang_credit(single_search.mashang_credit)
    # 第三方负面信息
    third_negative_info = mashang_negative(single_search.mashang_negative)
    # 第三方逾期信息
    third_over_time = mashang_overdue(single_search.mashang_overdue)
    # 马上身份验证信息
    mashang_idcard = horse_idcard(single_search.mashang_idcard)
    # 马上综合得分
    third_score = horse_score(single_search.mashang_score)
    # 马上人脸识别得分
    third_face_score = horse_face_score(single_search.mashang_face)
    # 马上手机号认证
    third_is_phone = horse_online(single_search.mashang_online)
    # 身份证正面照地址

    youla_face_score = horse_face_score(single_search.youla_face)

    cell_phone = handle_cellphone(single_search.channel_cellphone)

    # 在网时长W1
    operator_phonetime_data = handle_operator_phonetime(single_search.operator_phonetime_data)
    # 不良信息W1
    obtain_riskinfocheck_data = handle_obtain_riskinfocheck(single_search.obtain_riskinfocheck_data)
    # 多平台借贷W1
    operator_multiplatform_data = handle_operator_multiplatform(single_search.operator_multiplatform_data)

    # 网贷逾期多平台
    channel_netloanblacklist = handle_netloan_platforms(
        single_search.channel_netloanblacklist or {})
    # 网贷逾期风险校验
    channel_riskinfocheck = handle_netloan_risk(
        single_search.channel_riskinfocheck or {})
    blacklist_check = blacklist_check_handle(single_search.blacklist_check or {})
    # 用户关联信息校验
    user_contact_info_data = user_contact_info_handle(single_search.user_contact_info)
    user_queryed_info_data = user_queryed_info_handle(single_search.user_queryed_info)

    undesirable_info = handle_undesirable_info(single_search.undesirable_info)

    overdue_b = handle_overdue_b(single_search.overdue_b)
    multiple_loan_apply_a = handle_multiple_loan_apply_a(single_search.multiple_loan_apply_a)
    multiple_loan_register_b = handle_multiple_loan_register_b(single_search.multiple_loan_register_b)
    overdue_c = handle_overdue_c(single_search.overdue_c)
    multiple_loan_apply_b = handle_multiple_loan_apply_b(single_search.multiple_loan_apply_b)
    financial_bad = handle_financial_bad(single_search.financial_bad)
    obtain_piccompare = handle_obtain_piccompare(single_search.obtain_piccompare)

    func_list = single_search.permission_func
    field_list = [j for i in func_list if CreditAuth.FUN_FIELD.get(i) for j in CreditAuth.FUN_FIELD.get(i)]
    response = {}
    for i in field_list:
        response[CreditAuth.FIELD_RESP[i]] = locals()[i]
    verify_Info = {}
    verify_Info.update(response.get("isId", {"isId": 1}))
    verify_Info.update(response.get("isBankNum", {"isBankNum": 1}))
    verify_Info.update({'score': int(input_apply.score) if input_apply.score else -100})
    verify_Info.update(response.get("faceScore", {"faceScore": -100}))
    verify_Info.update(response.get("isPhone", {"isPhone": 1}))

    # call java server api to get token info to get img info
    # urls = [Config.FILE_SERVER_TOKEN]
    # rs = (grequests.post(u, data={"companyId": input_apply.input_user.company_id}, timeout=1) for u in urls)

    def exception_handler(request, exception):
        project_logger.error("call java token server error %s %s" % (
            str(exception), str(input_apply.input_user.company_id)))
        return {}
    
    # ret = list(grequests.map(rs, exception_handler=exception_handler))[0]
    param = ''
    # try:
    #     ret = ret.json().get("data", {})
    #     ret.update({
    #         'companyId': input_apply.input_user.company_id
    #     })
    #     for key, value in ret.items():
    #         param += '&' + str(key) + '=' + str(value)
    # except:
    #     ret = {}

    if input_apply.photo_with_card:
        verify_Info.update({"faceImg": input_apply.photo_with_card + '?from=riskbackend' + param})
    else:
        verify_Info.update({"faceImg": ""})

    if input_apply.operator != 1:
        is_break = int(input_apply.is_break_rule) if input_apply.is_break_rule else 0
    else:
        is_break = -1

    res = {
        'isBreakRule': is_break,
        'basicInfo': basic_info,
        'verifyInfo': verify_Info,
        'addressInfo': {"addressStatus": 1, "eAddress": [], "usualAddress": ""},
        'eBusinessDanger': {"isTarget": 0, "targetList": [], "targetNum": 0},
        'infoDanger': {"isTarget": 0, "targetList": [], "targetNum": 0},
        'loanOverTimeBlackList': {"isTarget": 1, "targetList": [], "targetNum": 0},
        'multipleLoan': {"isTarget": 0, "loanNum": 0, "targetList": []},
        'noFaithList': {"isTarget": 1, "targetList": [], "targetNum": 0},
        'phoneMarkBlackList': {"isTarget": 0, "targetList": []},
        'phoneRelative': {"isTarget": 3},
        'phoneVertify': {},
        'socialDanger': {"attentionList": [], "isTarget": 0, "targetList": [], "targetNum": 0},
        'onLineTime': {"operator": "", "phoneStatus": "", "timeRange": ""},
        'thirdAntiFraud': {"isTarget": 0, "targetList": []},
        'thirdNegativeInfo': {"isAction": -1, "isAntiFraud": -1, "isLost": -1, "isTarget": 0},
        'thirdOverTime': {"isNow": -1, "isPast": -1, "isTarget": 0},

    }
    res.update(response)

    # if channel_cellphone
    if single_search.channel_cellphone:
        res['verifyInfo']['isPhone'] = cell_phone['isPhone']
        res['isPhone'] = cell_phone['isPhone']
        # res['onLineTime']['operator'] = cell_phone['operator']
    res['onLineTime']['operator'] = get_phone_type(basic_info['phone'])

    from .pipeline import handle_import_contact
    res['contactInfoCheck'] = handle_import_contact(session, single_search.operator_data, single_search.apply_number)
    return res


def get_is_break(result_dict, search_id):
    """计算是否触犯规则"""

    single_search = SingleSearch.objects(apply_number=search_id).first()
    if not single_search:
        return 0
    func_list = single_search.permission_func
    # 电商高位清单
    _e_business_danger = tel_risk(result_dict.get('credit_telrisklist'))
    # 信息平台危清单
    _info_dangers = info_danger(result_dict.get("credit_newsplatrisk"))
    # 多平台借贷
    _multiple_loan = many_plat(result_dict.get('credit_manyplatcheck'))
    # 手机关联过账户
    _phone_relate = phone_relative(result_dict.get("credit_phonedevicecheck"))
    # 网贷逾期黑名单
    _loan_over_time_blacklist = loan_over(result_dict.get("credit_netblacklist"))
    # 失信黑名单
    _no_faith_list = no_faith(result_dict.get("credit_shixin"))
    # 手机标注黑名单
    _phone_mark_blaklist = phone_mark_black(result_dict.get("credit_phoneblack"))
    # 社交平台高位清单
    _social_dangers = social_danger(result_dict.get("credit_socialblacklist"))

    # 马上负面信息借口
    _third_negative_info = mashang_negative(result_dict.get("mashang_negative", {}))
    # 马上逾期信息
    _third_over_time = mashang_overdue(result_dict.get("mashang_overdue", {}))
    # 马上综合反欺诈
    _third_anti_fraud = mashang_credit(result_dict.get("mashang_credit", {}))
    # 马上简项身份核查
    _verifyInfo = horse_idcard(result_dict.get("mashang_idcard", {}))
    # 马上手机号验证
    _verifyInfo.update(horse_online(result_dict.get("mashang_online", {})))
    # 银行卡验证信息
    if 'channel_bankby3' in func_list:
        _verifyInfo.update(bank_three(result_dict.get("channel_bankby3")))
    # 小视银行卡三要素
    if 'channel_name_card_account' in func_list:
        _verifyInfo.update(name_idcard_account(result_dict.get("channel_name_card_account")))

    _cell_phone = handle_cellphone(result_dict.get('cellphone_get', {}))
    # 公安不良信息
    undesirable_info = handle_undesirable_info(single_search.undesirable_info)

    data_list = [
        _e_business_danger,
        _info_dangers,
        _multiple_loan,
        _phone_mark_blaklist,
        _social_dangers,
        _third_anti_fraud,
        _third_negative_info,
        _third_over_time,

    ]
    data_other_list = [
        _loan_over_time_blacklist,
        _phone_relate,
        _no_faith_list,
        undesirable_info  # 公安不良信息
    ]
    project_logger.warn("[data_list|%s][data_other_list|%s][_verifyInfo|%s]", data_list, data_other_list, _verifyInfo)
    is_break_rule = 0
    if 2 in [i.get("isTarget", 0) for i in data_other_list]:
        is_break_rule = 1
    if 1 in [i.get('isTarget', 0) for i in data_list]:
        is_break_rule = 1
    if 3 in _verifyInfo.values():
        is_break_rule = 1
    if _cell_phone.get('isPhone') == 3:
        is_break_rule = 1
    return is_break_rule


def new_get_is_break(conclusion):
    """按照贷前风险评估计算是否违规"""

    if conclusion >= 4:
        return True

    return False
