# -*- coding: utf-8 -*-

from flask_restful import reqparse


input_parser = reqparse.RequestParser()
input_parser.add_argument('phone', type=str, required=True, location='json')
input_parser.add_argument('apply_number', type=int, required=True, location='json')
input_parser.add_argument('userId', location='args', type=int)

creditlist_parser = reqparse.RequestParser()
creditlist_parser.add_argument('page', type=int, location='json', default=1)
creditlist_parser.add_argument('count', type=int, location='json', default=10)
creditlist_parser.add_argument('number', type=str, location='json')
creditlist_parser.add_argument('approveEndTime', location='json', type=int)
creditlist_parser.add_argument('approvePeriod', location='json', type=str, choices=('all', 'today', 'week', 'month'))
creditlist_parser.add_argument('approveStartTime', location='json', type=int)
creditlist_parser.add_argument('approveStatus', location='json', type=int)
creditlist_parser.add_argument('approveTimeSort', location='json', type=int)
creditlist_parser.add_argument('intoEndTime', location='json', type=int)
creditlist_parser.add_argument('intoPeriod', location='json', type=str, choices=('all', 'today', 'week', 'month'))
creditlist_parser.add_argument('intoStartTime', location='json', type=int)
creditlist_parser.add_argument('intoTimeSort', location='json', type=int, choices=(1, 2, 3))
creditlist_parser.add_argument('isBreakRule', location='json', type=int, choices=(-1, 0, 1))
creditlist_parser.add_argument('searchStatus', location='json', type=int)
creditlist_parser.add_argument('localState', location='json', type=int, choices=(0, 1, 2), default=0)
creditlist_parser.add_argument('userId', location='args', type=int)


# 信用报告查询
credit_single_result = reqparse.RequestParser(bundle_errors=True)
credit_single_result.add_argument('id', location='args', type=int, required=True)
credit_single_result.add_argument('token', location='args', type=str)
credit_single_result.add_argument('userId', location='args', type=int)

# 运营商请求参数
operator_parser = reqparse.RequestParser(bundle_errors=True)
operator_parser.add_argument('id', type=int, required=True)
operator_parser.add_argument("page", type=int, default=1)
operator_parser.add_argument("count", type=int, default=10)
operator_parser.add_argument("isMark", type=int, default=0)
operator_parser.add_argument('token', type=str)
operator_parser.add_argument('userId', location='args', type=int)

# 带钱风险评估
risk_evaluation = reqparse.RequestParser(bundle_errors=True)
risk_evaluation.add_argument('id', type=int, required=True)
risk_evaluation.add_argument('userId', location='args', type=int)

# 运营商的获取详细数据的token 和 status
capcha_parser = reqparse.RequestParser(bundle_errors=True)
capcha_parser.add_argument('task_id', location='json', type=str, required=True)
capcha_parser.add_argument('user_id', location='json', type=str)
capcha_parser.add_argument('mobile', location='json', type=str)
capcha_parser.add_argument('bills', location='json')
capcha_parser.add_argument('userId', location='args', type=int)

address_parser = reqparse.RequestParser(bundle_errors=True)
address_parser.add_argument('id', type=int, required=True, location='args')
address_parser.add_argument('userId', location='args', type=int)

address_save = reqparse.RequestParser(bundle_errors=True)
address_save.add_argument('id', type=int, required=True, location='json')
address_save.add_argument('bussiness2live', type=str, location='json')
address_save.add_argument('live2third', type=str, location='json')
address_save.add_argument('third2business', type=str, location='json')
address_save.add_argument('apply2business', type=str, location='json')
address_save.add_argument('apply2live', type=str, location='json')
address_save.add_argument('live2work', type=str, location='json')
address_save.add_argument('third2work', type=str, location='json')
address_save.add_argument('work2apply', type=str, location='json')
address_save.add_argument("token", type=str, location='json')
address_save.add_argument('userId', location='args', type=int)

# 信用报告下载pdf的接口
pdf_download_parser = reqparse.RequestParser(bundle_errors=True)
pdf_download_parser.add_argument('id', type=int, required=True)
pdf_download_parser.add_argument('url', type=str, required=True)
pdf_download_parser.add_argument('name', type=str, required=False)
pdf_download_parser.add_argument('intoNumber', type=str, required=True)
pdf_download_parser.add_argument('intoTime', type=str, required=True)
pdf_download_parser.add_argument('userId', location='args', type=int)

#淘宝授权
taobao_parser = reqparse.RequestParser(bundle_errors=True)
taobao_parser.add_argument("id", type=str, required=True)
taobao_parser.add_argument("token", type=str, required=True)
taobao_parser.add_argument("status", type=str, required=True)
taobao_parser.add_argument("key", type=str, required=True)

# 社保form处理token 和 status
social_parser = reqparse.RequestParser(bundle_errors=True)
social_parser.add_argument('task_id', location='json', type=str, required=True)
social_parser.add_argument('user_id', location='json', type=str)
social_parser.add_argument('username', location='json', type=str)
social_parser.add_argument('area_code', location='json',type=str)
social_parser.add_argument('timestamp', location='json')
social_parser.add_argument('result', location='json')
social_parser.add_argument('message', location='json',type=str)

# 社保form处理token 和 status
fund_parser = reqparse.RequestParser(bundle_errors=True)
fund_parser.add_argument('task_id', location='json', type=str, required=True)
fund_parser.add_argument('user_id', location='json', type=str)
fund_parser.add_argument('username', location='json', type=str)
fund_parser.add_argument('area_code', location='json',type=str)
fund_parser.add_argument('timestamp', location='json')
fund_parser.add_argument('result', location='json')
fund_parser.add_argument('message', location='json',type=str)

# 人行form处理token 和 status
bank_parser = reqparse.RequestParser(bundle_errors=True)
bank_parser.add_argument('user_id', location='json', type=str, required=True)
bank_parser.add_argument('task_id', location='json', type=str, required=True)
bank_parser.add_argument('mapping_id', location='json', type=str)
bank_parser.add_argument('result', location='json')
bank_parser.add_argument('message', location='json',type=str)
bank_parser.add_argument('report_no', location='json',type=str)

# 自动拒绝触犯规则
break_rule_parser = reqparse.RequestParser(bundle_errors=True)
break_rule_parser.add_argument('user_id', location='args', type=str, required=True)
break_rule_parser.add_argument('id', location='args', type=int, required=True)
