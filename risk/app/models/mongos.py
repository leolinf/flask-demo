# -*- coding: utf-8 -*-

from app.core.logger import project_logger
import datetime

from mongoengine import Document, FileField, DateTimeField, StringField, \
    DictField, IntField, ListField, EmbeddedDocumentField, EmbeddedDocument, \
    BooleanField, EmbeddedDocumentListField, DynamicDocument, DynamicField


class ErrorMsg(Document):
     """记录马上数据的错误请求"""
     singlesearch_apply_number = StringField()
     result = DictField(default={})


class SingleSearch(Document):
    """单条记录"""

    # 进件单号( 也是和mysql 关联的唯一id)
    apply_number = IntField(unique=True)
    # 姓名
    name = StringField()
    # 手机号
    phone = StringField()
    # 身份证号
    id_num = StringField()
    # 银行卡号
    bank_num = StringField()
    # 企业名称
    enterprise_name = StringField()
    # 常用地址
    address = StringField()
    # 图片
    id_face = FileField()
    # 邮箱
    email = StringField()
    # 座机号
    machine_number = StringField()
    # 公司地址
    enterprise_addr = StringField()

    # 银行卡三要素认证
    is_bank_num = DictField()
    # 小视银行卡三要素认证
    name_idcard_account = DictField()
    # 身份认证
    is_person = DictField()
    # 地址信息
    address_info = DictField()
    # 电商平台高危客户
    e_business_danger = DictField()
    # 信息平台高危客户
    info_danger = DictField()
    # 网贷逾期黑名单
    loan_over_time_blacklist = DictField()
    # 多平台借贷注册校验A
    multiple_loan = DictField()
    # 失信黑名单
    no_faith_list = DictField()
    # 手机号标注黑名单
    phone_mark_blaklist = DictField()
    # 手机号关联多账户
    phone_relative = DictField()
    # 手机注册及活跃度综合校验
    phone_verify = DictField()
    # 社交平台高危用户
    social_danger = DictField()
    # 是否触犯规则
    is_break_rule = IntField(default=0)
    # 创建人
    user_id = StringField()
    # 创建时间
    create_time = DateTimeField()
    # 查询状态
    status = IntField(default=1)
    # 是否已经加入贷中监控
    is_add_monitor = IntField(default=0)
    # 电商消费记录
    tel_record = DictField()
    # 企业工商信息
    enterprise = DictField()
    # 马上负面信息借口
    mashang_negative = DictField()
    # 马上失信详情
    mashang_shixin = DictField()
    # 马上简项身份核查
    mashang_idcard = DictField()
    # 马上信用评分
    mashang_score = DictField()
    # 马上逾期信息
    mashang_overdue = DictField()
    # 马上在网时长
    mashang_online = DictField()
    # 马上综合反欺诈
    mashang_credit = DictField()
    # 马上人脸验证
    mashang_face = DictField()
    # 优拉人脸验证
    youla_face = DictField()
    # 马上手机实名认证数据, 和在网时长的数据一样, 只是为了方便统计
    mashang_phone = DictField()
    # 运营商数据
    operator_data = DictField()

    # 马上接口 是否查询
    is_query = DictField()
    # 自己的单号
    number = StringField()
    # 公司名
    company_id = IntField()
    # 审批状态 1/2/3/4/5/6/7/8 未审批/初审中/已初审/复审中/已复审/终审中/通过/拒绝
    approve_status = IntField(default=1)
    # 进件时间
    apply_time = DateTimeField()
    # 审核时间 注意：只有通过或拒绝才有这个时间
    approve_time = DateTimeField()
    # 占用者
    block_user = StringField()
    # 开始占用时间
    block_time = DateTimeField()
    # 被占用
    is_blocked = IntField(default=0)

    # 欣颜进见系统接口传入参数
    inlet_xinyan = StringField()

    # 最新的初审内容
    first_view = DictField()
    # 最新的复审内容
    second_view = DictField()
    # 最新的终审内容
    third_view = DictField()

    # 贷中监控的ID
    monitor_id = StringField(default='')
    # 前段显示的权限
    permission = DictField()
    # 后端读数据的权限
    permission_func = ListField()

    # 运营商的 token 和 status信息
    capcha_info = DictField()

    # 运营商获取的 token的具体数据
    capcha_detail = DictField()

    # 用来后期 实现 重传机制, 保证数据一定会写入
    is_token = IntField()

    # 商户number
    merchant_num = IntField()

    e_business_danger_home = DictField()
    e_business_danger_work = DictField()
    e_business_danger_school = DictField()

    info_danger_home = DictField()
    info_danger_work = DictField()
    info_danger_school = DictField()

    social_danger_home = DictField()
    social_danger_work = DictField()
    social_danger_school = DictField()
    address_match_work = DictField()
    address_match = DictField()

    # 家庭联系人
    phone_home = StringField()
    # 单位联系人
    phone_work = StringField()
    # 学校联系人
    phone_school = StringField()

    # 新的在网时长接口
    channel_cellphone = DictField()
    # 公安不良信息
    undesirable_info = DictField()

    # 坐标，形如{'businessCoordinates': "104.070770,30.542892", 'liveCoordinates': "104.070770,30.542892", 'thirdCoordinates': "104.070770,30.542892"}
    location = DictField()
    # 距离，形如{'bussiness2live': '2', 'live2third': '3', 'third2business': '2'}
    distance = DictField()

    # 金融平台信用风险查询
    channel_riskinfocheck = DictField()
    # 网贷逾期黑名单T1
    channel_netloanblacklist = DictField()
    # 黑名单校验
    blacklist_check = DictField()
    # 用户被关联信息
    user_contact_info = DictField()
    # 用乎被查询信息
    user_queryed_info = DictField()
    # 手机号在网时长W1(中诚信)
    operator_phonetime_data = DictField()
    # 不良信息查询W1(维氏盾)
    obtain_riskinfocheck_data = DictField()
    # 多平台借贷（卧龙）
    operator_multiplatform_data = DictField()
    overdue_b = DictField()
    overdue_c = DictField()
    multiple_loan_apply_a = DictField()
    multiple_loan_apply_b = DictField()
    multiple_loan_register_b = DictField()
    # 金融行业不良信息
    financial_bad = DictField()

    # 社保task_id
    social_security_id = StringField()
    # 社保数据
    social_security_data = DictField()
    # 社保原始数据
    social_security_original = DictField()
    # 公积金task_id
    public_funds_id = StringField()
    # 公积金数据
    public_funds_data = DictField()
    # 公积金原始数据
    public_funds_original = DictField()
    # 人行报告数据
    bank_report_data = DictField()
    # 淘宝数据
    taobao_data = DictField()

    # gps地址
    gps_address = StringField()

    # 人像相似度对比验证W1
    obtain_piccompare = DictField()

    def update_repeat(self, **kw):
        self.update_mashang(save_flag=False, **kw)
        self.save()

    def update_mashang(self, save_flag=True, **kw):
        """ 如果save_flag 设置为flase,那么这个update是不会更新到数据库中的"""
        def status_result(result):
            if not result:
                return False
            if ('result' not in result) and (result.get('is_success',None) == 'F'):
                project_logger.warning('[TIME|%s]mashang result error %s',
                                       datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                       str(result))
                ErrorMsg(singlesearch_apply_number=str(self.apply_number), result=kw).save()
                return False
            else:
                return True

        for key, value in kw.items():
            if key.startswith('mashang_'):
                if status_result(value) is True:
                    setattr(self, key, kw.get(key, {}))
        if save_flag is True:
            self.save()


class InterfaceStat(Document):
    """接口调用统计"""

    # 对应公司的id字段
    company_id = StringField()
    # 公司名称
    company_name = StringField()
    # 商户number
    merchant_num = StringField()
    # 商户名称
    merchant_name = StringField()
    # 模块名称 参见constant.MODULE_DICT
    module_name = StringField()
    # 接口方法名 参见constant.MODULE_DICT
    func_name = StringField()
    # 是否成功调用 1/0 success/fail
    is_success = IntField()
    # 是否命中 1/0 success/fail
    is_target = IntField()
    # 创建时间
    create_time = DateTimeField()
    # 日期时间戳 以秒为单位
    date = IntField()


class MonitorSearch(Document):
    """贷中监控"""

    # 与mysql 对应的monitor 的id
    monitor_id = IntField(unique=True)
    # 姓名
    name = StringField()
    # 手机号
    phone = StringField()
    # 身份证号
    id_num = StringField()
    # 异常项数
    break_num = IntField(default=0)
    # 电商平台高危客户
    e_business_danger = DictField()
    # 信息平台高危客户
    info_danger = DictField()
    # 网贷逾期黑名单
    loan_over_time_blacklist = DictField()
    # 多平台借贷
    multiple_loan = DictField()
    # 失信黑名单
    no_faith_list = DictField()
    # 手机号标注黑名单
    phone_mark_blaklist = DictField()
    # 手机号关联多账户
    phone_relative = DictField()
    # 社交平台高危用户
    social_danger = DictField()

    # 创建时间
    create_time = DateTimeField()
    # 最后异常时间
    last_break_time = DateTimeField()
    # 创建人
    user_id = IntField()
    # 电商购物趋势
    time_line_data = ListField()
    # 贷中异常趋势
    unusual_trend = ListField()

    number = StringField()

    last_update_time = DateTimeField()

    # 公司id
    company_id = IntField()
    #
    status = IntField()

    # 商户number
    merchant_num = IntField()

    meta = {
        'collections':'monitor_search',
        'indexes': ["monitor_id"],
        'index_background': True,
    }


class ImportSearch(Document):
    """上传的文件"""

    create_time = DateTimeField()
    data = FileField()

    meta = {
        'indexes': [
            {
                'fields': ['create_time'],
                'expireAfterSeconds': 60 * 60,
            }
        ]
    }


class Uploading(Document):
    """上传中"""

    # 创建人
    user_id = IntField()
    # 总量
    total = IntField()
    # 成功数
    success = IntField()
    # 正在加入贷中监控的数
    doing = IntField()
    # 重复的
    duplicate = IntField()
    # A/B single_search/monitor
    upload_type = StringField()


class FakeScore(Document):
    """伪造评分"""

    phone = StringField()
    # 低风险
    one = IntField(default=-1)
    two = IntField(default=-1)
    three = IntField(default=-1)
    four = IntField(default=-1)
    # 高风险
    five = IntField(default=-1)


class Caching(DynamicDocument):
    """
    目前用来存贷前风险评估的缓存
    """

    search_id = IntField()

    resp = DictField()


class SearchCache(DynamicDocument):
    """信用报告的缓存"""

    apply_number = IntField(unique=True)


class PhoneAddress(DynamicDocument):
    """手机号归属地"""

    phone = StringField()
    address = StringField()


class IdcardAddress(DynamicDocument):
    """身份证号归属地"""

    idcard = StringField()
    address = StringField()


class BreakRule(DynamicDocument):
    """自动拒绝的触犯规则"""

    apply_number = IntField(unique=True)

    break_rule = ListField()
