# -*- coding: utf-8 -*-
from app.models.sqlas import  ApplyTable, Company
from sqlalchemy import func
from app.databases import Session

def __generate_version(dest):

    dest = dest.replace('.', '')
    dest = '.'.join(str(int(dest)  +1))
    return dest

def generate_version(dest):
    if not dest:
        return 'V1.0.0'
    dest = __generate_version(dest[1:])
    return 'V' + str(dest)


def sum_total(json_obj):
    """ 对json对象进行计算，输出totalShow 和totalMustWrite字段 """
    all_b_modules = json_obj['modules']
    for b_index, each_b_mod in enumerate(all_b_modules):
        total_must_write = total_show = 0
        all_pages = each_b_mod["pages"]
        for each_page in all_pages:
            modulars = each_page['modulars']
            for sm_index, sm_mod in enumerate(modulars):
                total_field = 0
                for each_field in sm_mod['labels']:
                    total_field += 1 if each_field['isShow'] == 1 else 0
                    total_must_write += 1 if each_field['mustWrite'] else 0
                    total_show += 1 if each_field['isShow'] == 1 else 0

                modulars[sm_index]['totalShow'] = total_field

        all_b_modules[b_index]['totalMustWrite'] = total_must_write
        all_b_modules[b_index]['totalShow'] = total_show


from sqlalchemy import and_


class RelationShipApplyTable(object):
    """ 申请表的特殊处理情况 """
    @classmethod
    def contract_status(cls, session, company_id):
        """ 获取合同状态 """
        return session.query(Company).filter(Company.id == company_id).first().if_online_sign_contract

    @classmethod
    def home_adddress_contract(cls, session, field_obj, company_id, contract_status=None):
        """ 合同状态 影响居住地址 """
        if contract_status is None:
            obj_status = cls.contract_status(session, company_id)
            if not obj_status or obj_status.is_on is False:
                return True
        elif contract_status == 0 or contract_status is False:
            return True

        if field_obj['key'] == 'home_live_address' or field_obj['key'] == 'home_detail_address':
            if field_obj['isShow'] == 0 or field_obj['mustWrite'] == 0:
                return False

        return True


class __GenerateApplyTableId(object):
    def __new__(cls):
        if hasattr(cls,'_inst'):
            return cls._inst

        cls._inst=super().__new__(cls)
        # cls._inst.__dict__['cached_session'] = cls.get_current_apply_id(session)
        # cls._inst.__dict__['test_func'] = cls.yield_func(cls._inst)
        # cls._inst.__dict__['session'] = session
        return cls._inst

    @classmethod
    def yield_func(cls, instance):
        initizer = instance.cached_session
        while True:
            initizer = str(int(initizer) + 1)
            yield initizer

    @classmethod
    def get_current_apply_id(cls, session):
        """func.max 在对字符串操作时会出现问题 """
        ret = session.query(func.distinct(ApplyTable.id).label("id"))
        list_id = [int(i.id) for i in ret]
        if not list_id:
            return "1"
        else:
            return max(list_id)

    @property
    def next_id(self):
        session = Session()
        ret = session.query(func.distinct(ApplyTable.id).label("id"))
        list_id = [int(i.id) for i in ret]
        if not list_id:
            return "1"
        else:
            session.close()
            return str(max(list_id) + 1)


from app.models.sqlas import ApplyModule, ApplyPage, ApplyField


def delete_apply_module(session, module_index, apply_table_id):
    all_modules = session.query(ApplyModule).filter(and_(
        ApplyModule.index == module_index, ApplyModule.apply_table_id==apply_table_id)).all()
    for each_b_mod in all_modules:
        all_pages = session.query(ApplyPage).filter(ApplyPage.apply_module_id==each_b_mod.id).all()
        for page in all_pages:
            fields = session.query(ApplyField).filter(ApplyField.apply_page_id==page.id).all()
            for i in fields:
                session.delete(i)
            session.flush()
            session.delete(page)
        session.flush()
        session.delete(each_b_mod)
    session.flush()

GenerateApplyTableId_ = __GenerateApplyTableId()
from  app.apply_table import function
function.GenerateApplyTableId = GenerateApplyTableId_

import sys
sys.modules["app.apply_table.function.GenerateApplyTableId"] = GenerateApplyTableId_

