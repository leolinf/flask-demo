# -*- coding: utf-8 -*-

class Code:
    """错误码"""

    LOGIN_ERROR = 10001 # 登录失败
    NEED_LOGIN = 10024
    UNABLE_LOCK = 10030 # 不能锁
    SEARCH_NOT_EXIST = 10037    # 风控表不存在
    UNVALID_INPUT_ID = 10038
    NOT_LOCKED = 10039      # 没有被锁
    ALREADY_LOCKED = 10040      # 已经被别人锁了
    APPLY_TABLE_SAVE_ERROR = 10041  # 进件表保存失败
    ACCESS_DENIED = 10100 # 不在白名单内，拒绝访问

    # 迁移过来
    SUCCESS = 10000
    MULTI_NOT_EXIST = 10001
    SINGLE_NOT_READY = 10002
    SINGLE_NOT_EXIST = 10003
    UNSUPPORTED_FORMAT = 10004
    MONITOR_ALREADY_EXIST = 10005
    BATCH_NOT_FINISHED = 10006
    MONITOR_NOT_EXIST = 10007
    MONITOR_NOT_READY = 10008
    ALREADY_ADDED_TO_MONITOR = 10009
    SINGLE_ALREADY_BLOCKED = 10010
    SINGLE_NOT_BLOCKED = 10011
    AUTH_ERROR = 10012
    DOES_NOT_EXIST = 10013
    IMG_DOES_NOT_EXIST = 10014
    APPLY_SAVE_ERROR = 10022
    SINGLE_IMCOMPLETE = 10023
    TOKEN_HAS_EXIST = 10025  # 运营商token信息已经保存
    SAVE_TOKEN_ERROR = 10026  # 保存运营商 token 信息失败
    COMPANY_NOT_EXIST = 10027
    MERCH_NOT_EXIST = 10028
    NOT_IMAGE = 10029
    LOAN_NOT_EXIST = 10031
    UNABLE_CONFIRM_LOAN = 10032
    SYNC_MERCH_FAILED = 10035
    CONTRACT_NOT_EXIST = 10036

    # shawn
    # 身份证验证不通过
    VERIFY_FAIL = 11030
    # 申请表正在被使用， 无法禁用
    NOT_DISABLE_APPLY = 11037
    # 合同状态打开， 居住信息是必填项目
    HOME_ADDRESS_CONTRACT_ERR = 11038

    VALID_COMPANY_SERVICE = 11039   # 这个公司没有对应的模板

    # 申请表已经被禁用， 商户不能使用这个申请表
    UNVALID_APPLY_TABLE_ID = 11040

    # 帐号失效
    VALID_ACCOUNT = 11041

    # 访问不属于自己的资源
    NOT_ALLOWED = 12000

    # 未知错误
    SYSTEM_ERROR = 20000

    # ssq sign more than once
    SIGN_OVER_TIME = 10042
    # 商户用户存在
    MERCH_USER_EXISTS = 10043

    MSG = {
        SUCCESS: '成功',
        NEED_LOGIN: '需要登录',
        ACCESS_DENIED: '拒绝访问',
        APPLY_TABLE_SAVE_ERROR: '进件申请表保存失败',
        UNVALID_INPUT_ID: '进件Id错误',
        MULTI_NOT_EXIST: 'this multiple search does not exist',
        SINGLE_NOT_READY: 'this single search not done yet',
        SINGLE_NOT_EXIST: 'this single search does not exist',
        UNSUPPORTED_FORMAT: 'unsupported file type',
        MONITOR_ALREADY_EXIST: 'this monitor already exist',
        BATCH_NOT_FINISHED: 'there is batch not finished',
        MONITOR_NOT_EXIST: 'this monitor not exist',
        MONITOR_NOT_READY: 'this monitor not ready',
        ALREADY_ADDED_TO_MONITOR: 'this single search already added to monitor',
        SINGLE_ALREADY_BLOCKED: 'this single search already blocked',
        SINGLE_NOT_BLOCKED: 'this single search not blocked',
        AUTH_ERROR: 'auth failed!',
        APPLY_SAVE_ERROR: 'input apply error!',
        DOES_NOT_EXIST: 'does not exist!',
        SINGLE_IMCOMPLETE: 'this single search not complete',
        COMPANY_NOT_EXIST: 'this company not exists',
        MERCH_NOT_EXIST: 'this merchant not exists',
        NOT_IMAGE: 'this is not image',
        UNABLE_LOCK: 'this search is unable to be blocked',
        LOAN_NOT_EXIST: 'this loan not exist',
        UNABLE_CONFIRM_LOAN: 'unable to change status of this loan',
        IMG_DOES_NOT_EXIST: 'this image dose not exist',
        SYNC_MERCH_FAILED: 'sync merchant info failed',
        SEARCH_NOT_EXIST: '风控表不存在',
        NOT_ALLOWED: '没有权限访问该资源',
        SIGN_OVER_TIME: "ask for ssq sign url more than once",
        MERCH_USER_EXISTS: "商户用户登录名存在",
    }


class Status:
    """input_apply的status字段"""

    INPUTING = 100      # 进件中
    ENDINPUT = 101      # 进件终止
    SEARCHING = 200     # 查询中
    ENDSEARCH = 201     # 终止查询
    SEARCHFAILED = 202  # 查询失败
    APPROVING = 300     # 审核中
    ENDAPPROVE = 301    # 终止审核
    APPROVEDENIED = 302     # 审核拒绝
    WAITMERCH = 400     # 待商户确认
    ENDMERCH = 401  # 终止确认
    MERCHDENIED = 402   # 商户确认拒绝
    WAITSIGN = 500      # 待签合同
    ENDSIGN = 501       # 终止签合同
    WAITLOAN = 600      # 待确认放款
    ENDLOAN = 601       # 终止确认放款
    LOANDENIED = 602    # 放款拒绝
    LOANSUCCESS = 700   # 放款成功
    LOANFAILED = 701    # 放款失败
    LOANING = 702       # 放款中
    WAITUPLOADPIC = 800     # 待上传发货照片
    ENDUPLOADPIC = 801  # 上传照片超时


class SearchStatus:
    """信用报告的查询状态"""

    NO = 900    # 未查询
    DONE = 902    # 已查询完
    DOING = 901   # 查询中
    FAILED = 903    # 查询失败
    ADD_TO_MONITOR = 904  # 加入贷后监控


class LoanStatus:
    """借款状态, 存在input_apply表的loan_status字段"""

    REFUNDING = 100     # 还款中
    OVERDUE = 200       # 已逾期
    DONE = 300          # 已结清


class MonitorStatus:

    DONE = 1        # 准备好了
    DOING = 2       # 准备中
    STOP = 0        # 停止监控


class ApproveStatus:
    """审批状态"""

    WAITING = 800         # 未审批
    FIRST_DOING = 801     # 初审核
    FIRST_DONE = 802      # 已初审
    SECOND_DOING = 803    # 复审中
    SECOND_DONE = 804     # 已复审
    THIRD_DOING = 805     # 终审中
    PASS = 806            # 通过
    DENY = 807            # 拒绝
    AUTO_DENY = 808       # 自动拒绝 也是吊炸天
    AUTO_PASS = 809       # 自动拒绝 更是吊炸天


class ViewStatus(object):
    """ 审核状态 """
    VIEW_FIRST = 1   # 初审
    VIEW_SECOND = 2  # 复审
    VIEW_THIRD = 3   # 终审
    VIEW_BACK = 4    # 通过拒绝 回退到 已复审


class InputApplyStatus:
    """进件端的状态, 存在input_apply的loan_status"""

    APPROVING = 1   # 审批中
    DENIED = 2      # 被拒绝
    WAITMERCH = 3   # 待商户确认
    MERCHDENY = 4   # 商户确认未通过
    WAITSIGN = 5    # 待签合同
    LOANING = 6     # 已签署合同
    REFUNDING = 7   # 交易成功
    FAILED = 8      # 交易失败


class ReceiveType:
    """
    产品类型，1:现金贷,2:消费分期 3.运营商手机分期
    """

    MERCHANT = 1
    CLIENT = 2
    BANDANYUAN = 3


class LocalState:

    MOBILE = 1
    WEB = 2


class ViewLogTemp(object):
    # 操作内容模板
    TEMPLATE = {
        1: '将审批状态由’未审批‘改为‘已初审’',
        2: '将审批状态由’已初审‘改为‘已复审’',
        3: '将审批状态由’已复审‘改为‘通过’',
        4: '将审批状态由’已复审‘改为‘拒绝’',
        5: '将审批状态由’拒绝‘改为‘已复审’',
        6: '将审批状态由’拒绝‘改为‘通过’',
        7: '将审批状态由’通过‘改为‘已复审’',
        8: '将审批状态由’通过‘改为‘拒绝’',
        9: "命中自动初筛拒绝规则，系统初筛自动拒绝",
        10: "自动通过",
    }


class CreditUri:
    KEY = '7lH1jUnhToOUslaO0EVwOwLz1H0ts4ab'
    TELRISKLIST = '/credit/telrisklist/get?'
    MANYPLAT = '/credit/manyplatcheck/get?'
    LOAN_OVER = '/credit/netblacklist/get?'
    PHONERLATE = '/credit/phonedevicecheck/get?'
    INFODANGER = '/credit/newsplatrisk/get?'
    PHONEMARK = '/credit/phoneblack/get?'
    PHONEACTIVE = '/credit/phonemsgcheck/get?'
    SOCIAL = '/credit/socialblacklist/get?'
    SYNTHESIS = '/credit/synthesis/get?'
    # FAITH = '/credit/person/get?'
    FAITH = '/credit/implement?'
    SHIXIN = '/credit/enterprise/get?'
    IDCARDCHECK = '/channel/idcard/get?'
    BANK3 = '/channel/bankby3/get?'
    TELURL = '/tel/batch/get?'
    TELURL_BASICS = '/tel/basics/batch/get?'
    PORTRAIT = '/portrait/active/get?'
    ADDRESS = '/address/getbymobile?'
    COURT = '/enterprise/court/get?'
    JUDGMENT = '/enterprise/judgment/get?'
    ZHIXING = '/enterprise/zhixing/get?'
    FIRMINFO = '/enterprise/info/get?'
    NameIdCardAccount = '/channel/NameIDCardAccountVerify/get?'
    ADDRESSMATCH = '/address/match/get?'
    OPERATOR = '/operator/result?'
    MOJIEOPERATOR = '/operator/capricorn/result?'

    MOJIESOCIAL = '/v2/obtain/securityreport?' # 社保报告
    MOJIEFUND = "/v2/obtain/fundreport?" # 社保详情
    MOJIESOCIALORIGNAL = '/v2/obtain/securitydetail?' # 公积金报告
    MOJIEFUNDORIGNAL = "/v2/obtain/funddetail?" # 公积金详情
    MOJIEBANKREPORT = "/v2/obtain/peoplebankreport?" # 人行报告

    CELLPHONE = '/channel/idnamephonecheck?'
    UNDESIRABLE_INFO = '/channel/illegaldetailcheck?' # 公安不良信息
    YOULA_FACE = '/channel/idNameFase/post/'          # 优拉的人脸识别接口
    NET_LOAN_PLATFORMS = "/channel/netloanblacklist?" # 网贷逾期多平台
    NET_LOAN_RISK_CHECK = "/channel/riskinfocheck?"   # 网贷风险校验
    TAOBAO_INFO = "/operator/tbResult/capcha?" # 淘宝授权

    BLACKLIST_CHECK = "/channel/blacklistverify?"
    NEW_IDCARD_VERIFY = "/channel/personverify?"   # 新的身份证认证接口
    XIAOSHI_ONLINE = "/channel/phoneonlinetime?"   # 小视在网时长
    USERCONTACT_INFO = "/credit/relaterecord/get?" # 用户关联信息
    USERQUERYED_INFO = "/credit/queryrecord/get?"  # 用户个人信息查询

    OBTAIN_RISKINFOCHECK = '/v2/obtain/riskinfocheck?'   # 不良信息查询W1
    OPERATOR_PHONETIME = '/v2/operator/phonetime?'       # 手机号在网时长W1
    OPERATOR_MULTIPLATFORM = '/operator/Multiplatform?'  # 多平台借贷W1

    OBTAIN_LOANINTEGRATION = "/v2/obtain/loanintegration?"       # 信贷整合查询W1
    OBTAIN_LOANRISKINQUIRY = "/v2/obtain/loanriskinquiry?"       # 借款人风险查询W1
    OBTAIN_PICCOMPARE = "/v2/obtain/piccompare?"                 # 人像相似度对比验证W1


class CreditAuth:

    MODULE_DICT = {
        'telBatch': ['tel_batch'],
        'portraitActive': ['portait_active'],
        'creditTelRiskList': ['credit_telrisklist'],
        'creditManyPlatCheck': ['credit_manyplatcheck', 'operator_multiplatform'],
        'creditPhoneBlack': ['credit_phoneblack'],
        'creditPhoneDeviceCheck': ['credit_phonedevicecheck'],
        'creditNewsPlatRisk': ['credit_newsplatrisk'],
        'creditPhoneMsgCheck': ['credit_phonemsgcheck'],
        'creditSocialBlackList': ['credit_socialblacklist'],
        'idcard': ['mashang_idcard', 'channel_idcard'],
        'channelBankby3': ['channel_name_card_account', 'channel_bankby3'],
        'creditNetBlackList': ['credit_netblacklist'],
        'creditPerson': ['credit_person'],
        'addressGetByMobile': ['address_getbymobile'],
        'firmInfo': ['firm_info'],
        'shixin': ['credit_shixin', 'mashang_shixin'],
        'firmCourt': ['firm_court'],
        'firmJudgment': ['firm_judgment'],
        'firmZhixing': ['firm_zhixing'],
        'mashangNegative': ['mashang_negative'],
        'mashangScore': ['mashang_score'],
        'mashangOverdue': ['mashang_overdue'],
        'online': ['mashang_online', 'operator_phonetime'],
        'mashangCredit': ['mashang_credit'],
        'mashangFace': ['mashang_face', 'youla_face', "obtain_piccompare"],
        'operator': ['operator_black'],
        'phone_auth': ['mashang_phone'],   # 马上数据的 手机实名认证

        "multiPlatformloanOverTime": ['net_loan_overdue_platforms'],
        "internetLoanRisk": ['net_loan_risk_check'],
        "blackList": ["blacklist_check_query"],
        "userContactInfo": ["user_contact_info", ],
        "userQueryedInfo": ["user_queryed_info", ],
        'policeBadInfo': ['obtain_riskinfocheck', 'undesirable_info'],
        "overdueB": ["obtain_loanintegration"],
        "multipleLoanApplyA": ["obtain_loanintegration"],
        "multipleLoanRegisterB": ["obtain_loanintegration"],
        "overdueC": ["obtain_loanriskinquiry"],
        "multipleLoanApplyB": ["obtain_loanriskinquiry"],
        "financialBad": ["obtain_loanriskinquiry"],
    }

    # 方法对应的字段
    FUN_FIELD = {
        'address_getbymobile': ["addressInfo"],
        "credit_person": ["no_faith_list"],
        "mashang_shixin": ["horse_shixin"],
        'credit_telrisklist': ["e_business_danger"],
        'credit_manyplatcheck': ['multiple_loan'],
        'credit_phoneblack': ['phone_mark_blaklist'],
        'credit_phonedevicecheck': ['phone_verify'],
        'credit_newsplatrisk': ['info_dangers'],
        'credit_phonemsgcheck': ['phone_relatives'],
        'credit_socialblacklist': ['social_dangers'],
        'mashang_idcard': ['mashang_idcard'],
        'channel_idcard': ["channel_idcard_data"],
        'channel_bankby3': ["channel_bankby3"],
        'credit_netblacklist': ["loan_over_time_blacklist"],
        'mashang_negative': ["third_negative_info"],
        'mashang_overdue': ['third_over_time'],
        'mashang_online': ['online_time', 'third_is_phone'],
        'mashang_score': ['third_score'],
        'mashang_face': ['third_face_score'],
        'youla_face': ['youla_face_score'],
        'mashang_credit': ['third_anti_fraud'],
        'channel_name_card_account': ['name_idcard_account_data'],
        "net_loan_overdue_platforms": ["channel_netloanblacklist"],
        "net_loan_risk_check": ["channel_riskinfocheck"],
        "blacklist_check_query": ["blacklist_check"],
        "user_contact_info": ["user_contact_info_data", ],
        "user_queryed_info": ["user_queryed_info_data", ],
        'undesirable_info': ['undesirable_info'],
        'operator_phonetime': ['operator_phonetime_data'],
        'obtain_riskinfocheck': ['obtain_riskinfocheck_data'],
        'operator_multiplatform': ['operator_multiplatform_data'],
        "obtain_loanintegration": ["overdue_b", "multiple_loan_apply_a", "multiple_loan_register_b"],
        "obtain_loanriskinquiry": ["overdue_c", "multiple_loan_apply_b", "financial_bad"],
        "obtain_piccompare": ["obtain_piccompare"],
    }

    # 字段对应的返回字段
    FIELD_RESP = {
        'no_faith_list': 'noFaithList',
        'mashang_idcard': "isId",
        'channel_idcard_data': "isId",
        'channel_bankby3': 'isBankNum',
        'name_idcard_account_data': 'isBankNum',
        'addressInfo': 'addressInfo',
        'e_business_danger': 'eBusinessDanger',
        'info_dangers': 'infoDanger',
        'loan_over_time_blacklist': 'loanOverTimeBlackList',
        'multiple_loan': 'multipleLoan',
        'phone_mark_blaklist': 'phoneMarkBlackList',
        'phone_relatives': 'phoneRelative',
        'phone_verify': 'phoneVertify',
        'social_dangers': 'socialDanger',
        'online_time': 'onLineTime',
        'third_anti_fraud': 'thirdAntiFraud',
        'third_negative_info': 'thirdNegativeInfo',
        'third_over_time': 'thirdOverTime',
        'third_is_phone': 'isPhone',
        'third_score': 'score',
        'third_face_score': 'faceScore',
        "youla_face_score": 'faceScore',

        "channel_netloanblacklist": "multiPlatformloanOverTime",
        "channel_riskinfocheck": "internetLoanRisk",
        "blacklist_check": "blackList",
        "user_contact_info_data": "userContactInfo",  # 用户被关联信息
        "user_queryed_info_data": "userQueryedInfo",  # 用户被查询信息
        'undesirable_info': 'policeBadInfo',
        'operator_phonetime_data': 'onLineTime',
        'obtain_riskinfocheck_data': 'policeBadInfo',
        'operator_multiplatform_data': 'multipleLoan',
        "overdue_b": "overdueB",
        "multiple_loan_apply_a": "multipleLoanApplyA",
        "multiple_loan_register_b": "multipleLoanRegisterB",
        "overdue_c": "overdueC",
        "multiple_loan_apply_b": "multipleLoanApplyB",
        "financial_bad": "financialBad",
        "obtain_piccompare": "faceScore",
    }


class TelPrice:

    CODE = 1200
    # 全网平均价格
    DATA_DICT = {
        "模玩/动漫/周边/cos/桌游" : "59.5116379198",
        "保险" : "0.1",
        "笔记本电脑" : "3341.46401381",
        "大家电" : "1232.19272283",
        "珠宝/钻石/翡翠/黄金" : "567.400809617",
        "女士内衣/男士内衣/家居服" : "53.3319668618",
        "隐形眼镜/护理液" : "45.6991533004",
        "其他" : "166.26359163",
        "OTC药品/医疗器械/计生用品" : "84.9867914472",
        "品牌台机/品牌一体机/服务器" : "2368.5691933",
        "农机/农具/农膜" : "34.2754957309",
        "全屋定制" : "329.935364563",
        "饰品/流行首饰/时尚饰品新" : "31.7682549038",
        "电子词典/电纸书/文化用品" : "20.0896341569",
        "家庭保健" : "152.930939676",
        "房产/租房/新房/二手房/委托服务" : "184.663313953",
        "个人护理/保健/按摩器材" : "158.275232607",
        "零食/坚果/特产" : "24.0976749383",
        "洗护清洁剂/卫生巾/纸/香薰" : "38.1056084039",
        "度假线路/签证送关/旅游服务" : "351.540917594",
        "国货精品数码" : "497.640841329",
        "DIY电脑" : "2138.17612246",
        "咖啡/麦片/冲饮" : "45.4838983587",
        "保险分销" : "348.538571429",
        "自行车/骑行装备/零配件" : "104.860961045",
        "天猫点券" : "404.0",
        "童鞋/婴儿鞋/亲子鞋" : "72.7501651593",
        "商业/办公家具" : "151.812070942",
        "购物提货券/蛋糕面包" : "200.442272689",
        "淘女郎" : "82.1135371179",
        "保险（汇金收费）" : "127.923076923",
        "餐饮美食" : "110.005665574",
        "零售O2O" : "63.7625",
        "智能设备" : "318.812794523",
        "移动/联通/电信充值中心" : "68.6967633121",
        "运动包/户外包/配件" : "67.2130907348",
        "教育培训" : "127.511428645",
        "生活电器" : "325.814335297",
        "运动/瑜伽/健身/球迷用品" : "113.901776521",
        "资产" : "43.741382668",
        "自用闲置转让" : "106.63245262",
        "农用物资" : "14.2714149164",
        "餐饮具" : "49.5998279612",
        "个性定制/设计服务/DIY" : "23.4846774367",
        "电脑硬件/显示器/电脑周边" : "206.812834388",
        "数码相机/单反相机/摄像机" : "2557.8916228",
        "女装/女士精品" : "131.118614131",
        "玩具/童车/益智/积木/模型" : "57.5009146529",
        "汽车/用品/配件/改装" : "136.514063165",
        "家装主材" : "162.386498975",
        "电玩/配件/游戏/攻略" : "172.684078044",
        "居家日用" : "32.4614315048",
        "古董/邮币/字画/收藏" : "57.9661687107",
        "ZIPPO/瑞士军刀/眼镜" : "96.7258618816",
        "宠物/宠物食品及用品" : "39.6180798509",
        "书籍/杂志/报纸" : "33.1950941096",
        "男装" : "145.430763121",
        "奶粉/辅食/营养品/零食" : "119.323797007",
        "音乐/影视/明星/音像" : "60.2031928132",
        "平板电脑/MID" : "1370.14923533",
        "景点门票/实景演出/主题乐园" : "124.478041599",
        "腾讯QQ专区" : "60.3749521511",
        "网络游戏点卡" : "95.4622080617",
        "室内设计师" : "72.8181818182",
        "户外/登山/野营/旅行用品" : "93.5644198393",
        "农业生产资料（农村淘宝专用）" : "25.9440060698",
        "交通票" : "57.2412334802",
        "传统滋补营养品" : "81.5275481349",
        "服务商品" : "473.076923077",
        "网络设备/网络相关" : "136.455004771",
        "外卖/外送/订餐服务（垂直市场）" : "12.2443575893",
        "摩托车/装备/配件" : "135.61103418",
        "超市卡/商场购物卡" : "501.172273324",
        "住宅家具" : "799.80207147",
        "童装/婴儿装/亲子装" : "51.8679716959",
        "床上用品" : "148.453395256",
        "粮油米面/南北干货/调味品" : "22.9759139314",
        "休闲娱乐" : "59.0297934255",
        "流行男鞋" : "152.952189892",
        "厨房电器" : "328.048187865",
        "运动鞋new" : "277.002614356",
        "国内机票/国际机票/增值服务" : "83.0091402472",
        "成人用品/避孕/计生用品" : "56.6889576608",
        "合作商家" : "22.1433035714",
        "茶" : "81.0551704987",
        "婚庆/摄影/摄像服务" : "2464.37449481",
        "公益" : "21.0623821693",
        "司法拍卖拍品专用" : "1.0",
        "居家布艺" : "24.4674937181",
        "保健食品/膳食营养补充食品" : "165.259435003",
        "办公设备/耗材/相关服务" : "178.54865171",
        "鲜花速递/花卉仿真/绿植园艺" : "16.6597918262",
        "俪人购(俪人购专用)" : "271.426424245",
        "电动车/配件/交通工具" : "242.901649466",
        "特色手工艺" : "54.8159769174",
        "网游装备/游戏币/帐号/代练" : "38.0565275069",
        "网络店铺代金/优惠券" : "181.885945239",
        "闪存卡/U盘/存储/移动硬盘" : "86.9311505027",
        "基础建材" : "48.5459659414",
        "电子/电工" : "65.9259668527",
        "水产肉类/新鲜蔬果/熟食" : "60.1230684218",
        "节庆用品/礼品" : "15.0321454738",
        "游戏物品交易平台" : "79.4770545496",
        "五金/工具" : "64.9751527142",
        "收纳整理" : "22.8467607895",
        "手机号码/套餐/增值业务" : "49.7189457988",
        "手表" : "308.790710286",
        "手机" : "1052.21486826",
        "服饰配件/皮带/帽子/围巾" : "46.1129711925",
        "淘商号" : "109.78440367",
        "众筹" : "89.120164795",
        "MP3/MP4/iPod/录音笔" : "303.623611253",
        "酒类" : "175.533896992",
        "影音电器" : "201.321865528",
        "特价酒店/特色客栈/公寓旅馆" : "599.569685306",
        "电影/演出/体育赛事" : "67.651241625",
        "本地化生活服务" : "117.921677628",
        "整车(经销商)" : "6620.31210191",
        "畜牧/养殖物资" : "49.3207272822",
        "乐器/吉他/钢琴/配件" : "350.060920038",
        "运动服/休闲服装" : "143.187514821",
        "厨房/烹饪用具" : "37.8120076987",
        "家庭/个人清洁工具" : "22.0871223147",
        "TP服务商大类" : "1.11111111111",
        "孕妇装/孕产妇用品/营养" : "82.2255536019",
        "女鞋" : "128.818566903",
        "箱包皮具/热销女包/男包" : "132.782375659",
        "外卖/外送/订餐(请勿发布)" : "85.0700610854",
        "新车/二手车" : "618.942533308",
        "家居饰品" : "45.491259945",
        "网店/网络服务/软件" : "96.6860936057",
        "尿片/洗护/喂哺/推车床" : "80.104183208",
        "彩妆/香水/美妆工具" : "41.1361959663",
        "3C数码配件" : "30.5767322464",
        "数字娱乐" : "5.81101728991",
        "装修设计/施工/监理" : "187.933657489",
        "全球购代购市场" : "287.150967968",
        "美容护肤/美体/精油" : "87.7391876074",
        "美发护发/假发" : "60.3193176395",
        "处方药" : "25.3181818182",
    }


class SwitchType(object):
    """开关"""

    CONTRACT = 1        # 上上签合同

    MAPPING = {
        CONTRACT: 'contract',
    }


class ApplyType(object):
    """进件类型"""

    TEST = 1        # 测试进件
    OFFICIAL = 2    # 正式进件


class ServiceType(object):
    """短信模板类型"""

    VALIDATE = 1    # 验证码

    SIGN = 2        # 签合同


class FieldType(object):
    """
    字段类型
    其实风控不需要
    """

    TEXT = 1
    RADIO = 2
    CHECKBOX = 3
    CODE = 4
    ADDRESS = 5
    SELECT = 6
    DATE = 7
    IMAGE = 8

    MAPPING = {
        TEXT: 'text',
        RADIO: 'radio',
        CHECKBOX: 'checkbox',
        CODE: 'code',
        ADDRESS: 'address',
        SELECT: 'select',
        DATE: 'date'
    }


class RiskEvaluation:
    """贷前风险评估的结果模板"""

    O = 0  # 没有填
    N = 1   # 没数据
    S = 2   # 低
    M = 3   # 关注
    L = 4   # 高
    XL = 5  # 极高

    SEARCHING = '运营商数据查询中,请稍候...'

    ID_VERIFY = {
        O: '未查询',
        N: '未命中',
        S: '身份认证一致',
        M: '手机号与姓名验证不一致。此客户身份信息涉嫌虚假，涉及欺诈风险',
        XL: '身份证与姓名不匹配。此客户身份信息涉嫌虚假，涉及欺诈风险',
    }

    NOFAITH_VERIFY = {
        O: '未查询',
        S: '未命中',
        'a': '命中失信被执行，有欺诈风险',
        'b': '命中负面信息，有欺诈风险',
        'c': '命中公安不良信息，有欺诈风险',
        'd': '命中黑名单，有欺诈风险',
        "f": "命中金融不良信息黑名单，有欺诈风险",
    }

    OVERDUE_VERIFY = {
        O: '未查询',
        S: '未命中',
        'a': '逾期{0}天，当逾期超过60天时，违约风险极高',
        'b': '逾期{0}天，当逾期大于30天时，违约风险高',
        'c': '逾期{0}天，当逾期小于30天时，有违约风险',
        'd': '当前逾期，有违约风险',
        'f': '历史逾期，有违约风险',
        'e': '命中网贷逾期黑名单，违约风险高',
        'g': '命中网贷风险校验黑名单，违约风险高',
    }

    MULTI_VERIFY = {
        O: '未查询',
        S: '未命中',
        "a": "在{0}个借贷平台有注册，存在多头借贷风险",
        "b": "在{0}个借贷平台有注册",
        "c": "在{0}个金融平台有借贷申请记录",
    }

    THIRD_RISK = {
        O: '未查询',
        S: '借款人及重要联系人未命中互联网平台高危风险项，套现或欺诈风险低',
        'a': '{0}手机号互联网平台命中风险关键词，套现或欺诈风险较高',
        'b': '{0}手机号互联网平台命中风险关键词，套现或欺诈风险较高',
        'c': '{0}手机号互联网平台命中风险关键词，套现或欺诈风险较高',
    }

    ADDRESS_MATCH = {
        O: '未填写居住及单位地址信息',
        N: '无第三方地址信息',
        S: "家庭或单位地址与第三方收货地址校验一致",
        L: '居住及单位地址与三方信息校验不一致，住址信息存在虚假嫌疑，违约风险较高',
    }

    DEFAULT_RISK = {
        N: '未进行运营商授权，无法判断',
        S: '与重要联系人通话、近1个月异地通话、夜间通话占比正常，无疑似催收号码',
        'a': '{0}近3个月无联系，违约风险较高',
        'b': '{0}近3个月联系{1}次，联系过于频繁，超过正常值范围',
        'c': '近1个月异地通话时间占比{0}%，异地通话占比过高，存在违约风险',
        'd': '近1个月异地通话时间占比{0}%，超过正常值范围',
        'e': '近3个月与{0}个疑似催收号码有联系，违约风险高',
        'f': '近3个月与{0}个疑似催收号码有联系，有违约风险',
        'g': '夜间通话占比{0:.2f}%，夜间通话频繁，欺诈风险较高',
        'h': '夜间通话占比{0:.2f}%，超过正常值范围',
    }

    LOAN_CONTRACT = {
        N: '未进行运营商授权，无法判断',
        S: '近1个月无主动呼叫贷款类号码',
        L: '近1个月主动呼叫贷款类号码{0}个，联系过于频繁，存在多头借贷风险',
        M: '近1个月主动呼叫贷款类号码{0}个，超过正常值范围',
    }

    LOST_VERIFY = {
        S: '手机号近六个月联系人、互通电话数量及使用时间正常',
    }


CacheFields = dict(
    search_result_view=[
        'thirdAntiFraud',
        'addressInfo',
        'infoDanger',
        'contactInfoCheck',
        'isBankNum',
        'isBreakRule',
        'blackList',
        'multiPlatformloanOverTime',
        'onLineTime',
        'internetLoanRisk',
        'phoneRelative',
        'phoneMarkBlackList',
        'isId',
        'basicInfo',
        'score',
        'verifyInfo',
        'noFaithList',
        'thirdNegativeInfo',
        'userQueryedInfo',
        'loanOverTimeBlackList',
        'thirdOverTime',
        'faceScore',
        'socialDanger',
        'isPhone',
        'userContactInfo',
        'policeBadInfo',
        'multipleLoan',
        'phoneVertify',
        'eBusinessDanger',
        "overdueB",
        "multipleLoanApplyA",
        "multipleLoanRegisterB",
        "overdueC",
        "multipleLoanApplyB",
        "financialBad",
    ],
    tel_consume_view = ['priceTrend', 'consumeTrend', 'priceCompare', 'consumeSituation', 'consumeTags', 'consumeGrade'],
    address_verify_view = ['chart', 'addressList'],
    operator_view = ['callAreaTop5', 'connTop5Analysis', 'riskNumTag', 'importantConnChart', 'callAnalysisData', 'importantConnAnalysis', 'phoneInfo', 'abnormalBehavior', 'connAreaTop5'],
    token_status_view = ['operatorStatus'],
    msg_record_view = ['msgDetail', 'total', 'totalRemark'],
    call_record_view = ['callDetail', 'total', 'totalRemark'],
)

