# -*- coding: utf-8 -*-

import datetime
import json
import requests

from BestSignAPI import BestSignAPI, errorCode

from ..models import BestsignUser, BestsignContract, BestsignInfo, InputApply
from ..config import Config
from ..databases import session_scope
from ..constants import LoanStatus, InputApplyStatus, Status, ReceiveType
from app.user.function import current_user


class BestsignManager(object):
    def __init__(self, session, *args, **kwargs):

        self.session = session
        self.api = BestSignAPI(url=Config.SSQ_URL, mid=Config.SSQ_MID, private_key=Config.SSQ_PRIVATE_KEY)

    @staticmethod
    def call_api_ok(response):

        def response_to_json(response):
            if type(response) is bytes:
                response = response.decode()
            resp_json = json.loads(response)
            return resp_json

        resp_json = response_to_json(response)
        return_code = resp_json['response']['info']['code']
        if return_code != 100000:
            raise AssertionError(errorCode.ERROR_CODE.get(return_code))
        else:
            return resp_json

    def _register_user(self, phone, name, idcard):
        """去上上签注册用户，返回uid"""

        data = {
            'mobile': phone,
            'name': name,
            'usertype': '1',
            'identity': idcard,
        }

        resp = self.api.register_user(data)
        resp_json = self.call_api_ok(resp)

        return resp_json['response']['content']['uid']

    def _cert_user(self, phone, name, idcard):
        """认证用户"""

        data = {
            'userType': '1',
            'name': name,
            'password': phone,
            'identityType': '0',
            'duration': "24",
            'mobile': phone,
            'identity': idcard,
        }

        resp = self.api.apply_personal_certificate(data)
        self.call_api_ok(resp)

    def _create_user(self, phone, name, idcard):
        """创建上上签用户"""

        now = datetime.datetime.now()

        uid = self._register_user(phone, name, idcard)
        self._cert_user(phone, name, idcard)
        user = BestsignUser(
            phone=phone,
            name=name,
            idcard=idcard,
            uid=uid,
            cert_time=now,
        )
        return user

    def get_user(self, phone, name, idcard):
        """获取上上签用户"""

        user = self.session.query(BestsignUser).filter(BestsignUser.phone == phone).one_or_none()

        if not user:
            user = self._create_user(phone, name, idcard)

        return user

    def generate_contract(self, sponsor_dict, signatory_a, signatory_b, company_id):
        """生成合同"""

        bestsign_info = self.session.query(BestsignInfo).filter(BestsignInfo.company_id == company_id).one_or_none()
        contract_file = bestsign_info.path

        # 如果合同是个链接就下下来
        if contract_file.startswith("http"):
            resp = requests.get(Config.FILE_SERVER_TOKEN, timeout=5).json()
            time = resp["data"]["time"]
            token = resp["data"]["token"]
            filename = "contracts/{0}.pdf".format(company_id)
            f = open(filename, "wb")
            url = "{0}?time={1}&token={2}".format(contract_file, time, token)
            r = requests.get(url, timeout=5)
            f.write(r.content)
            f.close()
            contract_file = filename

        resp = self.api.send_document(contract_file, sponsor_dict, signatory_a, signatory_b)
        resp_json = self.call_api_ok(resp)

        sign_id = resp_json['response']['content']['contlist'][0]['continfo']['signid']
        doc_id = resp_json['response']['content']['contlist'][0]['continfo']['docid']
        return sign_id, doc_id

    def auto_sign(self, signid, email, position):
        """自动签署"""

        resp = self.api.auto_sign(signid, email, position)
        self.call_api_ok(resp)

    def preview_contract(self, sign_id):
        """预览合同"""

        contract = self.session.query(BestsignContract).filter(BestsignContract.signid == sign_id).one_or_none()

        if not contract:
            return 'not exists'

        return self.api.view_document(sign_id, contract.docid)

    def sign_contract(self, input_apply_id):
        """签署合同"""

        credit = self.session.query(InputApply).filter(InputApply.id == input_apply_id).one_or_none()
        contract = self.session.query(BestsignContract).filter(BestsignContract.id == input_apply_id).one_or_none()
        input_apply = credit

        if not credit:
            return 'not exists'

        bestsign_info = self.session.query(BestsignInfo).filter(
            BestsignInfo.company_id == credit.company_id).one_or_none()
        if not bestsign_info:
            return "no sign"

        # 没有CA认证过的用户就认证并存库
        user = self.get_user(credit.phone, credit.name, credit.idcard)
        self.session.add(user)

        if not contract:
            sponsor_dict = {
                'emailtitle': bestsign_info.email_title,
                'emailcontent': bestsign_info.email_content,
                'sxdays': bestsign_info.sxdays,
                'selfsign': '0',
                'name': Config.SSQ_NAME,
                'mobile': Config.SSQ_MOBILE,
                'usertype': Config.SSQ_USERTYPE,
                'Signimagetype': Config.SSQ_SIGNIMAGETYPE,
                'UserfileType': Config.SSQ_USERFILETYPE,
                'email': Config.SSQ_EMAIL,
            }

            # 债务人
            signatory_a = {
                'name': credit.name,
                'isvideo': bestsign_info.isvideo,
                'mobile': credit.phone,
                'usertype': '1',
                'Signimagetype': '1',
            }

            # 债权人
            signatory_b = {
                'email': bestsign_info.email,
                'name': bestsign_info.name,
                'isvideo': bestsign_info.isvideo,
                'mobile': bestsign_info.phone,
                'usertype': bestsign_info.usertype,
                'Signimagetype': bestsign_info.signimagetype,
            }

            # 发送合同
            signid, docid = self.generate_contract(sponsor_dict, signatory_a, signatory_b, credit.company_id)
            contract = BestsignContract(
                id=credit.id,
                signid=signid,
                docid=docid,
                status='3',
                company_id=credit.company_id,
                input_apply_id=credit.id,
            )
            self.session.add(contract)

            # 债权人自动签署
            auto_sign = json.loads(bestsign_info.auto_sign)
            self.auto_sign(signid, bestsign_info.email, auto_sign)

        callback = '{0}/msg_success/{1}/{2}/{3}?phone={4}'.format(
            credit.company.into_url.rstrip('/'),
            credit.company.id,
            input_apply.merchant_id,
            input_apply.interest_id,
            input_apply.phone,
        )

        if contract.status == '5':
            return callback

        manual_sign = credit.company.bestsign_info.manual_sign

        return self.api.get_sign_page_link(contract.signid, credit.phone, manual_sign, callback, '2')

    def downloan_contract(self, sign_id):
        """下载合同"""

        contract = self.session.query(BestsignContract).filter(BestsignContract.signid == sign_id).one_or_none()
        if not contract:
            return 'not exists'

        return self.api.get_download_document_url(sign_id, Config.SSQ_FILETYPE)

    def close_contract(self, signid, code):
        """结束合同"""

        if code != '100000':
            return

        contract = self.session.query(BestsignContract).filter(BestsignContract.signid == signid).one_or_none()
        if not contract:
            return 'not exists'

        input_apply = self.session.query(InputApply).get(contract.id)
        if not input_apply:
            return 'not exists'

        resp = self.api.end_document(signid)
        self.call_api_ok(resp)

        contract.status = '5'
        if input_apply.merchant.product.recieve_type in [ReceiveType.CLIENT, ReceiveType.BANDANYUAN]:
            input_apply.status = Status.WAITMERCH
        else:
            input_apply.status = Status.WAITLOAN
        self.session.add(contract)
        self.session.add(input_apply)

    def for_java_to_sign_contract(self, input_apply_id, callback):
        """给java调的生成合同链接"""

        credit = self.session.query(InputApply).filter(InputApply.id == input_apply_id).one_or_none()

        if not credit:
            return 'not exists'

        # 没有CA认证过的用户就认证并存库
        user = self.get_user(credit.phone, credit.name, credit.idcard)
        self.session.add(user)

        company = credit.company
        bestsign_info = company.bestsign_info
        if not bestsign_info:
            return "no sign"

        sponsor_dict = {
            'emailtitle': bestsign_info.email_title,
            'emailcontent': bestsign_info.email_content,
            'sxdays': bestsign_info.sxdays,
            'selfsign': '0',
            'name': Config.SSQ_NAME,
            'mobile': Config.SSQ_MOBILE,
            'usertype': Config.SSQ_USERTYPE,
            'Signimagetype': Config.SSQ_SIGNIMAGETYPE,
            'UserfileType': Config.SSQ_USERFILETYPE,
            'email': Config.SSQ_EMAIL,
        }

        # 债务人
        signatory_a = {
            'name': credit.name,
            'isvideo': bestsign_info.isvideo,
            'mobile': credit.phone,
            'usertype': '1',
            'Signimagetype': '1',
        }

        # 债权人
        signatory_b = {
            'email': bestsign_info.email,
            'name': bestsign_info.name,
            'isvideo': bestsign_info.isvideo,
            'mobile': bestsign_info.phone,
            'usertype': bestsign_info.usertype,
            'Signimagetype': bestsign_info.signimagetype,
        }

        contract = self.session.query(BestsignContract).filter(BestsignContract.id == credit.id).one_or_none()

        has_contract = False
        if not contract:
            # 发送合同
            signid, docid = self.generate_contract(sponsor_dict, signatory_a, signatory_b, company.id)
            contract = BestsignContract(
                id=credit.id,
                signid=signid,
                docid=docid,
                status='3',
                company_id=credit.company_id,
                input_apply_id=credit.id,
            )
            self.session.add(contract)
        else:
            has_contract = True
            signid = contract.signid

        # 债权人自动签署
        auto_sign = json.loads(bestsign_info.auto_sign)
        if not has_contract:
            self.auto_sign(signid, bestsign_info.email, auto_sign)

        if contract.status == '5':
            return callback

        manual_sign = company.bestsign_info.manual_sign

        return self.api.get_sign_page_link(signid, credit.phone, manual_sign, callback, '2')
