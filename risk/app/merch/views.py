# -*- encoding: utf-8 -*-
import datetime
import json

from flask import g
from flask import request
from sqlalchemy.orm import scoped_session

from app import Session
from app.merch.utils import get_api_down_img, get_download_url
from PIL import Image
from flask import send_file
from io import BytesIO
from app.core.functions import make_response, timestamp2datetime
from app.core.logger import project_logger
from app.constants import Code
from app.models.sqlas import (
    Merchant, ApplyTable, Product, Company,
    MerchantUser)
from .parsers import (
    merch_add, merchant_list_parser,
    merchant_detail_parser, merchant_status_parser,
)
from .utils import (
    get_company_detail, get_merch_list, get_merch_detail,
    change_interest, get_token, merch_code,
    generate_id
)
from app.bases import BaseResource
from app.apply_table.function import generate_version
from app.user.function import login_required, current_user


class MerchAddEditView(BaseResource):
    @login_required
    def post(self):
        """商户添加和编辑"""
        req = merch_add.parse_args(strict=True)
        merchant_id = req["id"]
        base_info = req['baseInfo']
        session = scoped_session(Session)

        try:
            if merchant_id:
                merchant_obj = session.query(Merchant).get(merchant_id)
                merchant_user = session.query(MerchantUser).filter(MerchantUser.merchant_id == merchant_id).first()
                if not merchant_obj:
                    return make_response(status=Code.MERCH_NOT_EXIST)
                merchant_obj.name = base_info["name"]
                merchant_obj.org_code = base_info['organizeNum']
                merchant_obj.level = base_info['level']
                merchant_obj.merchant_phone = base_info['merchantPhone']
                merchant_obj.address = base_info['address']
                merchant_obj.linkman_name = base_info['contacts']
                merchant_obj.linkman_phone = base_info['contactPhone']
                merchant_obj.sign_time = timestamp2datetime(base_info['signTime'])
                merchant_obj.publish_channel = base_info.get('propagandaChannel')
                merchant_obj.remarks = base_info.get('remarks')
                merchant_obj.status = base_info['cooperationStatus']
                merchant_obj.banknum = base_info['bankAccount']
                merchant_obj.product_id = base_info['productId']
                merchant_user.mobile = base_info['merchantPhone']
                if base_info.get("contractStatus") in [1, "1"]:
                    merchant_obj.contract_name = base_info.get('contractName')
                    merchant_obj.contract_url = base_info.get('contractUrl')
                if base_info.get("licenseStatus") in [1, "1"]:
                    merchant_obj.license_name = base_info.get('licenseName')
                    merchant_obj.license_url = base_info.get('licenseUrl')
                merchant_obj.company_id = current_user.company_id
                session.add(merchant_obj)

            else:
                now = datetime.datetime.now()
                merchant_obj = Merchant(
                    name=base_info["name"],
                    org_code=base_info['organizeNum'],
                    level=base_info['level'],
                    merchant_phone=base_info['merchantPhone'],
                    address=base_info['address'],
                    linkman_name=base_info['contacts'],
                    linkman_phone=base_info['contactPhone'],
                    sign_time=timestamp2datetime(base_info['signTime']),
                    publish_channel=base_info.get('propagandaChannel'),
                    remarks=base_info.get('remarks'),
                    status=base_info.get('cooperationStatus'),
                    contract_name=base_info.get('contractName'),
                    contract_url=base_info.get('contractUrl'),
                    license_name=base_info.get('licenseName'),
                    license_url=base_info.get('licenseUrl'),
                    company_id=current_user.company_id,
                    banknum=base_info.get("bankAccount"),
                    product_id=base_info.get("productId"),
                    create_time=now,
                )
                session.add(merchant_obj)

                u = session.query(MerchantUser).filter(MerchantUser.login_name == base_info.get("account")).all()
                if u:
                    session.rollback()
                    session.remove()
                    return make_response(status=Code.MERCH_USER_EXISTS)

                merchant_user = MerchantUser(
                    merchant=merchant_obj,
                    mobile=base_info.get("merchantPhone"),
                    login_name=base_info.get("account"),
                    login_pwd="53fe3cd1dce3e1ce5062cb23916b1a16",
                    create_time=now,
                )
                session.add(merchant_user)
                session.flush()
                merchant_id = merchant_obj.id

            merchant_obj.qrcode_url = merch_code(base_info.get("productId"), merchant_id)
            session.add(merchant_obj)
            session.commit()
            m = session.query(Merchant).get(merchant_id)
            merchant_type = m.product.recieve_type if m.product else -1
            session.remove()
        except Exception as e:
            import traceback
            traceback.print_exc()
            project_logger.error("%s", str(e))
            session.rollback()
            session.remove()
            return make_response(status=Code.APPLY_TABLE_SAVE_ERROR)
        return make_response(data={
            "password": "a12345",
            "id": merchant_id,
            "merchantType": merchant_type,
        })


class MerchDetail(BaseResource):
    @login_required
    def get(self):
        """获取商户信息接口"""

        req = merchant_detail_parser.parse_args(strict=True)

        merch_id = req['id']

        result = get_merch_detail(merch_id)

        if result == 'not exists':
            return make_response(status=Code.MERCH_NOT_EXIST)

        return make_response(data=result)


class ApplySearchView(BaseResource):
    @login_required
    def get(self):
        """查询一个公司下有多少个表单"""

        session = scoped_session(Session)
        result = session.query(ApplyTable).filter(
            ApplyTable.company_id == current_user.company_id, ApplyTable.status == 1)
        result = result.order_by(ApplyTable.create_time.desc()).all()
        session.remove()
        if not result:
            return make_response(status=Code.SUCCESS, data={"application": []})
        return make_response(data={"application": [{"value": i.id, "name": i.name} for i in result]})


class GetMerchType(BaseResource):
    @login_required
    def get(self):
        """获取商户类型"""

        return make_response()


class MerchList(BaseResource):
    @login_required
    def get(self):
        """获取商户列表信息"""

        req = merchant_list_parser.parse_args(strict=True)

        merchants = get_merch_list(req)

        return make_response(
            data=merchants
        )


class MerchCoStatus(BaseResource):
    @login_required
    def post(self):
        """修改合作状态"""

        req = merchant_status_parser.parse_args(strict=True)

        merch_id = req['id']
        status = req['status']

        session = scoped_session(Session)
        merchant = session.query(Merchant).filter(Merchant.id == merch_id,
                                                    Merchant.company_id == current_user.company_id).first()
        if not merchant:
            session.remove()
            return make_response(status=Code.MERCH_NOT_EXIST)

        merchant.status = status
        session.add(merchant)
        session.commit()
        session.remove()
        return make_response(status=Code.SUCCESS)


class CompanyUploadToken(BaseResource):
    @login_required
    def get(self):
        from flask import jsonify
        """获取七牛的token"""
        token = get_token()
        return jsonify({'code': 10000, 'msg': 'success', 'uptoken': token})


class CompanyInfoView(BaseResource):
    @login_required
    def get(self):
        """公司信息"""

        session = scoped_session(Session)
        company = session.query(Company).get(current_user.company_id)
        if not company:
            session.remove()
            return make_response(status=Code.COMPANY_NOT_EXIST)

        result = get_company_detail(company)
        session.remove()

        return make_response(data=result)


class MerchUpload(BaseResource):
    @login_required
    def post(self):
        """上传合同附件或营业执照"""
        """
        req = upload_parser.parse_args(strict=True)

        attachment = req['attachment']
        type_= req['type']
        if type_ == 1 and attachment.cokntent_type not in Code.IMAGE_CONTENT_TYPE:
            return make_response(status=Code.NOT_IMAGE)

        attach = Attachment()
        attach.content.put(attachment.stream.read(), content_type=attachment.content_type)
        attach.name = attachment.filename
        attach.company_id = current_user.company_id
        attach.save()
        """
        return make_response()


class MerchAttachment(BaseResource):
    @login_required
    def get(self):
        """下载附件"""

        """
        req = merchant_file_parser.parse_args(strict=True)

        attachment_id = req['id']
        attachment = Attachment.objects(id=attachment_id, company_id=current_user.company_id).first()

        if not attachment:
            return make_response(status=Code.ATTACHMENT_NOT_EXIST)

        output = BytesIO(attachment.content.read())
        filename = attachment.name.encode().decode('unicode_escape')
        return send_file(output, attachment_filename=filename, as_attachment=True)
        """
        return make_response()


class MerchCode(BaseResource):
    @login_required
    def get(self):
        """二维码下载"""
        return make_response()


class DownQrCodeView(BaseResource):
    """
    url: /api/download_code/
    下载接口
    """
    def get(self):
        merch_id = request.args.get('id')
        size = int(request.args.get('size'))
        session = scoped_session(Session)
        merchant = session.query(Merchant).filter(Merchant.id == merch_id).first()
        io_obj = get_api_down_img(merchant.qrcode_url, merchant.name, size)
        ret = BytesIO(io_obj)

        img_obj = Image.open(ret)
        out = img_obj.resize((size, size), Image.ANTIALIAS)  # resize image with high-quality
        ret.seek(0)
        out.save(ret, format="PNG")
        ret.seek(0)
        file_name = merchant.name + "-" + str(size) + 'px.png'
        session.remove()
        return send_file(ret, mimetype='image/png', attachment_filename=file_name.encode("utf-8").decode("latin-1"),
                         as_attachment=True)
