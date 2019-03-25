# -*- coding: utf-8 -*-

from sqlalchemy import (
    Column, Integer, String, ForeignKey, BigInteger, DateTime,
    func, TEXT, Boolean, UniqueConstraint, Numeric,
    Table)
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from flask_login import UserMixin
from sqlalchemy.dialects.mysql import VARCHAR

from ..constants import SearchStatus, MonitorStatus, ApproveStatus

Base = declarative_base()


class Company(Base):
    """公司"""

    __tablename__ = 'company'

    # 公司ID
    id = Column(BigInteger, primary_key=True)
    # 公司名字
    name = Column(String(128))
    # 进件系统的协议+网址 如： https://baidu.com
    into_url = Column(String(64), nullable=False)
    # 接口访问权限，JSON格式
    permissions = Column(TEXT, nullable=False)
    # logo链接
    logo_url = Column(String(64))
    # 联系人姓名
    linkman_name = Column(String(32))
    # 联系人电话
    linkman_phone = Column(String(16))
    # 联系人身份证号
    linkman_idcard = Column(String(32))
    # 公司所在省
    province = Column(String(32))
    # 公司所在市
    city = Column(String(32))
    # 公司地址
    address = Column(String(128))
    # 工商注册号
    ic_code = Column(String(32))
    # 组织机构代码
    org_code = Column(String(32))
    # 税务等级证号
    tax_code = Column(String(32))
    # 公章图片
    cachet_url = Column(VARCHAR(256))
    # 合同附件
    contract_url = Column("contract_url_fs", VARCHAR(256))
    contract_name = Column(String(32))
    bestsign_info = relationship('BestsignInfo', uselist=False)
    # 公司类型 1/2 正式/演示
    company_type = Column(Integer, default=1)
    # 公司最大演示次数
    max_input = Column(Integer)
    # 公司使用状态 1-合作中，2-暂停合作
    collaborate_status = Column(Integer, default=1)
    if_online_sign_contract = Column(Boolean, default=False)


class User(Base, UserMixin):
    """平台可登陆的用户"""

    __tablename__ = 'sys_user'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    # 用户名，唯一
    username = Column('username', String(64), unique=True)
    # 密码，加密后的值
    password = Column('password', String(256))
    # 最后登录时间
    last_login = Column('last_login', DateTime)
    # 公司ID
    # company_id = Column(BigInteger, ForeignKey('company.id'), nullable=False)

    # 公司，关系，不实际存在
    # company = relationship('Company', uselist=False)

    # 是否删除 0-否，未删除，1-是，已删除
    # is_delete = Column(Integer, default=0)


class InputApply(Base):
    """进件信息"""

    __tablename__ = 'input_apply'

    id = Column(BigInteger, primary_key=True, autoincrement=False)
    # 姓名
    name = Column(String(32))
    # 手机号
    phone = Column(String(16), nullable=False, index=True)
    # 身份证号
    idcard = Column(String(32), index=True)
    # 银行卡号
    banknum = Column(String(32))
    # 邮箱
    email = Column(String(32))
    # QQ号
    qq_num = Column(String(16))
    # 是否是学生
    is_student = Column(Boolean)
    # 短信
    sms_code = Column(String(16))
    # 用户申请协议
    application_protocol = Column(Boolean)

    # 创建时间
    create_time = Column(DateTime, server_default=func.now(), index=True)
    # 更新时间
    last_update = Column(DateTime, onupdate=func.now())
    # 商户ID
    merchant_id = Column(BigInteger, ForeignKey('merchant.id'), nullable=False)
    # 公司ID
    company_id = Column(BigInteger, ForeignKey('company.id'), nullable=False)
    # 利率表的ID
    interest_id = Column('merchant_goods_id', BigInteger , ForeignKey('product.id'), nullable=False)
    # 利率表信息快照，JSON格式
    # interest_snapshot = Column(TEXT)
    # 表单快照，JSON格式
    apply_table_snapshot = Column(TEXT)
    # 产品名称
    product_name = Column(String(64))
    # 产品金额
    product_money = Column(Numeric(19, 7))
    # 借款金额
    loan_money = Column(Numeric(19, 7))
    # 银行卡账户名
    account = Column(String(32))
    # 借款期数
    instalments = Column(Integer)
    # 每月还款金额
    each_month_repay = Column(Numeric(19, 7))
    # 产品类别
    product_type = Column(String(64))
    # 申请参加保险
    is_insurance = Column(Boolean)
    # 还款随心包
    need_repay_package = Column(Boolean)
    # 银行预留手机号
    bank_with_phone = Column(String(32))
    # 开户行名称
    bank_name = Column(String(64))
    # 到账银行卡号
    bank_num = Column(String(64))

    #########
    # 工作信息
    #########
    # 单位名
    work_company_name = Column(String(128))
    # 职位
    work_position = Column(String(256))
    # 单位联系人
    work_contact_name = Column(String(32))
    # 单位地址
    work_address = Column(String(256))
    # 详细地址
    work_detail_address = Column(String(256))
    # 月收入
    work_month_income = Column(String(32))
    # 工作年限
    work_year = Column(String(32))
    # 所属行业
    work_industry = Column(String(128))
    # 单位性质
    work_nature = Column(String(128))
    # 单位规模
    work_scale = Column(String(128))
    # 单位联系人电话号码
    work_contact_phone = Column(String(64))
    #########
    # 教育信息
    #########
    # 学校名称
    school_name = Column(String(128))
    # 学历
    school_education = Column(String(128))
    # 入学时间
    school_start = Column(DateTime)
    # 专业名称
    school_major = Column(String(64))
    # 学校联系人姓名
    school_contact = Column(String(64))
    # 与联系人关系
    school_contact_relation = Column(String(64))
    # 学校联系人电话
    school_contact_phone = Column(String(32))
    #########
    # 家庭信息
    #########
    # 家庭及居住情况
    home_marriage = Column(String(256))
    # 配偶姓名
    home_mate_name = Column(String(32))
    # 配偶联系电话
    home_mate_phone = Column(String(32))
    # 供养人数
    home_num_support = Column(String(32))
    # 住房类型
    home_house_type = Column(String(64))
    # 居住时间
    home_live_time = Column(String(256))
    # 居住地址
    home_live_address = Column(String(256))
    # 家庭详细地址
    home_detail_address = Column(String(256))
    # 家庭成员姓名
    home_mem_name = Column(String(32))
    # 与申请人关系
    home_mem_relation = Column(String(64))
    # 联系电话
    home_mem_phone = Column(String(32))
    #########
    # 信贷信息
    #########
    # 是否有房贷
    credit_house = Column(Boolean)
    # 是否由车贷
    credit_car = Column(Boolean)
    # 是否由其他贷款
    credit_other = Column(Boolean)
    # 是否由信用卡
    credit_crecard = Column(Boolean)

    # 芝麻信用分截图
    seasame_credit = Column(VARCHAR(256))

    # 身份证正面照
    id_face = Column(VARCHAR(256))
    # 身份证背面照
    id_back = Column(VARCHAR(256))
    # 银行卡照
    bank_card = Column(VARCHAR(256))
    # 手持身份证照
    photo_with_card = Column(VARCHAR(256))
    # 学信网照片
    student_phone = Column(VARCHAR(256))
    others_img = Column(TEXT)
    # 运营商授权
    is_capcha = Column(Boolean)
    # 运营商授权的token
    token = Column(String(64))
    # marriage = Column(String(64))
    # 借款状态
    loan_status = Column(Integer)

    # 商户信息快照
    merchant_info = Column(TEXT)

    # 进件人ID
    input_user_id = Column(BigInteger, ForeignKey('input_user.id'), nullable=False)
    # 来源 1/2 移动端/web端
    local_state = Column(Integer)
    # 进件状态  1/2 测试进件/正式进件
    apply_type = Column(Integer)

    # 商户
    merchant = relationship('Merchant', uselist=False)
    # 进件人
    input_user = relationship('InputUser', uselist=False)

    # 是否欺诈
    is_break_rule = Column(Boolean, index=True)
    # 查询状态
    status = Column(Integer, nullable=False, index=True, default=SearchStatus.NO)
    # 审批状态
    approve_status = Column(Integer, index=True, default=ApproveStatus.WAITING)
    # 审批时间
    approve_time = Column(DateTime, index=True)
    # 评分
    score = Column(String(8))
    # 接口访问权限快照，JSON格式
    permissions_snapshot = Column(TEXT, nullable=False)
    # 运营商状态 0/1/2 不查运营商/查询中/查询完成
    operator = Column(Integer)

    # 第一步的审核 JSON格式
    first_view = Column(TEXT)
    # 第二步的审核 JSON格式
    second_view = Column(TEXT)
    # 第三步的审核 JSON格式
    third_view = Column(TEXT)
    # 最后一步的内容
    content = Column(TEXT)
    # 是否被锁
    is_locked = Column(Boolean, default=False)
    # 占用者ID
    lock_user_id = Column(BigInteger, ForeignKey('sys_user.id'))
    # 开始占用时间
    lock_time = Column(DateTime)
    # 查询状态
    search_status = Column(Integer)

    # 社保task_id
    social_security_id = Column(String(64))
    # 公积金task_id
    public_funds_id = Column(String(64))
    # 人行id
    credit_investigation_id = Column(String(256))
    # 淘宝id
    tb_id = Column(String(256))

    # 订单号的MD5编码
    md_order = Column(String(256))
    # 短信发送状态
    credit_investigation_status = Column(Integer)
    # 审核日志
    review_log = relationship('ReviewLog', back_populates='input_apply')
    # 占用者
    lock_user = relationship('User', uselist=False)
    # 公司，关系，不实际存在
    company = relationship('Company', uselist=False)
    # 合同
    bestsign_contract = relationship('BestsignContract', uselist=False)
    # 完成时间
    apply_time = Column(DateTime)
    # 对应贷后监控的ID
    monitor_id = Column(BigInteger, ForeignKey('loan_monitor.id'))


    loan_use = Column(String(64))
    others_earn = Column(BigInteger)
    unit_phone = Column(String(64))
    work_year_income = Column(String(64))
    work_year_unit = Column(String(64))
    work_contact_relation = Column(String(64))
    registered_residence = Column(String(64))
    credit_crecard_num = Column(Integer)
    maximum_amount = Column(BigInteger)
    contacts_idcard = Column(String(64))
    contacts_school_record = Column(String(64))
    contacts_work_unit = Column(String(64))
    contacts_position = Column(String(64))
    contacts_year_income = Column(String(64))
    contacts_others_income = Column(String(64))
    political_status = Column(String(64))
    bank_loan = Column(String(64))
    private_loan = Column(String(64))
    others_liabilities = Column(String(64))
    houses_num = Column(String(64))
    houses_message = Column(String(256))
    car_num = Column(String(64))
    car_message = Column(String(256))

    # 进件GPS { code: 0, latitude: position.coords.latitude, longitude: position.coords.longitude, }1: // 用户拒绝 2:　// 获取位置信息不支持 3:　// 获取位置信息超时 4:　// 浏览器不支持
    location = Column(String(512))


class BestsignUser(Base):
    """上上签用户"""

    __tablename__ = 'bestsign_user'

    # 手机号
    phone = Column(String(16), primary_key=True)
    # 名字
    name = Column(String(32))
    # 身份证号
    idcard = Column(String(32))
    # 上上签的uid
    uid = Column(String(32), nullable=False)
    # 创建时间
    create_time = Column(DateTime, server_default=func.now())
    # 认证时间
    cert_time = Column(DateTime)


class ApplyTable(Base):
    """进件申请表"""

    __tablename__ = 'apply_table'

    id = Column(BigInteger, primary_key=True)
    # 名字
    name = Column(String(32))
    # 公司ID
    company_id = Column(BigInteger, ForeignKey('company.id'), nullable=False)
    # 创建时间
    create_time = Column(DateTime, server_default=func.now())
    # 0/1 关闭/启用
    status = Column(Boolean, default=True)
    # 版本号
    version = Column(String(64))
    # 申请表类型 1/2/3 默认/推荐/自定义
    apply_type = Column(Integer, nullable=False, default=3)
    # 公司，关系，不实际存在
    company = relationship('Company', uselist=False)
    # 模块
    modules = relationship('ApplyModule')
    # 个性化配置
    custom_config = Column(TEXT)


class ApplyModule(Base):
    """申请表模块"""

    __tablename__ = 'apply_module'

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 名字
    name = Column(String(32))
    # 模块顺序，从1开始
    index = Column(Integer, nullable=False)
    # 大模块的状态
    immutable = Column(Boolean)

    apply_table_id = Column(BigInteger, ForeignKey('apply_table.id', ondelete='CASCADE'), nullable=False)

    pages = relationship('ApplyPage')


class ApplyPage(Base):
    """申请表模块的页"""

    __tablename__ = 'apply_page'

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 页码顺序，从1开始
    index = Column(Integer, nullable=False)
    apply_module_id = Column(Integer, ForeignKey('apply_module.id', ondelete='CASCADE'), nullable=False)

    fields = relationship('ApplyField')


class ApplyField(Base):
    """申请表页的具体字段"""

    __tablename__ = 'apply_field'

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 分页下小模块的名字
    submodule_name = Column(String(32))
    # 分页下小模块是否是自定义的
    submodule_is_ext = Column(Integer)
    # the key for submodule_name
    submodule_key = Column(String(32))
    submodule_index = Column(Integer)
    # 英文，键名
    key = Column(String(32))
    # 中文， 展示
    name = Column(String(32))
    # 是否是额外添加的字段
    is_ext = Column(Boolean, default=False)
    # 是否展示
    is_show = Column(Boolean, default=True)
    # 是否必须
    is_required = Column(Boolean, default=False)
    # 输入的类型
    type_choice = Column(Integer, nullable=False)
    # 是否可以改变
    changable = Column(Boolean, default=True)
    # 字段备注
    remark = Column(String(128))
    # 字段索引
    field_index = Column(Integer)

    apply_page_id = Column(Integer, ForeignKey('apply_page.id', ondelete='CASCADE'), nullable=False)

    __table_args__ = (
        UniqueConstraint('key', 'apply_page_id', 'submodule_key', name='uix'),
    )


class Merchant(Base):
    """商户"""

    __tablename__ = 'merchant'

    # 商户ID，因为要写在链接上并且不能暴露有多少个公司
    id = Column(BigInteger, primary_key=True)
    name = Column(String(64))
    # 组织机构代码
    org_code = Column(String(32), nullable=False)
    # 等级
    level = Column(String(8), nullable=False)
    # 商户电话
    merchant_phone = Column(String(16), nullable=False)
    # 地址
    address = Column(String(128), nullable=False)
    # 联系人姓名
    linkman_name = Column(String(32), nullable=False)
    # 联系人电话
    linkman_phone = Column(String(16), nullable=False)
    # 签约时间
    sign_time = Column(DateTime, nullable=False)
    # 宣传渠道
    publish_channel = Column(String(128))
    # 备注
    remarks = Column(TEXT)
    # 0/1 停止/开启合作
    status = Column(Boolean, default=True)
    # 合同附件链接
    contract_url = Column(VARCHAR(256))
    # 执照链接
    license_url = Column(VARCHAR(256))
    # 营业执照名称
    license_name = Column(String(64))
    # 合同附件名称
    contract_name = Column(String(64))
    # 公司ID
    company_id = Column(BigInteger, ForeignKey('company.id'), nullable=False)
    product_id = Column(BigInteger, ForeignKey('product.id'), nullable=False)
    # 商户二维码链接
    qrcode_url = Column(VARCHAR(256), nullable=False)
    # 公司，关系，不实际存在
    company = relationship('Company', uselist=False)
    product = relationship('Product', uselist=False)
    # 结算账户
    banknum = Column(String(64))
    merchant_user = relationship("MerchantUser", uselist=False, back_populates="merchant")
    create_time = Column(DateTime)


class Product(Base):
    """产品"""

    __tablename__ = 'product'

    # 产品ID，因为要写在链接上并且不能暴露
    id = Column(BigInteger, primary_key=True)
    # 公司ID
    company_id = Column(BigInteger, ForeignKey('company.id'), nullable=False)
    # 申请表ID
    apply_table_id = Column(BigInteger, ForeignKey('apply_table.id'), nullable=False)
    # 利率表信息，JSON格式，形如[{"name":3,"month_rate":"1.00","month_serve":"1.00","month_manage_rate":"1.00","month_insurance_rate":"1.00","package_charge":"0"}]
    interest = Column(TEXT)
    name = Column(String(64))
    recieve_type = Column(Integer)
    repay_type = Column(Integer)


class Monitor(Base):
    """贷后监控"""

    __tablename__ = 'loan_monitor'

    id = Column(BigInteger, primary_key=True, autoincrement=False)
    # 姓名
    name = Column(String(32))
    # 手机号
    phone = Column(String(16), nullable=False, index=True)
    # 身份证号
    idcard = Column(String(32), index=True)
    # 状态
    status = Column(Integer, nullable=False, default=MonitorStatus.DOING)
    # 最新异常时间
    last_break_time = Column(DateTime)
    # 异常项数
    break_num = Column(Integer, default=0)
    # 开始监控时间
    create_time = Column(DateTime, server_default=func.now())
    # 用户ID
    user_id = Column(BigInteger, ForeignKey('sys_user.id'))
    # 公司ID
    company_id = Column(BigInteger, ForeignKey('company.id'), nullable=False)
    input_apply_id = Column(BigInteger)

    exception_list = Column(String(512))

    __table_args__ = (
        UniqueConstraint('phone', 'idcard', 'name', 'company_id', name='uix'),
    )


class BestsignInfo(Base):
    """上上签相关信息"""

    __tablename__ = 'bestsign_info'

    id = Column(BigInteger, primary_key=True)
    company_id = Column(BigInteger, ForeignKey('company.id'))

    # 自动签署坐标，形如[{'signx': '0.1', 'signy': '0.1', 'pagenum': '1'}] JSON格式
    auto_sign = Column(TEXT, nullable=False)
    # 手动签署坐标，形如[{'signx': '0.1', 'signy': '0.1', 'pagenum': '1'}] JSON格式
    manual_sign = Column(TEXT, nullable=False)
    # 邮件消息标题
    email_title = Column(String(64), nullable=False)
    # 邮件消息内容
    email_content = Column(String(64), default='')
    # 合同有效天数
    sxdays = Column(String(8), default='30')
    # 收件人姓名
    name = Column(String(32), nullable=False)
    # 用户账户
    phone = Column(String(16), nullable=False)
    # 用户类型
    usertype = Column(String(8), default='2')
    # 用户账户
    email = Column(String(32), nullable=False)
    # 包含视频
    isvideo = Column(String(8), default='0')
    # 当用户不存在时生成系统自动签名 没什么用
    signimagetype = Column(String(8), default='0')
    # 合同文件的相对路径
    path = Column(String(256), nullable=False)


class ReviewLog(Base):
    """审批日志"""

    __tablename__ = 'input_review_history'

    id = Column(Integer, primary_key=True, autoincrement=True)

    input_apply_id = Column(BigInteger, ForeignKey('input_apply.id'))
    # 审核人
    user_id = Column('review_user_id', BigInteger, ForeignKey('sys_user.id'))
    # 创建时间
    create_time = Column('approve_time', DateTime, server_default=func.now())
    # 操作的所有参数 JSON格式
    params = Column(TEXT)
    # 操作内容模板ID v2.2起没有用了
    template_number = Column(Integer)

    input_apply = relationship('InputApply', uselist=False)
    user = relationship('User', uselist=False)


class BestsignContract(Base):
    """上上签合同"""

    __tablename__ = 'bestsign_history'

    id = Column(BigInteger, ForeignKey('input_apply.id'), primary_key=True)

    # 合同编号
    signid = Column(String(32))
    # 文档编号
    docid = Column(String(32))
    # 状态
    status = Column(String(8))
    # 这个是个假的，没有用
    input_apply_id = Column(BigInteger)
    # 这个是真的，但是没有用
    company_id = Column(BigInteger)

    input_apply = relationship('InputApply', uselist=False)


class ExtField(Base):
    """进件信息额外的字段"""

    __tablename__ = 'apply_ext_field'

    id = Column(Integer, primary_key=True, autoincrement=True)
    # 进件信息ID
    input_apply_id = Column(BigInteger, ForeignKey('input_apply.id'), nullable=False)
    # 英文，键名
    key = Column(String(32), name="key_info")
    # 中文， 展示
    name = Column(String(32))
    # 值
    value = Column(String(256))
    # 字段的类型
    field_type = Column(Integer)


class InputUser(Base):
    """进件端用户"""

    __tablename__ = 'input_user'

    id = Column(BigInteger, primary_key=True)

    name = Column(String(32))
    phone = Column(String(16))
    idcard = Column(String(32))
    pass_idcard = Column(Boolean, default=False)

    # 公司ID
    company_id = Column(BigInteger, ForeignKey('company.id'), nullable=False)

    __table_args__ = (
        UniqueConstraint('phone', 'company_id', name='uix'),
    )


class VerifyCode(Base):
    """短信验证码"""

    __tablename__ = 'verify_code'

    phone = Column(String(16), primary_key=True)
    code = Column(String(8), nullable=False)
    # 创建时间
    create_time = Column(DateTime, server_default=func.now())
    # 更新时间
    last_update = Column(DateTime, onupdate=func.now())
    # 当天次数
    times = Column(Integer, default=1)


class SmsTemplate(Base):
    """短信模板"""

    __tablename__ = 'sms_template'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey('company.id'), nullable=False)
    # 业务类型
    service_type = Column(Integer, nullable=False)
    # 短信内容模板
    template = Column(TEXT)

    company = relationship('Company', uselist=False)


class LoanPayHistory(Base):
    """"""

    __tablename__ = 'loan_pay_history'

    id = Column(BigInteger, primary_key=True)

    # 到账金额
    account_money = Column(Numeric(19, 7))
    # 起息日
    value_date = Column(DateTime)
    # 进件单号
    input_apply_id = Column(BigInteger, ForeignKey('input_apply.id'), nullable=False)


class LoanRepayPlan(Base):

    __tablename__ = "loan_repay_plan"

    id = Column(BigInteger, primary_key=True)
    repay_method = Column(String(64))
    # 进件单号
    input_apply_id = Column(BigInteger, ForeignKey('input_apply.id'), nullable=False)


class MerchantUser(Base):

    __tablename__ = "merchant_user"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    merchant_id = Column(BigInteger, ForeignKey('merchant.id'), nullable=False)
    mobile = Column(String(32))
    login_name = Column(String(32))
    login_pwd = Column(String(512))
    create_time = Column(DateTime)
    merchant = relationship("Merchant", back_populates="merchant_user")


class InputApplyUpload(Base):

    __tablename__ = "input_apply_upload"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    serial_number = Column(String(30))

    photo_url = Column(String(1000))

    input_apply_id = Column(BigInteger, ForeignKey('input_apply.id'), nullable=False)


class MerchantGoods(Base):

    __tablename__ = "merchant_goods"

    id = Column(BigInteger, primary_key=True, autoincrement=True)

    describes = Column(TEXT)


class CompanyRule(Base):
    """自动拒绝的规则"""

    __tablename__ = "company_rule"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    company_id = Column(BigInteger, ForeignKey("company.id"), nullable=False)
    # 自动拒绝的
    deny_rule = Column(TEXT)
    # 自动通过的
    pass_rule = Column(TEXT)


class NewReviewLog(Base):
    """新的审核日志"""

    __tablename__ = 'input_review_log'

    id = Column(Integer, primary_key=True, autoincrement=True)

    input_apply_id = Column(BigInteger, ForeignKey('input_apply.id'))
    # 审核人
    user_id = Column('review_user_id', BigInteger, ForeignKey('sys_user.id'))
    username = Column(String(128))
    # 创建时间
    create_time = Column('approve_time', DateTime, server_default=func.now())
    # 操作的所有参数 JSON格式
    params = Column(TEXT)

    input_apply = relationship('InputApply', uselist=False)
    user = relationship('User', uselist=False)
