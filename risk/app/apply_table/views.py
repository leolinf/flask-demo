# -*- coding: utf-8 -*-
import json

from flask_restful import Resource, marshal, request
from flask import Response, make_response, Flask
from flask_login import login_user
import datetime
from flask import g
from sqlalchemy import or_
from sqlalchemy.orm import scoped_session

from app.core.data_base_controller import UserController, ApplyController,\
    ApplyModelController, ApplyPageController, ApplyFieldController
from app.core.functions import make_response
from app.constants import Code

from app.core.functions import generate_field_key
from app.apply_table.function import sum_total
from app.apply_config import default, recommend
from collections import OrderedDict

from app.databases import session_scope, Session
from .function import generate_version, delete_apply_module

from flask import Response

from app.apply_table.function import GenerateApplyTableId
from app.core.logger import project_logger, trace_view,class_logger
from app.models.sqlas import ApplyTable, ApplyModule, ApplyField, ApplyPage
from app.bases import BaseResource
from app.user.function import current_user, login_required


@trace_view
@class_logger
class AddApplyTable(BaseResource):
    """
    新增一个申请表, 或者修改一个申请表的信息
    url:/api/post_application/
    """
    def bool_handle(self, value):
        if value == 0:
            return False
        return True

    @login_required
    def post(self):
        from app.apply_table.parases import CustomParse
        from app.core.data_base_controller import MerchantController
        from app.apply_table.function import RelationShipApplyTable

        session = scoped_session(Session)

        try:
            req = CustomParse()(request.json)
        except Exception as e:
            return make_response("request args is error", 400)
        is_changed = None
        really_apply_id = req['id'] or GenerateApplyTableId.next_id
        #generate_apply_id(current_user.company.id)
        # if merchant has used the apply table, can not changed

        if req['id'] and req['status'] == 0:
            merchants = MerchantController.get_merchant_by_kw(session, really_apply_id, 1).all()
            if merchants:
                return make_response(status=Code.NOT_DISABLE_APPLY)
        # # 合同
        # contract_status = RelationShipApplyTable.contract_status(g.session, current_user.company.id)
        # if contract_status:
        #     contract_status = contract_status.is_on
        # else:
        #     contract_status = False
        #
        # project_logger.info("company|{} 合同状态|{}".format(
        #     current_user.company.id, contract_status))

        # 申请表版本号控制
        if not req['id']:
            is_changed = 1 # create apply_table , is always True
        else:
            is_changed = req['isChanged']
        length_module = 0

        try:
            apply_table_obj = ApplyController.find_or_create(
                session, name=req['name'], status=req['status'], apply_id=really_apply_id,
                company_id=current_user.company.id
            )
            # merge, if the primary key is existed, update the record otherwise insert the record
            if is_changed: # need to update version
                version = generate_version(apply_table_obj.version)
                apply_table_obj.version = version

            if not req['id']:
                version = generate_version(None)
                apply_table_obj.version = version

            apply_table_obj = session.merge(apply_table_obj)
            session.flush()

            # length_module = len(req['modules'])
            #list_mods_leng = len(g.session.query(ApplyModule).filter(ApplyModule.apply_table_id==apply_table_obj.id).all())
            # list_mods_leng = 0
            delete_list = set()

            new_page_ids = []
            new_field_ids = []
            for each_mod in req['modules']:
                # if list_mods_leng <= int(each_mod['index']):
                delete_list.add(each_mod['index'])
                # print("&&&&", list_mods_leng, each_mod['index'])
                # list_mods_leng = each_mod['index']
                b_mods_obj = ApplyModelController.find_or_create(
                    session, name=each_mod['name'], index=each_mod['index'],
                    apply_table_id=apply_table_obj.id, immutable=self.bool_handle(each_mod['immutable']))
                b_mods_obj = session.merge(b_mods_obj)
                session.flush()
                for page_index, each_page in enumerate(each_mod['pages']):
                    page_obj = ApplyPageController.find_or_create(
                        session, index=page_index, apply_module_id=b_mods_obj.id
                    )
                    page_obj = session.merge(page_obj)
                    new_page_ids.append(page_obj.id)
                    session.flush()
                    for s_index, each_s_mod in enumerate(each_page['modulars']):
                        submodule_key = each_s_mod.get('key', None) or generate_field_key(each_s_mod['name'])
                        for each_field in each_s_mod['labels']:
                            # 合同状态开关影响 家庭地址信息的判断不要了
                            # if RelationShipApplyTable.home_adddress_contract(
                            #     g.session, each_field, current_user.company.id, contract_status) is False:
                            #
                            #     project_logger.info("each_field home_address: key|%s, isShow|%s, mustWrite|%s " % (
                            #         each_field['key'], each_field['isShow'], each_field['mustWrite']))
                            #
                            #     g.session.rollback()
                            #     return make_response(status=Code.HOME_ADDRESS_CONTRACT_ERR)

                            field_obj = ApplyFieldController.find_or_create(session,
                                key=each_field['key'] or generate_field_key(each_field['name']),
                                name=each_field['name'],
                                is_ext=each_field.get('isExt', 0) or 0,
                                is_show=self.bool_handle(each_field['isShow']),
                                is_required=self.bool_handle(each_field['mustWrite']),
                                type_choice=each_field['type'],  # 输入框的类型, 后面会重构
                                changable=self.bool_handle(each_field['unchanged']),
                                apply_page_id=page_obj.id,
                                remark=each_field['remarks'],
                                field_index=each_field['field_index'],
                                submodule_name=each_s_mod['name'],
                                submodule_key=submodule_key,
                                submodule_index=s_index,
                                submodule_is_ext=each_s_mod.get('isExt', 0) or 0,
                            )
                            session.add(field_obj)
                            session.flush()
                            new_field_ids.append(field_obj.id)
            # 自定义的字段可以删
            to_delete = session.query(ApplyField).join(ApplyPage, ApplyPage.id == ApplyField.apply_page_id).join(ApplyModule, ApplyModule.id == ApplyPage.apply_module_id).join(ApplyTable, ApplyTable.id == ApplyModule.apply_table_id).filter(ApplyTable.id == apply_table_obj.id, ApplyField.id.notin_(new_field_ids)).all()
            for i in to_delete:
                session.delete(i)
            session.flush()

            to_delete_pages = session.query(ApplyPage).join(ApplyModule, ApplyModule.id == ApplyPage.apply_module_id).join(ApplyTable, ApplyTable.id == ApplyModule.apply_table_id).filter(ApplyTable.id == apply_table_obj.id, ApplyPage.id.notin_(new_page_ids)).all()
            for i in to_delete_pages:
                session.delete(i)

            session.flush()

            # print("\n1gfg***", length_module, list_mods_leng, '\n\n')
            delete_list = set([1, 2, 3, 4, 5]) - delete_list
            for i in delete_list:
                # g.session.query(Apply)
                delete_apply_module(session, i, apply_table_obj.id)
            session.commit()
            apply_table_id = apply_table_obj.id
        except Exception as e:
            import traceback
            traceback.print_exc()
            session.rollback()
            return make_response(status=Code.APPLY_TABLE_SAVE_ERROR)
        finally:
            session.remove()
        return make_response(status=Code.SUCCESS, data={'id': apply_table_id})


class GetApplyListView(BaseResource):
    """
    url:  /api/application_list/
    获取申请表列表接口
    """
    def bool_handle(self, value):
        if value is True:
            return 1
        return 0

    @login_required
    def get(self):
        session = scoped_session(Session)
        count = int(request.args.get('count', 1))
        page = int(request.args.get('page', 1))
        all_apply = ApplyController.find_one_by_kwargs(session, company_id=current_user.company.id)
        all_apply = all_apply.order_by(ApplyTable.create_time.desc()).all()
        data = []
        for obj in all_apply[(page - 1) * count: count * page]:
            data.append({
                'createTime': obj.create_time,
                'edition': obj.version,
                'id': obj.id,
                'name': obj.name,
                'status': self.bool_handle(obj.status)
            })
        session.remove()
        return make_response(data={'applicationList': data, 'total': len(all_apply)})


class GetApplyTableDetailView(BaseResource):
    """
    获取已经有的配置
    URL: /api/application/
    """

    def bool_change(self, value):
        if isinstance(value, bool):
            if value is True:
                return 1
            else:
                return 0
        return value

    def sub_mod_field(self, sub_mod_obj, data):
        sub_key = data.submodule_key
        if sub_key not in sub_mod_obj:
            sub_mod_obj[data.submodule_key] = {}
            sub_mod_obj[data.submodule_key]['labels'] = []

        sub_mod_obj[data.submodule_key]['name'] = data.submodule_name
        if data.submodule_is_ext:
            sub_mod_obj[data.submodule_key]['isExt'] = data.submodule_is_ext

        middle = {
                "name": data.name,
                "key": data.key,
                "isShow": self.bool_change(data.is_show),
                "mustWrite": self.bool_change(data.is_required),
                "type": data.type_choice,
                "unchanged": self.bool_change(data.changable),
                "remarks": data.remark,
                "index": data.submodule_index,
                'field_index': data.field_index,
            }
        if self.bool_change(data.is_ext):
            middle['isExt'] = self.bool_change(data.is_ext)

        sub_mod_obj[data.submodule_key]['labels'].append(middle)

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
        req = request.args
        from collections import OrderedDict
        config_type = 3

        session = scoped_session(Session)

        app_table_obj = ApplyController.find_one_by_kwargs(session, id=req['id'])

        app_table_obj = app_table_obj[0]
        modules_list = []

        for each_module in sorted(app_table_obj.modules, key=lambda x: x.index):
            sub_mod_field = OrderedDict()
            pages = []
            for each_page in sorted(each_module.pages, key=lambda x: x.index):
                for each_field in sorted(each_page.fields, key=lambda x: x.submodule_index):
                    self.sub_mod_field(sub_mod_field, each_field)
                pages.append({'modulars': self.trans_dict_to_list_by_key(sub_mod_field)})
            modules_list.append({
                "name": each_module.name,
                "immutable": self.bool_change(each_module.immutable or 1),
                "index": each_module.index,
                'pages': pages.copy()
            })
        data = {
            "modules": modules_list,
            'id': app_table_obj.id,
            "name": app_table_obj.name,
            "status": self.bool_change(app_table_obj.status)
        }
        sum_total(data)
        return make_response(data)


class GetDefaultConfig(BaseResource):
    """
    url:  /api/application_config/
    获取默认配置
    """
    def get(self):
        from app.apply_config import default
        data = default._config.copy()

        sum_total(data)
        return make_response(data=data)


class GetRecomdmendView(BaseResource):
    """
        url: /api/recommend_application/
        获取推荐配置
    """
    def get(self):
        from app.apply_config import recommend
        data = recommend._config.copy()

        sum_total(data)
        return make_response(data=data)


class CustomConfigView(BaseResource):
    """
    url: /api/custom_config/
    保存或者获取个性配置
    """

    @login_required
    def post(self):

        table_id = request.json.get('id')
        data = request.json.get('data')

        session = scoped_session(Session)

        try:
            table = session.query(ApplyTable).filter(ApplyTable.id == table_id).one_or_none()
        except:
            return make_response(status=Code.UNVALID_APPLY_TABLE_ID)

        if not table:
            return make_response(status=Code.UNVALID_APPLY_TABLE_ID)

        try:
            data = json.dumps(data)
        except:
            data = json.dumps({})

        with session_scope(session) as session:
            table.custom_config = data
            session.add(table)

        return make_response()

    @login_required
    def get(self):

        table_id = request.args.get('id')

        session = scoped_session(Session)

        try:
            table = session.query(ApplyTable).filter(ApplyTable.id == table_id).one_or_none()
        except:
            return make_response(status=Code.UNVALID_APPLY_TABLE_ID)

        if not table:
            return make_response(status=Code.UNVALID_APPLY_TABLE_ID)

        try:
            data = json.loads(table.custom_config)
            data = {"modules": data}
        except:
            data = {}

        session.remove()
        return make_response(data=data)
