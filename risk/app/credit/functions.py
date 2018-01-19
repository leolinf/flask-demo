# -*- coding:utf-8 -*-
import hashlib
import time

from flask import current_app
from mongoengine import NotUniqueError

from app.core.logger import project_logger
from app.constant import const
from app import models


def check_company(token):
    """进件验证:
    验证规则：
    1, token == company_id（公司id） + time_stamp(时间戳13位，单位ms)+
                            md5(company_id + time_stamp + auth_key)
        auth_key: 公司秘钥md5加密后存入数据库
    2, 同一个token只能使用一次
    """

    company_id = token[:3]
    time_stamp = token[3:16]
    password = token[16:]

    # 判断时间是否过期
    if time.time() * 1000 - int(time_stamp) > 300 * 1000:
        project_logger.warning("进件请求时间过期")
        return False
    # 判断是否已用
    if current_app.cache.get(company_id + time_stamp):
        project_logger.warning("进件重复请求")
        return False
    # 验证
    company_obj = models.Company.objects(company_id=company_id).first()
    if company_obj:
        secret_pass = get_md5(company_id + time_stamp + company_obj.auth_key)
        if secret_pass == password:
            # 添加缓存记录
            current_app.cache.set(key=company_id + time_stamp, value=1)
            return True

    project_logger.warning("进件请求token认证错误！")
    return False


def get_md5(password):
    md5 = hashlib.md5()
    md5.update(password.encode("utf-8"))
    return md5.hexdigest()


def add_company(name, password, company_id=None):
    auth_key = get_md5(password)
    if not company_id:
        latest_company = models.Company.objects.order_by('-company_id').first()
        if latest_company:
            max_id = latest_company.company_id
        else:
            max_id = 0
        company_id = "%03d" % (int(max_id) + 1)
    try:
        o = models.Company(name=name, company_id=company_id, auth_key=auth_key)\
            .save()
    except NotUniqueError:
        o = models.Company.objects(name=name).first()
        o.update(auth_key=auth_key)
    project_logger.info("添加公司:{} id:{} auth_key:{}".format(name, company_id,
                                                           auth_key))


def save_input(data_dict, company_id):
    """进件申请入库"""
    order_num = company_id + data_dict['order_num'][3:]
    obj = models.InputApply.objects(order_num=order_num,
                                    company_id=company_id).first()

    if obj and obj.confirm:
        return 2
    if obj is None:
        project_logger.info("进件insert {}".format(data_dict))
        obj = models.InputApply(order_num=order_num,
                                company_id=company_id,
                                production_id=data_dict['production_id'],
                                merchant_id=data_dict['merchant_id']).save()
    else:
        project_logger.info("进件update {}".format(data_dict))

    obj.merchant_id = int(data_dict['merchant_id'])
    obj.code = data_dict['code']
    obj.basic_info = models._Basic(**data_dict['basic_info'])
    if isinstance(data_dict['loan_info'], dict):
        obj.loan_info = models._Loan(**data_dict['loan_info'])
    # 工作信息
    if data_dict['work_info'] is not None:
        obj.work_info = models._Work(**data_dict['work_info'])
    # 学校信息
    if data_dict['school_info'] is not None:
        obj.school_info = models._School(**data_dict['school_info'])
    # 家庭信息
    if data_dict['family_info'] is not None:
        if not data_dict['family_info']['family_mem']:
            data_dict['family_info'].pop('family_mem')
            data_dict['family_info'].pop('mem_relation')
            data_dict['family_info'].pop('mem_telephone')
        if not data_dict['family_info']['marriage']:
            data_dict['family_info'].pop('mate_name')
            data_dict['family_info'].pop('mate_tel')

        obj.family_info = models._Family(**data_dict['family_info'])
    # 授权验证信息
    if data_dict['verify_info'] and type(data_dict['verify_info']) is list:
        obj.verify_info = []
        for i in data_dict['verify_info']:
            obj.verify_info.append(models._Verify(**i))
    elif data_dict['verify_info'] and type(data_dict['verify_info']) is dict:
        obj.verify_info = [models._Verify(**data_dict['verify_info']),]

    obj.save()
    return 1


def get_address(province, city, district):
    """
    获取地址
    :param province:
    :param city:
    :param district:
    :return:
    """
    p_name, c_name, d_name = "", "", ""
    p = models.ProvinceCode.objects(code=province).first()
    if p:
        p_name = p.name
    c = models.CityCode.objects(code=city).first()
    if c:
        c_name = c.name
    d = models.DistrictCode.objects(code=district).first()
    if d:
        d_name = d.name
    return "{} {} {} ".format(p_name, c_name, d_name)


def address_handler(info_dict):
    if isinstance(info_dict.get('work'), dict):
        p = info_dict['work'].get('province', '')
        c = info_dict['work'].get('city', '')
        d = info_dict['work'].get('district', '')
        if p or c or d:
            district = get_address(province=p, city=c, district=d)
            info_dict['work']['companyAdd'] = district + info_dict['work']['companyAdd']
    if isinstance(info_dict.get('family'), dict):
        p = info_dict['family'].get('province', '')
        c = info_dict['family'].get('city', '')
        d = info_dict['family'].get('district', '')
        if p or c or d:
            district = get_address(province=p, city=c, district=d)
            info_dict['family']['familyAdd'] = district + info_dict['family']['familyAdd']
        if info_dict['family']['community_num'] not in (",,", ""):
            l = info_dict['family']['community_num'].split(',')
            addr_num = ""
            if l[0] != "":
                addr_num += " " + l[0] + "栋"
            if l[1] != "":
                addr_num += l[1] + "单元"
            if l[2] != "":
                addr_num += l[2] + "号"
            info_dict['family']['community'] += addr_num
    if not info_dict['other'].get('city', ''):
        info_dict['other']['city'] = '成都'
    return info_dict


def make_response(data=None, status=const.SUCCESS, msg=None):
    if data is None:
        data = {}

    return {
        'data': data,
        'code': status,
        'msg': msg or const.MSG.get(status) or ''
    }