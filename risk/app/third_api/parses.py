# -*- coding: utf-8 -*-

from flask_restful import reqparse, inputs
import json
import traceback
telephone = inputs.regex(r'^1[0-9]\d{9}$')


# 身份证验证
verify_idcard = reqparse.RequestParser(bundle_errors=True)
verify_idcard.add_argument('userId', type=str, required=True)
verify_idcard.add_argument('idNum',  type=str, required=True)
verify_idcard.add_argument('name', type=str, required=True)
verify_idcard.add_argument('tradeNum', type=str, required=True)
verify_idcard.add_argument('userId', location='args', type=int)

# 短信模板
sms_template = reqparse.RequestParser(bundle_errors=True)
sms_template.add_argument("phone", type=telephone, required=True)
sms_template.add_argument("verifyCode", type=str, required=True)
sms_template.add_argument("companyId",type=str, required=True)
sms_template.add_argument('serviceType', type=int, default=1)
sms_template.add_argument('userId', location='args', type=int)
