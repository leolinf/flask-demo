# -*- coding: utf-8 -*-

import json
import time
import hashlib
import functools
import requests
import base64
import datetime

from app.constants import CreditUri as const
from app.config import Config

from app.core.logger import project_logger
from app.core.aes import AESHelper
from app.core.functions import querystring

from app.models.mongos import  SingleSearch
from app.credit.asyncreq import async_request
from app.databases import session_scope
from app.models.sqlas import InputApply
import requests
import urllib.parse
from app.user.function import ImgController
from app.config import Config
import traceback


def exeTime(func):
    """记录请求数据所花的时间"""

    @functools.wraps(func)
    def newFunc(*args, **kwargs):
        start_time = time.time()
        if 'flag' in kwargs:
            key = func.__name__ + '_' + kwargs['flag']
        else:
            key = func.__name__
        project_logger.info('[TIME|%s] [FUNCNAME|%s] [request args: %s]',
            datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            key,
            str(kwargs)
        )
        content = func(*args, **kwargs)
        back = {key: content}
        if not isinstance(content, dict):
            if isinstance(content, list):
                back = {key : content}
            else:
                try:
                    content = json.loads(content)
                except Exception as e:
                    project_logger.error('func {func_name} response error, \
                        can not json.loads, content: {content}'.format(
                        func_name=key, content=content))
                    back = {key: {}}
                else:
                    back = {key: content}

        project_logger.info("[GET][FUNCNAME|%s][RESPONSE|%s][TIME|%s][REQUEST|%s]",
            key, back, time.time()-start_time, str(kwargs))
        return back
    return newFunc


@exeTime
def tel_batch(**kwargs):
    """电商消费记录"""

    enc = AESHelper(Config.SECRET)
    url = querystring(const.TELURL, {"enc_m": enc.encrypt(kwargs.get("phone"))})
    response = async_request(url)
    return response


@exeTime
def portait_active(**kwargs):
    """金融用户画像"""

    url = querystring(const.PORTRAIT, {"enc_m": kwargs.get("phone")})
    response = async_request(url)
    return response


@exeTime
def credit_telrisklist(**kwargs):
    """电商高危接口请求"""

    url = querystring(const.TELRISKLIST, {"enc_m": kwargs.get("phone")})
    response = async_request(url)
    return response


@exeTime
def credit_manyplatcheck(**kwargs):
    """多平借贷"""

    url = querystring(const.MANYPLAT, {"enc_m": kwargs.get("phone")})
    response = async_request(url)
    return response


@exeTime
def credit_phoneblack(**kwargs):
    """手机号标注黑名单"""

    url = querystring(const.PHONEMARK, {"enc_m": kwargs.get("phone")})
    response = async_request(url)
    return response


@exeTime
def credit_phonedevicecheck(**kwargs):
    """手机号关联多账户"""

    url = querystring(const.PHONERLATE, {"enc_m": kwargs.get("phone")})
    response = async_request(url)
    return response


@exeTime
def credit_newsplatrisk(**kwargs):
    """信息平台高危清单"""

    url = querystring(const.INFODANGER, {"enc_m": kwargs.get("phone")})
    response = async_request(url)
    return response


@exeTime
def credit_phonemsgcheck(**kwargs):
    """手机活跃度综合校验"""

    url = querystring(const.PHONEACTIVE, {"enc_m": kwargs.get("phone")})
    response = async_request(url)
    return response


@exeTime
def credit_socialblacklist(**kwargs):
    """社交平台高位数据"""

    url = querystring(const.SOCIAL, {"enc_m": kwargs.get("phone")})
    response = async_request(url)
    return response


@exeTime
def channel_idcard(**kwargs):
    """身份验证"""

    if kwargs.get("name") and kwargs.get("id_num"):
        param = {"name": kwargs.get("name"), "idCard": kwargs.get("id_num")}
    else:
        return {'status': 'search'}
    url = querystring(const.IDCARDCHECK, param)
    response = async_request(url)

    return response


@exeTime
def channel_bankby3(**kwargs):
    """银行卡三要素验证"""

    if kwargs.get("name") and kwargs.get("id_num") and kwargs.get("bank_num"):
        param = {"name": kwargs.get("name"), "idCard": kwargs.get("id_num"), 'accountno': kwargs.get("bank_num")}
    else:
        return {'status': 'search'}
    url = querystring(const.BANK3, param)
    response = async_request(url)

    return response


@exeTime
def channel_name_card_account(**kwargs):
    """银行卡三要素验证"""

    if kwargs.get("name") and kwargs.get("id_num") and kwargs.get("bank_num"):
        param = {"name": kwargs.get("name"), "idCard": kwargs.get("id_num"), 'accountNo': kwargs.get("bank_num")}
    else:
        return {'status': 'search'}
    url = querystring(const.NameIdCardAccount, param)
    response = async_request(url)
    return response


@exeTime
def credit_netblacklist(**kwargs):
    """网贷逾期黑名单"""
    if kwargs.get("name") and kwargs.get("id_num"):
        param = {"cardNum": kwargs.get("id_num"), 'iname': kwargs.get("name")}
    elif kwargs.get("phone") and kwargs.get("name"):
        param = {"enc_m": kwargs.get("phone"), "iname": kwargs.get("name")}
    else:

        return {'status': 'search'}
    url = querystring(const.LOAN_OVER, param)
    response = async_request(url)

    return response


@exeTime
def credit_person(**kwargs):
    """失信黑名单"""

    if kwargs.get("name") and kwargs.get("id_num"):
        param = {"name": kwargs.get("name"), "idCard": kwargs.get("id_num")}
    else:
        return {'status': 'search'}
    url = querystring(const.FAITH, param)
    response = async_request(url)
    return response


@exeTime
def address_getbymobile(**kwargs):
    """地址信息查询"""

    if kwargs.get("address"):
        param = {"enc_m": kwargs.get("phone")}
    else:
        return {"status": "search"}
    url = querystring(const.ADDRESS, param)
    response = async_request(url)

    return response


@exeTime
def address_match(**kwargs):
    """地址匹配信息接口"""

    if kwargs.get("address"):
        param = {
            "enc_m": kwargs.get("phone"),
            'address': kwargs.get('address'),
        }
    else:
        return {"status": "search"}
    url = querystring(const.ADDRESSMATCH, param)
    response = async_request(url)

    return response


@exeTime
def firm_info(**kwargs):
    """企业工商信息查询"""

    if kwargs.get("enterprise"):
        param = {'company_name': kwargs.get("enterprise", "")}
    else:
        return {"Address": "", "EconKind": "", "Industry": "",
                "RegistCapi": "", "Status": "", "TermStart": "", "companyName": ""}
    url = querystring(const.FIRMINFO, param)
    response = async_request(url)
    return response


@exeTime
def credit_shixin(**kwargs):
    """失信网企业失信数据"""

    if kwargs.get("enterprise"):
        param = {'iname': kwargs.get("enterprise", "")}
    else:
        return []
    url = querystring(const.SHIXIN, param)
    response = async_request(url)
    return response


@exeTime
def firm_court(**kwargs):
    """法院公告信息"""

    if kwargs.get("enterprise"):
        param = {'company_name': kwargs.get("enterprise", "")}
    else:
        return []
    url = querystring(const.COURT, param)
    response = async_request(url)

    return response


@exeTime
def firm_judgment(**kwargs):
    """企业裁判文书信息"""

    if kwargs.get("enterprise"):
        param = {'company_name': kwargs.get("enterprise", "")}
    else:
        return []
    url = querystring(const.JUDGMENT, param)
    response = async_request(url)

    return response


@exeTime
def firm_zhixing(**kwargs):
    """企业被执行信息"""

    if kwargs.get("enterprise"):
        param = {'company_name': kwargs.get("enterprise", "")}
    else:
        return []
    url = querystring(const.ZHIXING, param)
    response = async_request(url)

    return response


@exeTime
def cellphone_get(**kwargs):
    """ 新的小视实名认证  """
    param = {
        "name": kwargs.get("name", ''),
        "idCard": kwargs.get("id_num", ''),
        "phone": kwargs.get("phone", "")
    }
    url = querystring(const.CELLPHONE, param)
    response = async_request(url)

    return response


@exeTime
def undesirable_info(**kwargs):
    """ 公安不良信息 """
    param = {
        "name": kwargs.get("name", ""),
        "idCard": kwargs.get("id_num", "") }
    url = querystring(const.UNDESIRABLE_INFO, param)
    response = async_request(url)
    return response


class DataError(Exception):
    """ 当调用第三方数据出现非法时，触发这个异常"""

    def __init__(self, k, **kwargs):
        super(DataError, self).__init__()
        self.__k = k
    def __str__(self):
        return str(self.__k)


def gen_param(product_code, partner_trade_no, product_param, have_pic=0):

    """
    生成json参数
    :param product_code:
    :param partner_trade_no:
    :param product_param:
    :param have_pic:
    :return:
    """
    json_data = dict(
        method=Config.METHOD,
        version=Config.VERSION,
        partner=Config.PARTNER,
        sign_type=Config.SIGN_TYPE,
        charset=Config.CHARSET,
        business_data=dict(
            product_code=product_code,
            partner_trade_no=partner_trade_no,
            product_param=product_param
        )

    )
    if have_pic == 1:
        json_data['business_data'].update({
            'have_pic': '1'
        })
    return json_data


def encrypt(param=None, sign_key=None, is_sha1=False):
    list_param = []

    for k in sorted(param.keys()):
        res = param[k]
        if isinstance(param[k], dict):
            res = json.dumps(param[k]).replace(' ', '')
        list_param.append("%s=%s" % (k, res))
    if is_sha1:
        list_param.extend(['key=%s' % (sign_key)])
    else:
        list_param.extend(['sign=%s' % (sign_key)])
    str_sign = '&'.join(list_param)

    # res = hashlib.sha1(str_sign).hexdigest()
    if is_sha1:
        res = hashlib.sha1(str_sign.encode('utf-8')).hexdigest()
        return res
    else:
        return str_sign


def trans_error_to_json(response):
    """is_success = F & error = OVER_MAX_VISIT_COUNT"""
    ret = {}
    result_list = response.replace(' ', '').split('&')
    for ele in result_list:
        key_value = ele.split('=')
        key, value = key_value[0], key_value[1]
        ret.update({key: value})
    return ret


def net_get_data_handle(url, data):
    """
    :param url:
    :param data:
    :return:
    """
    index = 1
    res = None
    while index < 2:  # 如果出现系统错误,是需要重试的
        res = async_request(url, data=data, method='post')
        if res.status_code == 600:
            return {}
        if res.status_code == 200 or res.status_code == '200':
            if 'SYSTEM_ERROR' in str(res.text):
                index += 1
                continue
            else:
                break
        index += 1

    # return res
    if 'success=F' in str(res.text):
        return trans_error_to_json(str(res.text))
    # 将里面有用的信息提取出来
    index = 0
    while index < len(res.text):
        if res.text[index] == '{':
            break
        index += 1

    last = len(res.text) - 1
    while last > -1:
        if res.text[last] == '}':
            break
        last -= 1

    ret = json.loads(res.text[index: last + 1])
    if 'result' in ret:
        ret['result'] = json.loads(ret['result'])
        return ret
    else:
        return {'result': {}}


def wrapper(name, trade_num, param, url=None, have_pic=0):
    """
    对加密和ulr构造进行封装
    :param name:
    :param kwargs.get("trade_num"):
    :param param:
    :param url:
    :return:
    """
    from app.config import Config as config
    trade_num = trade_num + config.REPEAT_NUM

    data = gen_param(name, trade_num, param, have_pic=have_pic)
    sign = encrypt(data, Config.SIGNKEY, is_sha1=True)
    paramn_sign = encrypt(data, sign, is_sha1=False)
    return net_get_data_handle(url or Config.URL, paramn_sign)


@exeTime
def mashang_negative(**kwargs):
    """负面信息接口"""

    def is_pass(kw):
        if kw.get('id_num', None) and kw.get('name', None) and \
                kw.get('phone', None):
            return True
        else:
            return False

    if is_pass(kwargs) is False:
        return {'is_pass': True}

    param = dict(
        username=kwargs.get("name"),
        id_card=kwargs.get("id_num"),
        phone_number=kwargs.get("phone"))
    if kwargs.get("machine_number"):
        param.update({'machine_number': kwargs.get("machine_number")})
    if kwargs.get("address"):
        param.update({"address": kwargs.get("address")})
    if kwargs.get("email"):
        param.update({"email": kwargs.get("email")})
    func_name = 'DPD_AF_02613'
    return wrapper(func_name, kwargs.get("trade_num") + 'negative', param)


@exeTime
def mashang_shixin(**kwargs):
    """ 失信详情 """

    def is_pass(kw):
        if kw.get('id_num', None) and kw.get('name', None):
            return True
        else:
            return False

    if is_pass(kwargs) is False:
        return {'is_pass': True}

    param = dict(
        username=kwargs.get("name"),
        id_card=kwargs.get("id_num"))
    # func_name = sys._getframe().f_code.co_name
    func_name = 'DPD_AF_02610'
    return wrapper(func_name, kwargs.get("trade_num") + 'shixin', param)


@exeTime
def mashang_idcard(**kwargs):
    """ 简项身份核查"""

    # def is_pass(kw):
    #     if kw.get('id_num', None) and kw.get('name', None):
    #         return True
    #     else:
    #         return False

    # if is_pass(kwargs) is False:
    #     return {'is_pass': True}

    # param = dict(
    #     username=kwargs.get("name"),
    #     id_card=kwargs.get("id_num"))
    # if kwargs.get("phone"):
    #     param.update({'phone_number': kwargs.get("phone")})

    # func_name = 'DPD_AF_01501'
    # return wrapper(func_name, kwargs.get("trade_num") + 'idcard', param)
    # 因为临时紧急问题, 马上接口进行了更换
    param = {"idCard": kwargs.get("id_num"), "name": kwargs.get("name")}
    url = querystring(const.NEW_IDCARD_VERIFY, param)
    response = async_request(url)
    project_logger.info("resport_verify result %s" % str(response))
    try:
        result = json.loads(response).get("data", {}).get("resCode", "")
    except:
        result = -1

    if result == '2010' or result == 2010:
        result = "一致"
    else:
        result = "不一致"

    return {
        "result": {
            "MC_IDENT_IDS": {"IDENT_NAME": result}
        }}


@exeTime
def mashang_score(**kwargs):
    """ 信用评分 """

    def is_pass(kw):
        if kw.get('id_num', None) and kw.get('name', None) and \
                kw.get('phone', None) and kw.get('bank_num'):
            return True
        else:
            return False

    if is_pass(kwargs) is False:
        return {'is_pass': True}

    param = dict(
        username=kwargs.get("name"),
        id_card=kwargs.get("id_num"),
        card_number=kwargs.get("bank_num"),
        phone_number=kwargs.get("phone"))
    func_name = 'DPD_AF_02605'
    return wrapper(func_name, kwargs.get("trade_num") + 'score', param)


@exeTime
def mashang_overdue(**kwargs):
    """ 逾期信息 """

    def  is_pass(kw):
        if kw.get('id_num', None) and kw.get('name', None) and \
                kw.get('phone', None):
            return True
        else:
            return False

    if is_pass(kwargs) is False:
        return {'is_pass': True}

    param = dict(
        id_card=kwargs.get("id_num"),
        username=kwargs.get("name"),
        phone_number=kwargs.get("phone"))
    func_name = 'DPD_AF_02609'
    return wrapper(func_name, kwargs.get("trade_num") + 'overdue', param)


@exeTime
def mashang_online(**kwargs):
    """ 小视在网时长 """
    param = {
        "phone": kwargs.get("phone", ""),
        "name": kwargs.get("name", ""),
        "idCard": kwargs.get("id_num", "")}
    url = querystring(const.XIAOSHI_ONLINE, param)
    response = async_request(url)
    return response


@exeTime
def mashang_credit(**kwargs):
    """ 综合反欺诈 """

    def is_pass(kw):
        if kw.get('id_num', None) and kw.get('name', None) and \
                kw.get('phone', None):
            return True
        else:
            return False
    if is_pass(kwargs) is False:
        return {'is_pass': True}

    param = dict(
        id_card=kwargs.get("id_num"),
        username=kwargs.get("name"),
        phone_number=kwargs.get("phone"))
    if kwargs.get("machine_number"):
        param.update({
            "matchine_number": kwargs.get("machine_number")
        })
    if kwargs.get("address"):
        param.update({
            "address": kwargs.get("address")
        })
    if kwargs.get("email"):
        param.update({"email": kwargs.get("email")})
    func_name = 'DPD_AF_02608'
    return wrapper(func_name, kwargs.get("trade_num") + 'credit', param)


@exeTime
def mashang_phone(**kwargs):
    """ 手机实名认真, 用作统计"""
    return {}


@exeTime
def mashang_face(**kwargs):
    """ 人脸验证 """
    trade = kwargs.get('trade_num')

    data = None

    with session_scope() as session:
        obj = session.query(InputApply).filter_by(id=int(trade)).first()
        if obj and obj.photo_with_card:
            try:
                url = urllib.parse.urlparse(obj.photo_with_card)
                cookie = {
                    'userId': obj.input_user.id,
                    "companyId": obj.input_user.company_id
                }
                # 需要从redis中去循环获取所有的 key 然后比较 companyId 和UserId是否一样
                resid_img = ImgController()

                def trans_class_to_dict(src):
                    dest ={}
                    for k, v in src.__dict__.items():
                        if  not k.endswith("__"):
                            dest[k] = v
                    return dest

                resid_img.init_connect(trans_class_to_dict(Config))
                all_keys = resid_img.get_keys()
                dest_key = None
                for key in all_keys:

                    value = resid_img.get_key_value(key)

                    if isinstance(value, bytes):
                        value = value.decode("utf-8")
                    value = json.loads(value) if value else {}

                    if value.get("companyId", None) == cookie['companyId']:
                        dest_key = key
                        break

                ctoken = dest_key.decode("utf-8")

                ret = requests.get(Config.CREDIT_DOMAIN + url.path, headers={'Cookie': "ctoken={}".format(ctoken)})

                try:
                    data = ret.json()
                    if data:
                        data = None
                except:
                    data = ret.content
            except Exception as e:
                traceback.print_exc()
                data = None

    if data is None:
        data = bytes()

    def is_pass(data, kw):
        if kw.get('id_num', None) and kw.get('name', None) and  data:
            return True
        else:
            return False

    if is_pass(data, kwargs) is False:
        return {'is_pass': True}
    param = dict(
            id_card=kwargs.get("id_num"),
            username=kwargs.get("name"),
            image=base64.b64encode(data).decode("utf-8"),
            image_type=kwargs.get("image_type", "1")
           )
    func_name = 'DPV_AF_00401'
    return wrapper(func_name, kwargs.get("trade_num") + 'face', param, Config.FACE_URL, have_pic=1)


@exeTime
def youla_face(**kwargs):
    trade_num = kwargs.get("trade_num")
    param = {"name": kwargs.get("name", ""), "idCard": kwargs.get("id_num", "")}
    url_face, form_data = querystring(const.YOULA_FACE, param, method='POST')
    data = None
    with session_scope() as session:
        obj = session.query(InputApply).filter_by(id=int(trade_num)).first()
        if obj and obj.photo_with_card:
            try:
                url = urllib.parse.urlparse(obj.photo_with_card)
                cookie = {
                    'userId': obj.input_user.id,
                    "companyId": obj.input_user.company_id
                }
                # 需要从redis中去循环获取所有的 key 然后比较 companyId 和UserId是否一样
                resid_img = ImgController()

                def trans_class_to_dict(src):
                    dest = {}
                    for k, v in src.__dict__.items():
                        if not k.endswith("__"):
                            dest[k] = v
                    return dest

                resid_img.init_connect(trans_class_to_dict(Config))
                all_keys = resid_img.get_keys()
                dest_key = None
                for key in all_keys:

                    value = resid_img.get_key_value(key)

                    if isinstance(value, bytes):
                        value = value.decode("utf-8")
                    value = json.loads(value) if value else {}

                    if value.get("companyId", None) == cookie['companyId']:
                        dest_key = key
                        break

                ctoken = dest_key.decode("utf-8")

                ret = requests.get(Config.CREDIT_DOMAIN + url.path, headers={'Cookie': "ctoken={}".format(ctoken)})
                project_logger.warning("apply_num: %s JAVA IMG CONTENT: %s" % (trade_num, ret.text))
                try:
                    data = ret.json()
                    if data:
                        data = None
                except:
                    data = ret.content
            except Exception as e:
                traceback.print_exc()
                data = None
    if data is None:
        data = bytes()
    img = base64.b64encode(data)
    param.update({"image": img})
    data = async_request(url_face, data=form_data, method='post')
    project_logger.info('[TIME|%s] [FUNCNAME|%s] [request args: %s] [RESULT|%s]',
                        datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'youlaface',
                        str(kwargs),
                        str(data.text)
                        )
    try:
        data = json.loads(data.text)
        score = data.get("data", {}).get('data', {}).get("score", "")
        score = '%.2f' % float(score)
    except Exception:
        traceback.print_exc()
        project_logger.warning("\nface api rec data is %s" % str(data))
        score = ''
    template = {"result": {"MC_PI": {"SCORE_IDENT": score}}}
    return template


@exeTime
def net_loan_overdue_platforms(**kwargs):
    """ 网贷逾期多平台 """
    param = {
        "name": kwargs.get("name", ""),
        "idCard": kwargs.get("id_num", "") }
    url = querystring(const.NET_LOAN_PLATFORMS, param)
    response = async_request(url)
    return response


@exeTime
def net_loan_risk_check(**kwargs):
    """ 网贷风险校验 """
    param = {
        "name": kwargs.get("name", ""),
        "idCard": kwargs.get("id_num", ""),
        "phone": kwargs.get("phone")
    }
    url = querystring(const.NET_LOAN_RISK_CHECK, param)
    response = async_request(url)
    return response


@exeTime
def blacklist_check_query(**kwargs):
    """ 黑名单校验  """
    param = {
        "name": kwargs.get("name", ""),
        "idCard": kwargs.get("id_num", ""),
        "phone": kwargs.get("phone", '')}

    url = querystring(const.BLACKLIST_CHECK , param)
    response = async_request(url)
    return response


@exeTime
def user_contact_info(**kwargs):
    """ 用户关联信息校验 """
    param = {
        "idCard": kwargs.get("id_num", ""),
        "phone": kwargs.get("phone", '')}

    url = querystring(const.USERCONTACT_INFO, param)
    response = async_request(url)
    return response


@exeTime
def user_queryed_info(**kwargs):
    """ 用户被查询记录 """
    param = {
        "idCard": kwargs.get("id_num", ""),
        "phone": kwargs.get("phone", '')}

    url = querystring(const.USERQUERYED_INFO, param)
    response = async_request(url)
    return response


@exeTime
def operator_black(**kwargs):
    """请求第三方运营商数据"""
    return {}


@exeTime
def test1(**kw):
    rest = async_request('http://127.0.0.1:5000/1')
    return rest


@exeTime
def test2(**kw):
    rest = async_request('http://127.0.0.1:5000/2')
    return rest


@exeTime
def obtain_riskinfocheck(**kwargs):
    """不良信息查询W1（维氏盾）"""
    param = {
        "name": kwargs.get("name", ""),
        "idCard": kwargs.get("id_num", ""),
    }
    url = querystring(const.OBTAIN_RISKINFOCHECK, param)
    response = async_request(url)
    return response


@exeTime
def operator_phonetime(**kwargs):
    """手机号在网时长W1（中诚信）"""
    param = {
        "name": kwargs.get("name", ""),
        "idCard": kwargs.get("id_num", ""),
        "phone": kwargs.get("phone", ""),
    }
    url = querystring(const.OPERATOR_PHONETIME, param)
    response = async_request(url)
    return response


@exeTime
def operator_multiplatform(**kwargs):
    """多平台借贷W1（卧龙）"""
    param = {
        "phone": kwargs.get("phone", ""),
    }
    url = querystring(const.OPERATOR_MULTIPLATFORM, param)
    response = async_request(url)
    return response


@exeTime
def obtain_loanintegration(**kwargs):
    """信贷整合查询W1"""

    param = {
        "phone": kwargs.get("phone", ""),
    }
    url = querystring(const.OBTAIN_LOANINTEGRATION, param)
    response = async_request(url)
    return response


@exeTime
def obtain_loanriskinquiry(**kwargs):
    """借款人风险查询W1"""

    param = {
        "phone": kwargs.get("phone", ""),
        "name": kwargs.get("name", ""),
        "idCard": kwargs.get("id_num", ""),
    }
    url = querystring(const.OBTAIN_LOANRISKINQUIRY, param)
    response = async_request(url)
    return response


@exeTime
def obtain_piccompare(**kwargs):
    """人像相似度对比验证W1"""

    trade = kwargs.get('trade_num')

    data = None

    with session_scope() as session:
        obj = session.query(InputApply).filter_by(id=int(trade)).first()
        if obj and obj.photo_with_card:
            try:
                def trans_class_to_dict(src):
                    dest ={}
                    for k, v in src.__dict__.items():
                        if not k.endswith("__"):
                            dest[k] = v
                    return dest

                ret = requests.get(obj.photo_with_card, timeout=5)

                try:
                    data = ret.json()
                    if data:
                        data = None
                except:
                    data = ret.content
            except Exception as e:
                traceback.print_exc()
                data = None

    if data is None:
        data = bytes()

    def is_pass(data, kw):
        if kw.get('id_num', None) and kw.get('name', None) and data:
            return True
        else:
            return False

    # if is_pass(data, kwargs) is False:
    #     return {'is_pass': True}
    param = dict(
        idCard=kwargs.get("id_num"),
        name=kwargs.get("name"),
    )
    url, fuck = querystring(const.OBTAIN_PICCOMPARE, param, method="post")
    fuck["image"] = json.dumps([base64.b64encode(data).decode("utf-8"), ])
    response = async_request(url, method="post", data=fuck, dont_dump=True)
    return response
