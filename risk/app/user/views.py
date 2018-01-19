# -*- coding: utf-8 -*-

import json

from flask import g
from flask_restful import Resource, marshal
from sqlalchemy.orm import scoped_session

from .parsers import user_login_parse, module_parser, pwd_parser
from app.core.data_base_controller import UserController
from app.models import User

from app.core.functions import make_response
from app.constants import Code
from .fields import company_info
from ..models import InputApply
from ..bases import BaseResource
from ..constants import CreditAuth
from ..databases import session_scope, Session
from .function import ImgController, login_required, current_user
from flask import current_app
from .function import current_user, login_required


class CompanyInfoView(Resource):
    @login_required
    def get(self):
        company_obj = current_user.company
        result = marshal(company_obj, company_info)
        return make_response(data=result)


class CompanyModuleList(BaseResource):

    @login_required
    def get(self, *args, **kwargs):
        """公司能查询的模块列表"""

        req = module_parser.parse_args(strict=True)
        search_id = req['id']
        session = scoped_session(Session)
        search = session.query(InputApply).filter_by(id=search_id).first()
        if not search:
            session.remove()
            return make_response(status=Code.DOES_NOT_EXIST)
        permissions = json.loads(search.permissions_snapshot)
        modules = [i['name'] for i in permissions]
        res = {}
        for i in CreditAuth.MODULE_DICT:

            if i in modules:
                res[i] = 1
            else:
                res[i] = 0
        # g.session.query(SingleSearch)
        # obj = SingleSearch.objects(apply_number=search_id).first()
        res.update({'contactInfoCheck': 1})
        res.update({"policeBadInfo": 1})
        session.remove()
        return make_response(data=res)


class SwitchList(Resource):

    @login_required
    def get(self):
        """公司所有开关的列表"""

        d = {}

        d.update({'contract': int(current_user.company.if_online_sign_contract) if current_user.company.if_online_sign_contract else 0})

        return make_response(d)


class ChangePwd(BaseResource):

    def put(self):
        """修改密码"""

        req = pwd_parser.parse_args()

        with session_scope() as session:
            user_obj = session.query(User).filter(User.username == req['userName']).first()

            if user_obj and user_obj.check_password(req['oldPwd']):
                user_obj.set_password(req['newPwd'], session)
                return make_response()
            else:
                return make_response(status=Code.MULTI_NOT_EXIST)


class CheckHealth(BaseResource):

    def get(self):

        return make_response()
