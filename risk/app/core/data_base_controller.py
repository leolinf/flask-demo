# -*- coding: utf-8 -*-
import datetime

from app.models.sqlas import User, ApplyTable, ApplyModule, ApplyPage, ApplyField
from sqlalchemy import and_

def set_obj_property(obj, kwargs):
    for key, value in kwargs.items():
        setattr(obj, key, value)
    return obj

class UserController(object):

    @classmethod
    def find_one_by_kwargs(cls, session, **kwargs):
        return session.query(User).filter_by(**kwargs).first()


class ApplyController(object):
    """ 申请表 """
    @classmethod
    def find_one_by_kwargs(cls, session, **kwargs):
        return session.query(ApplyTable).filter_by(**kwargs)

    @classmethod
    def find_or_create(cls, session, name, status, company_id,apply_id):
        """ 根据主键来找某个申请表， 存在则返回这个对象， 否则新建一个对象 """
        ret = session.query(ApplyTable).filter_by(id=apply_id).first()
        if ret:
            ret = set_obj_property(ret, dict(
                name=name, status=status
                ))
        if not ret:
            ret = ApplyTable(id=apply_id, name=name, status=status, company_id=company_id,
                             create_time=datetime.datetime.now())
        return ret

    @classmethod
    def find_by_company_and_type(cls, session, company_id, apply_type):
        return session.query(ApplyTable).filter(
            and_(ApplyTable.company_id == company_id, ApplyTable.apply_type==apply_type)).all()


class ApplyModelController(object):
    @classmethod
    def find_or_create(cls, session, name, index, apply_table_id, immutable):
        ret = session.query(ApplyModule).filter(
            and_(ApplyModule.apply_table_id == apply_table_id, ApplyModule.index==index)).first()
        if not ret:
            ret = ApplyModule(name=name, index=index, apply_table_id=apply_table_id,
                              immutable=immutable)
        else:
            ret.name = name
            ret.immutable = immutable
        return ret


class ApplyPageController(object):
    @classmethod
    def find_or_create(cls, session, index, apply_module_id):
        ret = session.query(ApplyPage).filter(
            and_(ApplyPage.index == index, ApplyPage.apply_module_id==apply_module_id)).first()
        if not ret:
            ret = ApplyPage(index=index, apply_module_id=apply_module_id)
        return ret


class ApplyFieldController(object):

    @classmethod
    def find_or_create(cls, session, key, name, is_ext, is_show, is_required, type_choice, changable,
                       apply_page_id, remark, field_index, submodule_name, submodule_key, submodule_index, submodule_is_ext):
        # 修改小模块名字会出现异常
        ret = session.query(ApplyField).filter(and_(
            ApplyField.apply_page_id==apply_page_id, ApplyField.submodule_key==submodule_key,
            ApplyField.key==key
        )).first()
        if ret:
            ret = set_obj_property(ret, dict(
                name=name,
                is_ext=is_ext,
                is_show=is_show,
                is_required=is_required,
                type_choice=type_choice,  # 输入框的类型, 后面会重构
                changable=changable,
                remark=remark,
                field_index=field_index,
                submodule_name=submodule_name,
                submodule_is_ext=submodule_is_ext,
                ))
        if not ret:
            ret = ApplyField(
                key=key,
                name=name,
                is_ext=is_ext,
                is_show=is_show,
                is_required=is_required,
                type_choice=type_choice,  # 输入框的类型, 后面会重构
                changable=changable,
                apply_page_id=apply_page_id,
                remark=remark,
                field_index=field_index,
                submodule_key=submodule_key,
                submodule_name=submodule_name,
                submodule_index=submodule_index,
                submodule_is_ext=submodule_is_ext,
            )
        return ret


def query_apply_table(session, apply_table_obj):
    """ 注意保证 module.index 和page.index的顺序 """
    query_filter = session.query(ApplyTable, ApplyModule, ApplyPage, ApplyField).filter(
        ApplyTable.id ==apply_table_obj.id, ApplyModule.apply_table_id==ApplyTable.id,
        ApplyPage.apply_module_id==ApplyModule.id, ApplyField.apply_page_id==ApplyPage.id
    ).filter(ApplyModule.index, ApplyPage.index)

    return query_filter


class MerchantController(object):
    @classmethod
    def get_merchant_by_kw(cls, session, apply_table_id, status):
        from app.models.sqlas import Merchant, Product
        return session.query(Product, Merchant).filter(
            Merchant.id == Product.merchant_id, Product.apply_table_id == apply_table_id,
            Merchant.status == 1)
