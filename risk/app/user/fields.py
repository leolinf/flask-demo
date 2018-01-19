# -*- coding: utf-8 -*-

from flask_restful import fields


company_info = {
    'Id': fields.String(attribute="linkman_idcard"),  # 身份证号码
    'address': fields.String(attribute='test', default=""),
    'commerceNumber': fields.String(attribute="ic_code"),
    'contactName': fields.String(attribute="linkman_name"),
    'contactPhone': fields.String(attribute="linkman_phone"),
    'detailAddress': fields.String(attribute="address"),
    'name': fields.String(attribute="name"),
    'organizeCode': fields.String(attribute="org_code"),
    'taxNumber': fields.String(attribute="tax_code"),
    'contract':fields.String(attribute="test", default=""),     # 合同的名字
    'contractUrl': fields.String(attribute="contract_url"), # 合同附件下载url
    'officeSeal': fields.String(attribute="cachet_url"),
}
