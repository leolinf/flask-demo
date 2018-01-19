# --*- coding: utf-8 -*-

import json
import qrcode
import hashlib
from PIL import Image
from io import BytesIO

from flask import request, g
from sqlalchemy import func, or_
from qiniu import Auth, put_data, PersistentFop, urlsafe_base64_encode
from urllib.parse import urlencode
from sqlalchemy import and_
from sqlalchemy.orm import scoped_session

from app.core.logger import project_logger
from app.models.sqlas import Merchant, Company, Product
from app.core.functions import datetime2timestamp
from app.constants import Code, ReceiveType

from app.config import Config
from app.models.sqlas import Merchant, Product
from app.databases import Session
import random
import string
import requests
from app.user.function import current_user


def get_merch_list(req):
    """获取商户列表"""

    count = req['count']
    page = req['page']
    signSort = req['signSort']
    merchantName = req['merchantName']
    start = count * (page - 1)

    match = (Merchant.company_id == current_user.company_id, )

    if merchantName:
        match += (
            or_(
                Merchant.name.ilike("%{}%".format(merchantName)),
                Merchant.merchant_phone.ilike("%{}%".format(merchantName))
            ),
        )

    if signSort == 1:
        sort = (Merchant.sign_time, )
    elif signSort == 2:
        sort = (Merchant.sign_time.desc(), )
    else:
        sort = (Merchant.sign_time, )
    session = scoped_session(Session)
    result = session.query(Merchant).filter(*match).order_by(*sort)
    total_count = result.count()
    result = result.offset(start).limit(count)
    res = []
    for i in result:
        res.append({
            "cooperationStatus": int(i.status),
            "level": i.level,
            "id": i.id,
            "name": i.name,
            "signTime": datetime2timestamp(i.sign_time),
            "contactName": i.linkman_name,
            "contactPhone": i.linkman_phone,
            "merchantType": i.product.recieve_type if i.product else -1,
        })
    session.remove()
    return {"merchantList": res, "total": total_count}


def down_qrcode_url_object(url, name):
    ret = {
        300: get_download_url(url, name, 300),
        600: get_download_url(url, name, 600),
        1000: get_download_url(url, name, 1000)
    }
    return ret


def get_merch_detail(merch_id):
    """获取商户信息接口"""

    session = scoped_session(Session)
    merchant = session.query(Merchant).filter(Merchant.id == merch_id).first()
    if not merchant:
        session.remove()
        return 'not exists'

    merchant_id = merchant.id

    company = merchant.company

    def qrcode_url(interest_id):
        nonlocal company, merchant_id
        into_url = company.into_url[0: -1] if company.into_url.endswith('/') else company.into_url
        into_url = '{}/search_into_pieces/{}/{}/{}?collaborateStatus={}'.format(
            into_url, company.id,
            merchant_id, interest_id, company.collaborate_status
        )
        return into_url

    products = [merchant.product] if merchant.product else []

    def _process(fields):
        return [{
            'Insurance': field['month_insurance_rate'],
            'administrationMount': field['month_manage_rate'],
            'monthlyInterestRate': field['month_rate'],
            'package': field['package_charge'],
            'serviceMount': field['month_serve'],
            'stage': field['name'],
        } for field in json.loads(fields)]

    if merchant.product.recieve_type in [ReceiveType.CLIENT, ReceiveType.BANDANYUAN]:
        apply_table = [{"applicationId": product.apply_table_id, "qrcodeUrl": {}, "applicationUrl": ""} for product in products]
    else:
        apply_table = [{"applicationId": product.apply_table_id, "qrcodeUrl": down_qrcode_url_object(merchant.qrcode_url, merchant.name), 'applicationUrl': qrcode_url(product.id)} for product in products]

    res = {
        'baseInfo': {
            'address': merchant.address,
            'contactPhone': merchant.linkman_phone,
            'contacts': merchant.linkman_name,
            'cooperationStatus': int(merchant.status),
            'level': merchant.level,
            'merchantPhone': merchant.merchant_phone,
            'name': merchant.name,
            'organizeNum': merchant.org_code,
            'propagandaChannel': merchant.publish_channel if merchant.publish_channel else '',
            'remarks': merchant.remarks if merchant.remarks else '',
            'signTime': datetime2timestamp(merchant.sign_time),
            'licenseName': merchant.license_name or "",
            'licenseUrl': get_download_url(merchant.license_url, merchant.license_name) if merchant.license_url else '',
            'contractName': merchant.contract_name or "",
            'contractUrl': get_download_url(merchant.contract_url, merchant.contract_name) if merchant.contract_url else '',
            "account": merchant.merchant_user.login_name if merchant.merchant_user else "",
            "bankAccount": merchant.banknum,
            "productName": merchant.product.name if merchant.product else "",
            "productId": merchant.product.id if merchant.product else "",
            "merchantType": merchant.product.recieve_type if merchant.product else -1,
        },
        "applyTable": apply_table
    }
    session.remove()
    return res


def process_rate(rate):
    if isinstance(rate, (int, float)):
        return str(rate / 100)

    elif isinstance(rate, (str, bytes)) :
        try:
            return str(float(rate) / 100)
        except:
            return ''
    else:
        return ''


def get_company_detail(company):

    cachet_url = get_download_url(company.cachet_url) if company.cachet_url else ''
    if company.contract_url and company.contract_url.startswith("http"):
        resp = requests.get(Config.FILE_SERVER_TOKEN, timeout=5).json()
        time = resp["data"]["time"]
        token = resp["data"]["token"]
        contract_url = "{0}?time={1}&token={2}".format(company.contract_url, time, token)
    else:
        contract_url = ""

    res = {
        'Id': company.linkman_idcard,
        'address': company.address,
        'commerceNumber': company.ic_code,
        'contactName': company.linkman_name,
        'contactPhone': company.linkman_phone,
        'detailAddress': '',
        'name': company.name,
        'organizeCode': company.org_code,
        'taxNumber': company.tax_code,
        'contract': company.contract_name,
        'contractUrl': contract_url,
        'officeSeal': cachet_url,
    }

    return res


def change_interest(trial):
    interest_list = []
    for i in trial:
        interest_list.append({
            "name": i['stage'],
            "month_rate": process_rate(i.get('monthlyInterestRate')),
            "month_serve": process_rate(i.get('serviceMount')),
            "month_manage_rate": process_rate(i.get('administrationMount')),
            "month_insurance_rate": process_rate(i.get('Insurance')),
            "package_charge": i.get('package'),
        })
    return interest_list

def merch_code(interest_id, merchant_id):
    """生成二维码图片并且上传到七牛"""

    session = scoped_session(Session)
    company = session.query(Company).get(current_user.company_id)
    if not company:
        session.remove()
        return None
    into_url = company.into_url[0: -1] if company.into_url.endswith('/') else company.into_url
    into_url = '{}/search_into_pieces/{}/{}/{}'.format(
        into_url, current_user.company_id,
           merchant_id, interest_id
    )
    qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=20, # 1000 像素
            border=4,
        )
    qr.add_data(into_url)
    qr.make(fit=True)

    img = qr.make_image()

    logo_url = company.logo_url
    if logo_url:
        q = Auth(Config.QINIU_ACCESS_KEY, Config.QINIU_SECRET_KEY)
        private_url = q.private_download_url(logo_url, expires=3600)
        logo = requests.get(private_url, timeout=10)
        img = img.convert("RGBA")
        img_w, img_h = img.size
        icon = Image.open(BytesIO(logo.content))
        factor = 5
        size_w = int(img_w / factor)
        size_h = int(img_h / factor)
        icon_w, icon_h = icon.size
        if icon_w > size_w:
            icon_w = size_w
        if icon_h > size_h:
            icon_h = size_h
        icon = icon.resize((icon_w, icon_h), Image.ANTIALIAS)
        w = int((img_w - icon_w) / 2)
        h = int((img_h - icon_h) / 2)
        icon = icon.convert("RGBA")
        img.paste(icon,(w,h),icon)

    output = BytesIO()
    img.save(output, format='png')
    output.seek(0)
    data = output.read()
    qr_name = hashlib.md5(data).hexdigest()
    filename = '{}.png'.format(qr_name)
    token = get_token(key=filename)
    ret, info = put_data(token, filename, data)
    session.remove()
    return 'http://%s/%s' % (Config.QINIU_BUCKET_DOMAIN, ret['key'])


def get_token(key=None):
    """获取上传token"""

    #构建鉴权对象
    q = Auth(Config.QINIU_ACCESS_KEY, Config.QINIU_SECRET_KEY)
    #要上传的空间
    bucket_name = Config.QINIU_BUCKET_NAME
    #生成上传 Token，可以指定过期时间等
    if key:
        return q.upload_token(bucket_name, key=key, expires=3600)
    return q.upload_token(bucket_name, key=None, expires=3600)


def get_download_url(base_url, img_name=None, size=None):
    """ 构造预览链接 """

    q = Auth(Config.QINIU_ACCESS_KEY, Config.QINIU_SECRET_KEY)
    if img_name and size:
        base_url = base_url + "?imageView2/1/w/{}/h/{}".format(size, size)
        # base_url = base_url + "?" + urlencode(dict(attname="{}.png".format(str(img_name) + str(size) + "px")))
    elif img_name:
        base_url = base_url + "?" + urlencode(dict(attname="{}".format(img_name)))
    return q.private_download_url(base_url, expires=3600)

def get_api_down_img(base_url, img_name, size):
    """ 构造下载的链接 """
    url = Auth(Config.QINIU_ACCESS_KEY, Config.QINIU_SECRET_KEY).private_download_url(base_url, expires=3600)
    ret = requests.get(url)
    bytes_obj = ret.content
    return bytes_obj


class __GenerateId(object):
    def __new__(cls):
        if hasattr(cls, '_inst'):
            return cls._inst
        cls._inst = super().__new__(cls)
        # cls._inst.__dict__['_merchant_dict'] = cls.get_current_merchant_d(session)
        # cls._inst.__dict__['_interest_dict'] = cls.get_current_interest_d(session)
        return cls._inst

    @classmethod
    def get_current_merchant_d(cls, session):
        ret = session.query(func.distinct(Merchant.id).label("id"))
        d = {}
        for i in ret:
            d.update({i.id: 1})
        return d

    @classmethod
    def get_current_interest_d(cls, session):
        ret = session.query(func.distinct(Product.id).label("id"))
        d = {}
        for i in ret:
            d.update({i.id: 1})
        return d

    @property
    def generate_merchant_id(self):
        session = Session()
        ret = session.query(func.distinct(Merchant.id).label("id"))
        d = {}
        for i in ret:
            d.update({i.id: 1})

        while True:
            ret = random.sample(string.ascii_letters, 5)
            ret = ''.join(ret)
            if ret not in d:
                session.close()
                return ret

    @property
    def generate_interest_id(self):
        session = Session()
        ret = session.query(func.distinct(Product.id).label("id"))
        d = {}
        for i in ret:
            d.update({i.id: 1})

        while True:
            ret = random.sample(string.ascii_letters, 5)
            ret = ''.join(ret)
            if ret not in d:
                session.close()
                return ret

_generate_id = __GenerateId()
from app.merch import utils
utils.generate_id = _generate_id
import sys
sys.modules['app.mercha.utils.generate_id'] = _generate_id
sys.modules['app.mercha.utils.generate_id'] = _generate_id
