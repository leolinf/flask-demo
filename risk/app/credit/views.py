# -*- coding: utf-8 -*-

import json
import traceback
import time
import requests

from sqlalchemy.orm import scoped_session
from flask_restful import Resource
from flask import g, jsonify, request

from app.core.baidu import BaiduMap
from app.models.sqlas import InputApply
from app.databases import Session
from flask import current_app

from app.bases import BaseResource
from .managers import CreditManager, RiskManager
from app.core.logger import project_logger, trace_view, class_logger
from app.core.functions import make_response, get_from_cache, querystring
from app.models.mongos import SingleSearch, Caching, BreakRule
from app.constants import Code, CreditUri, SearchStatus, TelPrice as const, Status
from .pipeline import (
    firm_info, firm_court, firm_shixin,
    firm_zhixing, firm_judgment, phone_mark_enterprise,
    contact_area_list
)
from .parsers import (
    creditlist_parser, risk_evaluation,
    credit_single_result, operator_parser, capcha_parser,
    address_parser, pdf_download_parser,
    taobao_parser, social_parser, fund_parser, bank_parser,
    break_rule_parser)
from flask import send_file
from io import BytesIO
from app.config import Config
from .managers import InputShow
from .utils import check_whether_self
from .forcache import (
    cache_operator_view, cache_search_result_view, cache_msg_record_view,
    cache_call_record_view, cache_tel_consume_view, cache_address_verify_view,
    cache_token_status_view
)
from app.user.function import login_required, current_user
from .taobao import handler_data


class CreditListView(BaseResource):

    @login_required
    def post(self):
        """信用报告列表"""

        req = creditlist_parser.parse_args()

        session = scoped_session(Session)

        page = req['page']
        count = req['count']
        number = req['number']
        approveEndTime = req['approveEndTime']
        approveStartTime = req['approveStartTime']
        approvePeriod = req['approvePeriod']
        approveTimeSort = req['approveTimeSort']
        intoEndTime = req['intoEndTime']
        intoPeriod = req['intoPeriod']
        intoStartTime = req['intoStartTime']
        intoTimeSort = req['intoTimeSort']
        isBreakRule = req['isBreakRule']
        searchStatus = req['searchStatus']
        approveStatus = req['approveStatus']
        localState = req['localState']

        credit_manager = CreditManager(session)

        credits, total = credit_manager.get_list(
                current_user.company_id,
                offset=(page - 1) * count,
                limit=count,
                number=number,
                intoTimeSort=intoTimeSort,
                approveTimeSort=approveTimeSort,
                intoPeriod=intoPeriod,
                intoStartTime=intoStartTime,
                intoEndTime=intoEndTime,
                approvePeriod=approvePeriod,
                approveStartTime=approveStartTime,
                approveEndTime=approveEndTime,
                isBreakRule=isBreakRule,
                searchStatus=searchStatus,
                approveStatus=approveStatus,
                localState=localState,
            )

        session.remove()

        return make_response(data={
            'antiFraudList': credits,
            'total': total,
        })


class InputApplyShowView(BaseResource):
    """ 进件申请表
     url: /api/Into_pieces/
    """
    def sub_mod_field_f(self, sub_mod_obj, s_mod_name, s_mod_key, s_mod_index, field_index, data):
        sub_key = s_mod_key

        if sub_key not in sub_mod_obj:
            sub_mod_obj[sub_key] = {}
            sub_mod_obj[sub_key]['lists'] = []

        sub_mod_obj[sub_key]['name'] = s_mod_name
        sub_mod_obj[sub_key]['index'] = s_mod_index
        sub_mod_obj[sub_key]['lists'].append(
            {
                "name": data['name'],
                "key": data['key'],
                "isShow": data['isShow'],
                "mustWrite": data['isRequired'], #data['isRequired'],
                "type": data['type'], #data['typeChoice'],
                # "unchanged": data['unchanged'], #data['changable'],
                'isExt': data.get('isExt', 0) or 0,
            })
    def trans_dict_to_list_by_key(self, src):
        l, dict_obj= [], {}
        for key in src.keys():
            dict_obj.clear()
            dict_obj.update({
                "key": key,
                **src[key]})
            l.append(dict_obj.copy())
        return l

    @login_required
    def get(self):
        from flask import request
        import json
        session = Session()
        input_id = request.args.get("id")
        # input_id = '17030810010002'
        from .managers import InputApplyManager
        input_apply_obj = InputApplyManager.get_by_id(session, input_id)
        search = SingleSearch.objects(apply_number=input_id).first()
        if not input_apply_obj:
            return make_response(status=Code.UNVALID_INPUT_ID)

        format_data = input_apply_obj.apply_table_snapshot
        app_table_obj = json.loads(format_data)
        # modules_list = []
        from collections import OrderedDict
        sub_mod_field = OrderedDict()
        for each_module in sorted(app_table_obj['modules'], key=lambda x: x['index']):
            for each_page in each_module['pages']:
                for index_, s_mod in enumerate(each_page['modulars']):
                    for field_index, each_field in enumerate(sorted(s_mod['fields'], key=lambda x:x['fieldIndex'])):
                        self.sub_mod_field_f(sub_mod_field, s_mod['name'], s_mod['key'], index_, field_index, each_field)
        result_json_foramt = sub_mod_field

        result = InputShow.format_input_info(session, result_json_foramt, input_apply_obj, search)
        return make_response(data={"modules": result})


@trace_view
class OperatorView(Resource):
    """运营商基本信息"""

    # @login_required
    @login_required
    def get(self, *args, **kwargs):

        req = credit_single_result.parse_args(strict=True)
        cache = get_from_cache(req['id'], 'operator_view')
        if cache:
            return make_response(cache)

        session = scoped_session(Session)
        result = cache_operator_view(session, req)
        session.remove()

        if isinstance(result, int):
            return result

        return make_response(data=result)


@trace_view
class MsgRcoredView(Resource):
    """运营商短信记录"""

    #@login_required
    @login_required
    def get(self, *args, **kwargs):

        req = operator_parser.parse_args(strict=True)
        cache = get_from_cache(req['id'], 'msg_record_view')
        session = scoped_session(Session)
        if cache:
            page = req['page']
            count = req['count']
            start = (page - 1) * count
            is_mark = req['isMark']
            token = req['token']
            total = cache['total']

            if token:
                start = 0
                count = total
                result = cache['msgDetail']
            elif is_mark == 1:
                result = [i for i in cache['msgDetail'] if i['identifyInfo'] or i['label']]
                cache['total'] = cache['totalRemark']
            else:
                result = cache['msgDetail']
            cache['msgDetail'] = result[start:start + count]
            return make_response(cache)

        result = cache_msg_record_view(session, req)
        session.remove()

        if isinstance(result, int):
            return result

        return make_response(
            data=result
        )


@trace_view
class TokenStatusView(BaseResource):
    """
    运营商的状态
    url: /api/capcha/operator_status/
    """
    # @login_required
    @login_required
    def get(self):
        req = credit_single_result.parse_args(strict=True)
        #cache = get_from_cache(req['id'], 'token_status_view')
        #if cache:
        #    return make_response(cache)
        session = scoped_session(Session)
        res = cache_token_status_view(session, req)
        session.remove()
        return jsonify({"code": Code.SUCCESS, 'data': res})


@trace_view
class CallRcoredView(Resource):
    """运营商通话记录"""

    # @login_required
    @login_required
    def get(self, *args, **kwargs):
        req = operator_parser.parse_args(strict=True)
        cache = get_from_cache(req['id'], 'call_record_view')
        if cache:
            page = req['page']
            count = req['count']
            start = (page - 1) * count
            end = start + count
            is_mark = req['isMark']
            token = req['token']
            total = cache['total']

            if token:
                start = 0
                count = total
                result = cache['callDetail']
            elif is_mark == 1:
                result = [i for i in cache['callDetail'] if i['identifyInfo'] or i['label']]
                cache['total'] = cache['totalRemark']
            else:
                result = cache['callDetail']
            cache['callDetail'] = result[start:start + count]
            return make_response(cache)

        session = scoped_session(Session)
        data = cache_call_record_view(session, req)
        session.remove()
        if isinstance(data, int):
            return make_response(status=data)

        return make_response(data=data)


@trace_view
class ContactAreaView(Resource):
    """联系人区域分析"""

    # @login_required
    @login_required
    def get(self, *args, **kwargs):

        req = operator_parser.parse_args(strict=True)
        single_search = SingleSearch.objects(apply_number=req["id"]).first()
        if not single_search:
            return make_response(status=Code.SINGLE_NOT_EXIST)
        if not check_whether_self(single_search):
            return make_response(status=Code.NOT_ALLOWED)

        search_list, total = contact_area_list(req, single_search.operator_data)
        return make_response(
            data={
                'contactAreaInfo': search_list,
                'total': total,
            }
        )


class SearchResultView(Resource):

    #@login_required
    @login_required
    def get(self):
        """单条查询记录"""

        req = credit_single_result.parse_args(strict=True)

        cache = get_from_cache(req['id'], 'search_result_view')
        if cache:
            return make_response(cache)

        session = scoped_session(Session)
        data = cache_search_result_view(session, req)
        session.remove()
        if isinstance(data, int):
            return make_response(status=data)

        return make_response(data=data)


class TelConsumeView(Resource):
    """电商消费记录"""

    #@login_required
    @login_required
    def get(self):
        req = credit_single_result.parse_args(strict=True)
        cache = get_from_cache(req['id'], 'tel_consume_view')
        if cache:
            return make_response(cache)

        session = scoped_session(Session)
        data = cache_tel_consume_view(session, req)
        session.remove()
        if isinstance(data, int):
            return make_response(status=data)

        return make_response(data=data)


class EnterpriseView(Resource):
    """企业信息接口数据"""

    # @login_required
    @login_required
    def get(self):

        req = credit_single_result.parse_args(strict=True)

        single_search = SingleSearch.objects(apply_number=req["id"]).first()
        if not single_search:
            return make_response(status=Code.SINGLE_NOT_EXIST)
        if not check_whether_self(single_search):
            return make_response(status=Code.NOT_ALLOWED)
        result = {}
        data = single_search.enterprise
        result["CourtAnnouncements"] = firm_court(data.get("Court"))
        result["CreditCode"] = firm_judgment(data.get("Judgment"))
        result["ShiXing"] = firm_shixin(data.get("ShiXing"))
        result["ZhiXing"] = firm_zhixing(data.get("ZhiXing"))
        result["baseInfo"] = firm_info(data.get("baseInfo"), single_search.enterprise_addr)
        result["companyVerify"] = {"companyName": single_search.enterprise_name,
                                   "markCompany": phone_mark_enterprise(single_search.phone_mark_blaklist),
                                   "weiboCompany": ""}
        if not single_search.enterprise_name:
            result["baseInfo"] = {
                    "Address":"", "EconKind":"", "Industry":"", "RegistCapi": "",
                    "Status": "", "TermStart": "", "companyName": "", "OperName": "",
                }
            return make_response(data=result)
        else:
            if not result["baseInfo"]["companyName"]:
                result["baseInfo"]["companyName"] = single_search.enterprise_name
                result["baseInfo"]["Address"] = single_search.enterprise_addr
                return make_response(data=result)
            else:
                result["baseInfo"]["Address"] = single_search.enterprise_addr
                return make_response(data=result)


@trace_view
@class_logger
class ConfirmView(BaseResource):
    """
    确认进行去查询
    url: /api/credit/query
    """
    @login_required
    def post(self):
        from task.tasks import single_credit

        session = scoped_session(Session)
        req = request.json
        input_apply_id = req["InputId"]
        obj = session.query(InputApply).filter(InputApply.id==input_apply_id).first()
        if not obj:
            return make_response(status=Code.DOES_NOT_EXIST)
        try:
            work_addr = json.loads(obj.work_address)
            work_addr_join = ''.join(work_addr)
        except:
            work_addr_join = ''

        work_address = '{0}{1}'.format(
            work_addr_join,
            obj.work_detail_address if obj.work_detail_address else ''
        )
        try:
            home_addr = json.loads(obj.home_live_address)
            home_addr_join = ''.join(home_addr)
        except:
            home_addr_join = ''

        home_address = '{0}{1}'.format(
            home_addr_join,
            obj.home_detail_address if obj.home_detail_address else ''
        )
        kwargs = {
            "phone": obj.phone,
            "name": obj.name,
            "id_num": obj.idcard,
            "enterprise": obj.work_company_name or "",
            "address": home_address,
            "bank_num": obj.bank_num if obj.bank_num else obj.banknum,
            "trade_num": str(obj.id),
            "email": obj.email or "",
            "machine_number": "",
            "image_type": "1",
            "image": "",
            "school_phone": obj.school_contact_phone,
            'home_phone': obj.home_mem_phone,
            'work_phone': obj.work_contact_phone,
            'work_address': work_address,
        }

        permissions = obj.merchant.company.permissions
        func_list = list(set([i['func_name'] for i in json.loads(permissions)]))

        obj.permissions_snapshot = permissions
        obj.search_status = SearchStatus.DOING
        obj.status = Status.SEARCHING
        obj.operator = 1 if obj.token else 0
        session.add(obj)

        SingleSearch.objects(apply_number=obj.id).update(
            upsert=True,
            set__apply_number=obj.id,
            set__name=obj.name,
            set__phone=obj.phone,
            set__id_num=obj.idcard,
            set__bank_num=obj.bank_num if obj.bank_num else obj.banknum,
            set__company_id=obj.merchant.company_id,
            set__merchant_num=obj.merchant.id,
            set__create_time=obj.create_time,
            set__permission_func=func_list,
            set__phone_home=kwargs['home_phone'],
            set__phone_work=kwargs['work_phone'],
            set__phone_school=kwargs['school_phone'],
        )

        single_credit.apply_async(
            queue=current_app.config['ANTI_QUEUE'],
            args=(obj.id, obj.input_user.company_id, func_list),
            kwargs=(kwargs) )
        try:
            session.commit()
        except Exception as e:
            traceback.print_exc()
            session.rollback()
        finally:
            session.remove()
        return make_response()


class RiskEvaluationView(BaseResource):

    @login_required
    def get(self):
        """贷前风险评估"""

        req = risk_evaluation.parse_args()
        search_id = req['id']

        session = scoped_session(Session)
        risk_manager = RiskManager(session)
        res = risk_manager.risk_evaluation(search_id)
        session.remove()

        if res == 'not exist':
            return make_response(status=Code.SEARCH_NOT_EXIST)

        if res == 'not allowed':
            return make_response(status=Code.NOT_ALLOWED)

        return make_response(res)


class CapchaToken(Resource):
    """摩蝎运营商对接"""

    def post(self, *args, **kwargs):
        """保存进件系统 传过来的token 和status 值"""
        from task.tasks import capcha_info_token
        session = scoped_session(Session)
        req = capcha_parser.parse_args(strict=True)
        #if request.headers.get("auth") != CreditUri.KEY:
        #    project_logger.warn("[%s][%s][*********]", str(req), request.headers.get("auth"))
        #    return make_response(status=Code.SINGLE_NOT_EXIST)

        input_apply = session.query(InputApply).filter(
                InputApply.md_order == req["user_id"]).first()
        # 触发查询任务
        if not input_apply:
            project_logger.warn("[INPUTAPPLY][%s][########]", str(req))
            return make_response(status=Code.SINGLE_NOT_EXIST)
        phone = input_apply.phone
        apply_number = input_apply.id

        capcha_info_token.apply_async(
            queue=current_app.config['ANTI_QUEUE'],
            args=(apply_number, phone, req["task_id"], Config.MOJIE_TOKEN),
            kwargs=kwargs
        )
        project_logger.info('task_id:运营商{0}回调成功{1}'.format(req['task_id'], req["user_id"]))
        return {"code": Code.SUCCESS}, 201


class SocialToken(Resource):
    """摩蝎社保对接"""

    def post(self, *args, **kwargs):
        """保存进件系统 传过来的token 和status 值"""
        from task.tasks import social_info_token, social_detail_token
        session = scoped_session(Session)
        req = social_parser.parse_args(strict=True)
        #if request.headers.get("auth") != CreditUri.KEY:
        #    project_logger.warn("[%s][%s][*********]", str(req), request.headers.get("auth"))
        #    return make_response(status=Code.SINGLE_NOT_EXIST)

        # 触发查询任务
        input_apply = session.query(InputApply).filter(
                InputApply.md_order == req["user_id"]).first()
        if not input_apply:
            project_logger.warn("[SOCIAL][INPUTAPPLY][%s][########]", str(req))
            return make_response(status=Code.SINGLE_NOT_EXIST)
        phone = input_apply.phone
        apply_number = input_apply.id

        social_info_token.apply_async(
            queue=current_app.config['ANTI_QUEUE'],
            args=(apply_number, phone, req["task_id"], Config.MOJIE_TOKEN),
            kwargs=kwargs
        )
        social_detail_token.apply_async(
            queue=current_app.config['ANTI_QUEUE'],
            args=(apply_number, phone, req["task_id"], Config.MOJIE_TOKEN),
            kwargs=kwargs
        )
        project_logger.info('task_id:社保{0}回调成功{1}'.format(req['task_id'], req["user_id"]))
        return {"code": Code.SUCCESS}, 201


class FundToken(BaseResource):
    """摩蝎公积金对接"""

    def post(self, *args, **kwargs):
        """保存传进来的id和token"""

        from task.tasks import public_fund_token, public_detail_token
        session = scoped_session(Session)
        req = fund_parser.parse_args(strict=True)
        #if request.headers.get("auth") != CreditUri.KEY:
        #    project_logger.warn("[{}][{}][*********]".format(str(req), request.headers.get("auth")))
        #    return make_response(status=Code.SINGLE_NOT_EXIST)

        # 触发查询任务
        input_apply = session.query(InputApply).filter(
                InputApply.md_order == req["user_id"]).first()
        if not input_apply:
            project_logger.warn("[SOCIAL][INPUTAPPLY][%s][########]", str(req))
            return make_response(status=Code.SINGLE_NOT_EXIST)
        apply_number = input_apply.id

        public_fund_token.apply_async(
            queue=current_app.config['ANTI_QUEUE'],
            args=(apply_number, req["task_id"], Config.MOJIE_TOKEN),
            kwargs=kwargs
        )

        public_detail_token.apply_async(
            queue=current_app.config['ANTI_QUEUE'],
            args=(apply_number, req["task_id"], Config.MOJIE_TOKEN),
            kwargs=kwargs
        )
        project_logger.info('task_id:公积金{0}回调成功{1}'.format(req['task_id'], req["user_id"]))
        return {"code": Code.SUCCESS}, 201


class BankToken(BaseResource):
    """人行报告"""

    def post(self, *args, **kwargs):

        from task.tasks import bank_report_data
        session = scoped_session(Session)
        req = bank_parser.parse_args(strict=True)
        #if request.headers.get("auth") != CreditUri.KEY:
        #    project_logger.warn("[{}][{}][*********]".format(str(req), request.headers.get("auth")))
        #    return make_response(status=Code.SINGLE_NOT_EXIST)
        input_apply = session.query(InputApply).filter(
                InputApply.md_order == req["user_id"]).first()
        if not input_apply:
            project_logger.warn("[SOCIAL][INPUTAPPLY][%s][########]", str(req))
            return make_response(status=Code.SINGLE_NOT_EXIST)
        apply_number = input_apply.id
        bank_report_data.apply_async(
            queue=current_app.config['ANTI_QUEUE'],
            args=(apply_number, req["task_id"], Config.MOJIE_TOKEN),
            kwargs=kwargs
        )
        project_logger.info('task_id:人行报告{0}回调成功{1}'.format(req['task_id'], req["user_id"]))
        return {"code": Code.SUCCESS}, 201


class AddressVerifyView(BaseResource):

    #@login_required
    @login_required
    def get(self):
        """地址校验"""

        req = address_parser.parse_args()

        cache = get_from_cache(req['id'], 'address_verify_view')
        if cache:
            return make_response(cache)

        session = scoped_session(Session)
        res = cache_address_verify_view(session, req)
        session.remove()
        if isinstance(res, int):
            return make_response(status=res)

        return make_response(res)


class AddressSaveView(BaseResource):

    # @login_required
    @login_required
    def post(self):
        """地址保存"""

        # req = address_save.parse_args()
        # search_id = req['id']
        #
        # session = scoped_session(Session)
        # credit_manager = CreditManager(session)
        #
        # res = credit_manager.save_address(search_id, req.copy())
        # session.remove()
        #
        # return make_response(status=res)
        return make_response()


class PdfDownlaodView(BaseResource):
    """ pdf接口
     /api/presentation_pdf/
    """
    def get_url(self, url, token, args):
        # from urllib.request import
        from urllib.parse import urlencode
        project_logger.info("\ndownload token: %s", token.decode("utf-8"))
        def get_url(d):
            nonlocal  token
            c = {"token": token}
            if 'url' in d:
                d.pop('url')
            for key, value in d.items():
                c[key] = value
            return urlencode(c)

        # print("debug: ", url)
        if not url.endswith("?"):
            url = url + '?'
        url += get_url(args)
        print("\nrequest url: ", url)
        return url

    @login_required
    def get(self):
        """ 在这里需要配置一个用户可访问的 """
        req = pdf_download_parser.parse_args(strict=True)
        single_id = req['id']
        company_id, user_id = None, None
        from app.databases import session_scope
        user_name = None
        session = scoped_session(Session)
        with session_scope(session) as session:
            obj = session.query(InputApply).filter_by(id=single_id).first()
            if not obj:
                return make_response(status=Code.DOES_NOT_EXIST)
            company_id, user_id, user_name = obj.input_user.company_id, obj.input_user.id, obj.name
        from app.user.function import TokenAuth
        obj = {'id': req['id'], 'company_id': company_id}
        auth_obj = TokenAuth()
        try:
            auth_obj.redis_set({'id': req['id'], 'company_id': company_id})
        except Exception as ex:
            project_logger.warning('\nredis set pdfDownload error %s' % (str(ex)))
            return make_response(status=Code.SYSTEM_ERROR)
        # 向java服务器发送 html地址
        url = self.get_url(req['url'], auth_obj.encode_key(obj), req)

        ret = requests.post(
            Config.PDF_URL, data={"url": url},
            headers={"content-Type": 'application/x-www-form-urlencoded'}
        )
        if ret.status_code == 200:
            content = ret.content
            file_name = str(req['id']) + '_' + user_name + '_信用报告.pdf'
            return send_file(BytesIO(content), mimetype='application/pdf',
                             attachment_filename=file_name.encode("utf-8").decode("latin-1"), as_attachment=True)
        else:
            project_logger.error("java pdf download error, info| %s" %(str(ret.text)))
            return make_response(status=Code.SYSTEM_ERROR)


class JavaView(BaseResource):

    @login_required
    def post(self):

        data = request.get_json()

        project_logger.info('java透传时给的参数{0}'.format(data))

        if not data:
            project_logger.warn('没数据')
            project_logger.info(request.args)
            project_logger.info(request.form)
            project_logger.info(request.data)

        url = current_user.company.into_url.rstrip('/') + request.path

        try:
            start = time.time()
            r = requests.post(url, json=data, timeout=5)
            project_logger.info('java透传耗时{0}秒'.format(time.time() - start))
        except Exception as e:
            project_logger.error(e)
            res = {
                'code': Code.SYSTEM_ERROR,
            }
            return jsonify(res)

        try:
            res = r.json()
        except Exception as e:
            project_logger.error('status_code: {0}'.format(r.status_code))
            project_logger.error(r.text)
            project_logger.error(e)
            res = {
                'code': Code.SYSTEM_ERROR,
            }

        return jsonify(res)


@trace_view
class SocialResultView(Resource):
    """魔蝎社保卡信息"""

    @login_required
    def get(self, *args, **kwargs):

        req = credit_single_result.parse_args(strict=True)
        single_search = SingleSearch.objects(apply_number=req["id"]).first()
        if not single_search:
            return make_response(status=Code.SINGLE_NOT_EXIST)
        if not check_whether_self(single_search):
            return make_response(status=Code.NOT_ALLOWED)
        result = single_search.social_security_data
        original_result = single_search.social_security_original
        if result.get("code") == const.CODE and\
                original_result.get("code") == const.CODE:

            resp = result.get("data")
            resp.update({"original": original_result.get("data")})
            return make_response(data=resp)
        return make_response(status=Code.SINGLE_NOT_EXIST)


@trace_view
class PublicFundResultView(Resource):
    """魔蝎公积金信息"""

    @login_required
    def get(self, *args, **kwargs):

        req = credit_single_result.parse_args(strict=True)
        single_search = SingleSearch.objects(apply_number=req["id"]).first()
        if not single_search:
            return make_response(status=Code.SINGLE_NOT_EXIST)
        if not check_whether_self(single_search):
            return make_response(status=Code.NOT_ALLOWED)
        result = single_search.public_funds_data
        original_result = single_search.public_funds_original
        if result.get("code") == const.CODE and\
                original_result.get("code") == const.CODE:
            resp = result.get("data")
            resp.update({"original": original_result.get("data")})
            return make_response(data=resp)
        return make_response(status=Code.SINGLE_NOT_EXIST)


@trace_view
class BankReportView(Resource):
    """人行信息"""

    @login_required
    def get(self, *args, **kwargs):

        req = credit_single_result.parse_args(strict=True)
        single_search = SingleSearch.objects(apply_number=req["id"]).first()
        if not single_search:
            return make_response(status=Code.SINGLE_NOT_EXIST)
        if not check_whether_self(single_search):
            return make_response(status=Code.NOT_ALLOWED)
        result = single_search.bank_report_data
        if result.get("code") == const.CODE:
            return make_response(data=result.get("data"))
        return make_response(status=Code.SINGLE_NOT_EXIST)


@trace_view
class TaobaoView(Resource):
    """淘宝授权"""

    def get(self, *args, **kwargs):

        req = taobao_parser.parse_args(strict=True)
        apply_number=req["id"]
        if req['key'] != '9CsOEp8VovWFaOxr':
            project_logger.warn("[%s][%s][*********]", str(req), req)
            return make_response(status=Code.SINGLE_NOT_EXIST)

        url = querystring(CreditUri.TAOBAO_INFO, {"token": req["token"]}, platform="taobao")
        print(url)
        project_logger.warning("taotaotaotaotaobao{0}:{1}".format(apply_number, req))
        response = {}
        index = 0
        while index <= 3:
            try:
                response = requests.get(url, timeout=20).json()
                break
            except Exception as e:
                project_logger.warning("[taobaoURL|{}] [ERROR|{}]".format(url, str(e)))
                index += 1
                time.sleep(1)

        SingleSearch.objects(apply_number=apply_number).update(
            upsert=True,
            set__taobao_data=response,
            set__apply_number=apply_number,
        )
        #########################
        # 要更新地址校验那个东西。。。
        #########################
        if response.get("code") != 41000:
            return make_response(data={})

        single_search = SingleSearch.objects(apply_number=apply_number).first()
        resp = handler_data(response.get("data"), single_search.name, single_search.phone)
        address = resp["address"]
        if address:
            addr = address[0]
            address = "".join((addr["province"], addr["city"], addr["area"], addr["addressDetail"]))
        else:
            address = ""

        baidu = BaiduMap(Config.BAIDU_AK)
        # coordinates = query_location(address)
        coordinates = baidu.convert_address_to_coordinate(address)
        location = single_search.location
        if location:
            location["thirdCoordinates"] = coordinates
        # 正常情况都不会走到这一步
        else:
            location = {"thirdCoordinates": coordinates}

        single_search.update(
            set__location=location,
        )

        lc = baidu.convert_gps_to_utm(location.get("liveCoordinates"))
        tc = baidu.convert_gps_to_utm(coordinates)
        wc = baidu.convert_gps_to_utm(location.get("workCoordinates"))
        distance = single_search.location
        if distance:
                distance['live2third'] = baidu.calculate_distance(lc, tc)
                distance["third2work"] = baidu.calculate_distance(tc, wc)
        # 通常不会进入这一个if
        else:
            distance = {
                'live2third': baidu.calculate_distance(lc, tc),
                "third2work": baidu.calculate_distance(tc, wc)
            }

        SingleSearch.objects(apply_number=apply_number).update(
            set__distance=distance
        )

        session = scoped_session(Session)
        cache_address_verify_view(session, {'id': apply_number})
        # 清缓存
        Caching.objects(search_id=int(apply_number)).delete()
        # 重新缓存
        risk_manager = RiskManager(session)
        risk_manager.risk_evaluation(apply_number)
        session.remove()

        return make_response(data={})


@trace_view
class TaobaoReportView(Resource):
    """淘宝授权借口"""

    @login_required
    def get(self, *args, **kwargs):

        req = credit_single_result.parse_args(strict=True)
        single_search = SingleSearch.objects(apply_number=req["id"]).first()
        if not single_search:
            return make_response(status=Code.SINGLE_NOT_EXIST)
        if not check_whether_self(single_search):
            return make_response(status=Code.NOT_ALLOWED)
        result = single_search.taobao_data
        if result.get("code") == 41000:
            resp = handler_data(result.get("data"), single_search.name, single_search.phone)
            return make_response(data=resp)
        return make_response(status=Code.SINGLE_NOT_EXIST)


class BreakRuleView(Resource):
    """自动拒绝触犯规则"""

    @login_required
    def get(self):

        req = break_rule_parser.parse_args(strict=True)

        break_rule = BreakRule.objects(apply_number=req["id"]).first()

        if not break_rule:
            return make_response(status=Code.SINGLE_NOT_EXIST)

        if not break_rule.break_rule:
            res = []
        else:
            res = [{"key": i[0], "value": i[1]} for i in break_rule.break_rule]

        return make_response(data={"breakList": res})
