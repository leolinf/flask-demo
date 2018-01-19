# -*- coding: utf-8 -*-
from app.bases import BaseResource
from flask_restful import request
from .parses import verify_idcard, sms_template

from .function import ThirdApiManager, pass_verify
from app.core.functions import make_response
from app.constants import Code
from app.core.logger import project_logger, trace_view, class_logger

from flask import request
import json
from flask import current_app
from app.databases import session_scope
from sqlalchemy import and_
from ..config import Config
from app.core.logger import project_logger
from app.core.functions import querystring
from app.constants import CreditUri as const
from app.credit.asyncreq import async_request


class VerifyIdCardView(BaseResource):
    """
    身份验证接口
    url: /api/verify_idcard
    """
    def post(self):
        req = verify_idcard.parse_args(strict=True)
        # req = json.loads(request.data.decode("utf-8"))
        # result = ThirdApiManager().mashang_idcard(**{
        #     "userId": req['userId'],
        #     'name': req['name'],
        #     'idNum': req['idNum'],
        #     'tradeNum': req['tradeNum']
        # })
        # project_logger.info("[order_id|{}] mashang_verify [result|{}]".format(
        #     req['userId'], str(result)))
        #if pass_verify(result) is False:
        param = {"idCard": req.get("idNum"), "name": req["name"]}
        url = querystring(const.NEW_IDCARD_VERIFY, param)
        response = async_request(url)
        project_logger.info("NEW ID_CARD VERIFY RESULT: %s" % str(response))
        try:
            result = json.loads(response).get("data", {}).get("resCode", "")
        except:
            result = -1

        if result == '2010' or result == 2010:
            ret = True
        else:
            ret = False
        if ret is False:
            return make_response(status=Code.VERIFY_FAIL)
        return  make_response(status=Code.SUCCESS)


@trace_view
class SendSmsView(BaseResource):
    """ 获取短信验证码
        url: /api/get_verify_code/
    """
    def post(self):
        from task.tasks import send_sms
        from app.models.sqlas import SmsTemplate

        req = sms_template.parse_args(strict=True)
        company_id = req['companyId']

        # 根据公司和业务类型来获取不同的短信模板
        template = None
        with session_scope() as session:
            obj = session.query(SmsTemplate).filter(
                and_(SmsTemplate.company_id==req['companyId'], SmsTemplate.service_type==req['serviceType'])).first()
            if obj:
                template = obj.template

        if template is None:
            return make_response(status=Code.VALID_COMPANY_SERVICE)

        # template = template.format(phone=req['phone'], code=req['verifyCode'])
        template = template.format(req['verifyCode'])
        send_sms.apply_async(
            queue=Config.SMS_QUEUE,
            args=[req['phone'], req['verifyCode'], template],
        )
        return make_response()
