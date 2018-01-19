# -*- coding: utf-8 -*-

# from app.models import Module

"""
统计部分部分的功能
"""


def mashang_req_judge(result):
    """ 判断马上数据接口是否失败的情况 """
    if result.get('is_success', None) == 'F' and \
            'error' in result:
        return False
    if result.get('is_pass', False) is True:
        return False
    return True


def mashang_idcard(result):
    """ 马上身份证验证"""
    ret = {
        'module_name': 'idcard',
        'func_name': 'mashang_idcard',
    }
    if mashang_req_judge(result) is False:
        ret.update({
            'is_success': 0,
            'is_target': 0
        })
        return ret

    indent = result.get('MC_IDENT_IDS', {}).get('IDENT_ID', '')
    target = 1 if '存在' == indent else 0  # 身份证号码不存在, 认定为不命中
    ret.update({
        'is_success': 1,
        'is_target': target
    })
    return ret


def mashang_negative(result):
    """ 马上数据 负面信息"""
    ret = {
        'module_name': 'mashangNegative',
        'func_name': 'mashang_negative'
    }
    if mashang_req_judge(result) is False:
        ret.update({
            'is_success': 0,
            'is_target': 0
        })
        return ret
    d = result.get('MC_FRD', {})
    if d.get('IF_EXE') == '是' or d.get('IF_OC') == '是' or d.get('IF_F') == '是':
        target = 1
    else:
        target = 0
    ret.update({
        'is_success': 1,
        'is_target': target
    })
    return ret


def mashang_score(result):
    """ 马上数据  信用评分"""
    ret = {
        'module_name': 'mashangScore',
        'func_name': 'mashang_score'}
    if mashang_req_judge(result) is False:
        ret.update({
            'is_success': 0,
            'is_target': 0
        })
        return ret
    target = 1 if result.get('MC_CRESCO', {}).get('RUL_SUM', '') else 0
    ret.update({
        'is_success': 1,
        'is_target': target
    })
    return ret


def mashang_overdue(result):
    """ 逾期信息 """
    ret = {
        'module_name': 'mashangOverdue',
        'func_name': 'mashang_overdue'
    }
    if mashang_req_judge(result) is False:
        ret.update({
            'is_success': 0,
            'is_target': 0
        })
        return ret

    d = result.get('MC_PD', {})
    if d.get('IF_OD') == '是' or d.get('IF_ODN') == '是':
        target = 1
    else:
        target = 0
    ret.update({
        'is_success': 1,
        'is_target': target
    })
    return ret


def mashang_credit(result):
    """ 综合反欺诈 """
    ret = {
        'module_name': 'mashangCredit',
        'func_name': 'mashang_credit'
    }
    if mashang_req_judge(result) is False:
        ret.update({
            'is_success': 0,
            'is_target': 0
        })
        return ret
    if len(result.get('MC_CPF', [])) > 0:
        target = 1
    else:
        target = 0

    ret.update({
        'is_success': 1,
        'is_target': target
    })
    return ret


def mashang_face(result):
    """ 马上人脸评分"""
    ret = {
        'module_name': 'mashangScore',
        'func_name': 'mashang_face',
    }
    if mashang_req_judge(result) is False:
        ret.update({
            'is_success': 0,
            'is_target': 0
        })
        return ret
    target = 1 if result.get('MC_PI', {}).get('SCORE_IDENT', '') else 0

    ret.update({
        'is_success': 1,
        'is_target': target
    })
    return ret


def mashang_online(result):
    ret = {
        'module_name': 'online',
        'func_name': 'mashang_online',
    }
    if mashang_req_judge(result) is False:
        ret.update({
            'is_success': 0,
            'is_target': 0
        })
        return ret
    target = 1 if result.get('MC_TETIME', {}).get('TIME_PHONE') != '无记录' else 0
    ret = {
        'module_name': 'online',
        'func_name': 'mashang_online',
        'is_success': 1,
        'is_target': target,
    }

    return ret


def mashang_phone(result):
    """ 手机实名认证 """
    ret = {
        'module_name': 'phone_auth',
        'func_name': 'mashang_phone',
    }
    if mashang_req_judge(result) is False:
        ret.update({
            'is_success': 0,
            'is_target': 0
        })
        return ret
    target = 1 if '一致' in result.get('MC_TECHK', {}).get('RUL_PHONE', '') else 0
    ret = {
        'module_name': 'phone_auth',
        'func_name': 'mashang_phone',
        'is_success': 1,
        'is_target': target,
    }

    return ret


def mashang_all(all_result, company_id):
    """  马上数据 """
    # mashang_name_l = Module.objects(company_id=company_id).distinct('func_name')

    # if 'mashang_online' in mashang_name_l and 'mashang_phone' not in mashang_name_l:
    #     mashang_name_l.append('mashang_phone')
    mashang_name_l = ['mashang_phone', 'mashang_online']

    def map_reduce(key):
        d = all_result.get(key)
        if d:
            func_keys = globals()
            if key in func_keys:
                # 没有查询时, is_pass 在最外层,需要特殊处理
                if key.startswith('mashang') and 'is_pass' not in d:
                    d = d.get('result', {})
                # it does not need to judge , in case critial
                if key in func_keys:
                    ret = func_keys[key](d)
            return ret

    ret_l = map(map_reduce, mashang_name_l)
    return ret_l


"""
征信相关接口
"""


def check_interface(result):
    ret = {
        "is_success": 0,
        "is_target": 0,
    }
    if result.get("code", "") == 1200:
        ret.update({"is_success": 1, "is_target": 1})
    if result.get("code", "") == 1230:
        ret.update({"is_success": 1, "is_target": 0})
    return ret


def tel_batch(result):
    """电商消费记录"""

    ret = {
        'module_name': 'telBatch',
        'func_name': 'tel_batch',
    }
    success_target = check_interface(result)
    ret.update(success_target)
    return ret


def portait_active(result):
    """金融用户画像"""

    ret = {
        'module_name': 'portraitActive',
        'func_name': 'portait_active',
    }
    success_target = check_interface(result)
    ret.update(success_target)
    return ret


def credit_telrisklist(result):
    """电商高危接口请求"""

    ret = {
        'module_name': 'creditTelRiskList',
        'func_name': 'credit_telrisklist',
    }
    success_target = check_interface(result)
    ret.update(success_target)
    return ret


def credit_manyplatcheck(result):
    """多平借贷"""

    ret = {
        'module_name': 'creditManyPlatCheck',
        'func_name': 'credit_manyplatcheck',
    }
    success_target = check_interface(result)
    ret.update(success_target)
    return ret


def credit_phoneblack(result):
    """手机号标注黑名单"""

    ret = {
        'module_name': 'creditPhoneBlack',
        'func_name': 'credit_phoneblack',
    }
    success_target = check_interface(result)
    ret.update(success_target)
    return ret


def credit_phonedevicecheck(result):
    """手机号关联多账户"""

    ret = {
        'module_name': 'creditPhoneDeviceCheck',
        'func_name': 'credit_phonedevicecheck',
    }
    success_target = check_interface(result)
    ret.update(success_target)
    return ret


def credit_newsplatrisk(result):
    """信息平台高危清单"""

    ret = {
        'module_name': 'creditNewsPlatRisk',
        'func_name': 'credit_newsplatrisk',
    }
    success_target = check_interface(result)
    ret.update(success_target)
    return ret


def credit_phonemsgcheck(result):
    """手机活跃度综合校验"""

    ret = {
        'module_name': 'creditPhoneMsgCheck',
        'func_name': 'credit_phonemsgcheck',
    }
    success_target = check_interface(result)
    ret.update(success_target)
    return ret


def credit_socialblacklist(result):
    """社交平台高位数据"""

    ret = {
        'module_name': 'creditSocialBlackList',
        'func_name': 'credit_socialblacklist',
    }
    success_target = check_interface(result)
    ret.update(success_target)
    return ret


def channel_idcard(result):
    """身份验证"""

    ret = {
        'module_name': 'idCard',
        'func_name': 'channel_idcard',
        'is_success': 0,
        'is_target': 0
    }
    if result.get("code", 0) == 1200:
        ret.update({"is_success": 1})
        code_data = result.get("data", {}).get("result", "")
        if code_data == "-1" or code_data == "1":
            ret.update({"is_target": 1})
    return ret



def channel_bankby3(result):
    """银行卡三要素验证"""

    ret = {
        'module_name': 'channelBankby3',
        'func_name': 'channel_bankby3',
        'is_success': 0,
        'is_target': 0
    }
    if result.get("code", 0) == 1200:
        ret.update({"is_success": 1})
        code_data = result.get("data", {}).get("result", "")
        if code_data == "t" or code_data == "f":
            ret.update({"is_target": 1})
    return ret


def channel_name_card_account(result):
    """银行卡三要素验证"""

    ret = {
        'module_name': 'channelBankby3',
        'func_name': 'channel_name_card_account',
        'is_success': 0,
        'is_target': 0
    }
    if result.get("code", 0) == 1200:
        ret.update({"is_success": 1})
        code_data = result.get("data", {}).get("RESULT", "")
        if code_data == "1" or code_data == "2":
            ret.update({"is_target": 1})
    return ret


def credit_netblacklist(result):
    """网贷逾期黑名单"""

    ret = {
        'module_name': 'creditNetBlackList',
        'func_name': 'credit_netblacklist',
    }
    success_target = check_interface(result)
    ret.update(success_target)
    return ret


def credit_person(result):
    """失信黑名单"""

    ret = {
        'module_name': 'creditPerson',
        'func_name': 'credit_person',
    }
    success_target = check_interface(result)
    ret.update(success_target)
    return ret


def address_getbymobile(result):
    """地址信息查询"""

    ret = {
        'module_name': 'addressGetByMobile',
        'func_name': 'address_getbymobile',
    }
    success_target = check_interface(result)
    ret.update(success_target)
    return ret


def firm_info(result):
    """企业工商信息查询"""

    ret = {
        'module_name': 'firmInfo',
        'func_name': 'firm_info',
    }
    success_target = check_interface(result)
    ret.update(success_target)
    return ret



def credit_shixin(result):
    """失信网企业失信数据"""

    ret = {
        'module_name': 'shixin',
        'func_name': 'credit_shixin',
    }
    success_target = check_interface(result)
    ret.update(success_target)
    return ret



def firm_court(result):
    """法院公告信息"""

    ret = {
        'module_name': 'firmCourt',
        'func_name': 'firm_court',
    }
    success_target = check_interface(result)
    ret.update(success_target)
    return ret



def firm_judgment(result):
    """企业裁判文书信息"""

    ret = {
        'module_name': 'firmJudgment',
        'func_name': 'firm_judgment',
    }
    success_target = check_interface(result)
    ret.update(success_target)
    return ret



def firm_zhixing(result):
    """企业被执行信息"""

    ret = {
        'module_name': 'firmZhixing',
        'func_name': 'firm_zhixing',
    }
    success_target = check_interface(result)
    ret.update(success_target)
    return ret
