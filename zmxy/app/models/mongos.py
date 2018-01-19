# -*- coding: utf-8 -*-

import bcrypt
import datetime

from mongoengine import (
    DynamicDocument, StringField, ListField, DateTimeField,
    DictField, DynamicField, IntField, ReferenceField,
    BooleanField, ObjectIdField
)


class RequestRecord(DynamicDocument):

    app_key = StringField()

    create_time = DateTimeField()
    # api 大的分类
    # 接口大类
    interface = StringField()

    params = DictField()

    result = DynamicField()
    # 1 是成功
    success = IntField()
    # 匹配
    match = IntField()
    # 接口小的分类
    # 接口小分类, 统一以下划线来分开
    api_type = StringField()
    repeat = IntField()

    meta = {
        'collection': 'request_record'
    }


class OperatorRecord(DynamicDocument):

    # 创建时间
    create_time = IntField()
    # 手机号
    phone = StringField()
    # token
    uuid = StringField()
    # operator data
    operator_data = DynamicField()
    # operator_detail_data
    operator_detail = DynamicField()
    # 运营商
    operator = StringField()
    # name
    name = StringField()
    #idcard
    idcard = StringField()
    # callback
    callback = StringField()
    # 授权状态
    auth_status = IntField()
    # 队列返回的数据
    one_setp = StringField()
    two_setp = StringField()

    meta = {
        "collections": 'operator_record'
    }

class Account(DynamicDocument):
    """
    新需求将账号和公司区分开
    """
    account = StringField(unique=True)
    # 这个密码是明文存储,用来
    password = StringField()

    # 加密之后的存储, 用户登录和修改密码使用这个字段
    hash_password = StringField()
    # 用户类型 0/1/2/3 公司用户/管理员/普通管理员/超级管理员
    user_type = IntField(default=0)
    # 用来将账号和公司进行关联
    app_key = StringField()

    # 创建用户的account
    creator = StringField()
    # 创建时间
    create_time = DateTimeField(default=datetime.datetime.now)
    # 使用人
    nickname = StringField()
    # 最后修改人的account
    last_edit_user = StringField()
    # 最后修改时间
    last_edit_time = DateTimeField()

    def set_password(self, password):
        """修改密码"""
        pwd = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        self.hash_password = pwd
        self.save()


class User(DynamicDocument):
    """
    user表是公司信息
    """
    app_key = StringField(unique=True)

    app_secret = StringField()

    permissions = ListField()

    ip_list = ListField()

    ''' 以下account、password、user_type不会再使用
    　　而是在Account表中。
    '''
    account = StringField()
    password = StringField()
    user_type = IntField(default=0)

    # 用户文档权限
    param_limit = ListField(DictField())
    ''' 公司名'''
    companyname = StringField(unique=True)
    # 默认的api名字的顺序
    api_type_sort = ListField()

    # 注册时间，接入时间
    no_get_api_time = DateTimeField(default=datetime.datetime.now())
    # 包含了该公司所有的包月接口,
    monthly = ListField(default=[])
    # 是否存在一个非包月的接口
    # is_not_monthly = ListField(default=[])
    # 目前的非包月的情况的判断是 permissions列表减去0
    # monthly列表 剩下的 元素表示该公司非包月的接口



class ApiList(DynamicDocument):
    """接口表"""
    # 接口的名字, 中文表示, 给前端展示
    api_name = StringField(unique=True)
    # icon 地址
    icon_link = StringField()
    # icon 对应的应用接口说明
    icon_des = StringField()
    # 接口类型,用来和 数据聚合的表 对接
    # 接口大类
    interface = StringField(default="interface")
    # 接口小类
    api_type = StringField(unique=True)
    # 应用接口图例
    img = StringField()
    # 管理端需要增加部分字段
    # 测试状态 {app_key1: 1, app_key2: 0}
    measure_status = DictField(default={})
    # 测试数量
    measure_count = DictField(default={})
    # 正式状态
    offical_status = DictField(default={})
    # 接口是否已经使用， 接口本身的状态，不关乎用户
    # 当 is_open 为 0 的时候， 表示 接口还在开发中，此时measure_status 表示是否对用户显示。
    # 当is_open为１时，表示是否可测试状态
    is_open = IntField(default=1)
    # 表示一个接口是否进行过包月，不管是一个公司还是多个公司，只要有一个就置为1
    is_monthly = IntField(default=0)
    meta = {
        "collection": "apilist"
    }
    # 所有需要进行权限控制的字段进行保存，而不是放进配置文件中
    # 每一个元素目前都是一个字典
    '''{'description': u'是否结婚',
            'name': u'isMarried'
            xxx}
    '''
    all_auth_field = ListField(default=[])

    # api babel 接口标签
    label = ListField()

    # 后面迭代版本如果需要增加新的字段， 推荐使用ext_property开头，以表示扩展属性
    # 扩展属性， 表示是否 使用到模块中
    ext_property_used = BooleanField(default=False)

    # 用来设置事务
    pendingTransactions = ListField(default=[])

    # 这个是一个默认的时间, 每次不同的用户会进行覆盖
    ext_property_default_time = DateTimeField(
        default=datetime.datetime.now(), required=True)
    # 存储每个用户的时间
    # {'user1': '2016-08-09 08:00:00'}
    ext_property_user_time = DictField()
    # 渠道
    channel = StringField()
    # 计费方式
    billing = StringField()
    # 备注
    remark = StringField()
    # 第三方权限
    '''
    {
      'method': 'tianxing_idcard',
      'channel': u'天行',
      "weight": 0.1
    }
    '''
    three_auth = ListField()


class ApiModule(DynamicDocument):
    # 模块包含
    include_api = ListField(ReferenceField(ApiList))
    # 用来做顺序
    index = IntField(default=1)
    # 所属用户，存储的实际上是　app_key的值
    belong_user = ListField()
    # the name of the module
    module_name = StringField(unique=True)

    # 用来设置事务
    pendingTransactions = ListField(default=[])


class CacheDay(DynamicDocument):
    """
    定时去缓存每一天的调用情况，
    对当天的调用情况，将数据存储到redis中去读取
    """
    # 缓存的日期, 格式20161011
    cache_time = StringField(required=True)
    app_key = StringField(required=True)
    api_type = StringField(required=True)
    # 默认这次调用是非包月的， 0表示非包月
    monthly = IntField(default=0)
    # 成功调用的次数
    count_success = IntField(default=0)
    # 成功匹配次数
    count_match = IntField(default=0)
    meta = {
        "collection": "cacheday",
    }


class DocData(DynamicDocument):
    '''文档相关数据'''

    # 接口小类
    interface = StringField(default='interface')
    # 接口分类
    api_type = StringField(unique=True)
    # 接口描述
    serviceDescription = ListField()
    # 请求参数
    submitParams = DynamicField()
    # 相应数据
    responseData = DynamicField()
    # 接口名称
    name = StringField(unique=True)
    # 错误码
    errorCode = DynamicField()
    # 附表
    additionInfo = DynamicField()
    # 接口状态
    state = IntField(default=1)

    meta = {
        "collection": "docdata",
    }


class CheckDownload(DynamicDocument):
    """校验下载链接"""
    # download key
    key = StringField()

    meta = {
        "collection": "check_down"
    }

    @classmethod
    def save_key(cls, key):
        CheckDownload(key=key).save()
        return True


# 用来管理事务
class transactions(DynamicDocument):
    api_id = ObjectIdField(required=True)
    module_id = ObjectIdField(required=True)

    # True表示 add, False 表示 delete 操作
    operator = BooleanField(required=True)
    # 事务的状态
    state = StringField(required=True, default='initial')
    # 最后更改状态的时间
    lastModified = DateTimeField(required=True)


class RequestRecordIn(DynamicDocument):
    """接入接口的记录"""

    app_key = StringField()

    create_time = DateTimeField()
    # api 大的分类
    # 接口大类
    interface = StringField()

    params = DictField()

    result = DynamicField()
    # 1 是成功
    success = IntField()
    # 匹配
    match = IntField()
    # 接口小的分类
    # 接口小分类, 统一以下划线来分开
    api_type = StringField()
    repeat = IntField()

    # 第三方类型
    in_type = StringField()

    meta = {
        'collection': 'request_record_in',
        'indexes': [
            [('api_type', 1)],
            [('app_key', 1)],
            [('create_time', 1)],
            [('success', 1)],
            [('match', 1)],
            [('in_type', 1)],
        ]
    }


class ApiListIn(DynamicDocument):
    """接入接口表"""
    # 接口的名字, 中文表示, 给前端展示
    api_name = StringField(unique=True)
    # 接口类型,用来和 数据聚合的表 对接
    # 接口大类
    interface = StringField(default="interface")
    # 接口小类
    api_type = StringField()
    # 接入接口小类
    in_type = StringField(unique=True)
    # 渠道
    channel = StringField()
    icon_link = StringField()

    meta = {
        "collection": "apilistin"
    }


class CacheDayIn(DynamicDocument):
    """接入接口缓存"""

    meta = {
        "collection": "cachedayin"
    }
