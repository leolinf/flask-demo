from flask_restful import fields


class InputField:

    _basic = {
        "name": fields.String(attribute="name", default=""),
        "idNum": fields.String(attribute="ID_num", default=""),
        "phone": fields.String(attribute="phone", default=""),
        "email": fields.String(attribute="email", default=""),
        "qq": fields.String(attribute="qq", default=""),
        "isStudent": fields.Boolean(attribute="is_student", default=False)
    }

    _loan = {
        "accountName": fields.String(attribute="card_owner", default=""),
        "bankNum": fields.String(attribute="card_no", default=""),
        "ensurance": fields.Boolean(attribute="need_insurance", default=""),
        "instalments": fields.Integer(attribute="each_month_repay", default=-1),
        "loanMount": fields.Integer(attribute="loan_money", default=-1),
        "package": fields.Boolean(attribute="need_repay_package", default=""),
        "productCat": fields.String(attribute="category", default=""),
        "productName": fields.String(attribute="name", default=""),
        "stage": fields.String(attribute="cycle", default=""),
        "productPrice": fields.String(attribute="total_price", default=""),
    }

    _work = {
        "companyAdd": fields.String(attribute="company_addr", default=""),
        "companyCat": fields.String(attribute="nature", default=""),
        "companyContactName": fields.String(attribute="contacts_name", default=""),
        "companyContactPhone": fields.String(attribute="contacts_tel", default=""),
        "companyName": fields.String(attribute="company_name", default=""),
        "companySize": fields.String(attribute="scale", default=""),
        "position": fields.String(attribute="position", default=""),
        "salary": fields.Integer(attribute="income", default=-1),
        "trade": fields.String(attribute="industry", default=""),

        "province": fields.String(attribute="province", default=""),
        "city": fields.String(attribute="city", default=""),
        "district": fields.String(attribute="district", default=""),
    }

    _school = {
        "academy": fields.String(attribute="college", default=""),
        "admissionTime": fields.Integer(attribute="enter_time", default=-1),
        "contactName": fields.String(attribute="contacts_name", default=""),
        "contactPhone": fields.String(attribute="contacts_tel", default=""),
        "contactRelation": fields.String(attribute="relation", default=""),
        "major": fields.String(attribute="major", default=""),
        "school": fields.String(attribute="school", default=""),
    }

    _family = {
        "province": fields.String(attribute="province", default=""),
        "city": fields.String(attribute="city", default=""),
        "district": fields.String(attribute="district", default=""),

        "applerRealation": fields.String(attribute="mem_relation", default=""),
        "community": fields.String(attribute="community", default=""),
        "community_num": fields.String(attribute="community_num", default=""),
        "contactPhone": fields.String(attribute="mem_telephone", default=""),
        "familyAdd": fields.String(attribute="address", default=""),
        "familyName": fields.String(attribute="family_mem", default=""),
        "houseType": fields.String(attribute="house_type", default=""),
        "liveTime": fields.String(attribute="live_time", default=""),
        "marriage": fields.String(attribute="marriage", default=""),
        "mateName": fields.String(attribute="mate_name", default=""),
        "matePhone": fields.String(attribute="mate_tel", default=""),
    }
    PIC_DICT = {
        'ID_back': 'backId',
        'Sesame_Credit_screenshot': 'creditPic',
        'ID_face': 'frontId',
        'photo_with_ID': 'handId',
        'student_ID_img': 'studentPic',
        'bank_card': 'bankCard'
    }
    _pic = {
        "身份证背面照": fields.String(attribute="imgs__ID_back", default=''),
        "芝麻信用截图": fields.String(attribute="imgs__Sesame_Credit_screenshot", default=''),
        "身份证正面": fields.String(attribute="imgs__ID_face", default=''),
        "银行卡照片": fields.String(attribute="imgs__bank_card", default=''),
        "手持身份证现场照": fields.String(attribute="imgs__hand_with_ID", default=''),
        "学生证/学信网截图": fields.String(attribute="imgs__student_ID_img", default=''),
    }

    apply_label = {
        "order_num": fields.String(attribute="order_num", default=""),

        "basic": fields.Nested(_basic, attribute='basic_info'),
        "repayment": fields.Nested(_loan, attribute="loan_info"),
        "work": fields.Nested(_work, attribute="work_info"),
        "student": fields.Nested(_school, attribute="school_info"),
        "family": fields.Nested(_family, attribute="family_info"),
        "other": {
            "city": fields.String(default=""),
            "jobNum": fields.String(attribute="code", default=""),
            "organizationName": fields.String(attribute="beauty_organization", default="")
        }
    }

    excel_basic = {
        "姓名": fields.String(attribute="basic_info.name", default=""),
        "身份证号码": fields.String(attribute="basic_info.ID_num", default=""),
        "手机号": fields.String(attribute="basic_info.phone", default=""),
        "电子邮箱": fields.String(attribute="basic_info.email", default=""),
        "QQ号码": fields.String(attribute="basic_info.qq", default=""),
        "是否学生": fields.String(attribute="basic_info.is_student", default="")
    }

    excel_loan = {
        "账户名": fields.String(attribute="card_owner", default=""),
        "银行卡号": fields.String(attribute="card_no", default=""),
        "申请参加保险": fields.String(attribute="need_insurance", default=""),
        "月还款金额": fields.String(attribute="each_month_repay", default=""),
        "借款金额": fields.String(attribute="loan_money", default=""),
        "还款随心包": fields.String(attribute="need_repay_package", default=""),
        "产品类别": fields.String(attribute="category", default=""),
        "产品名称": fields.String(attribute="name", default=""),
        "分期数": fields.String(attribute="cycle", default=""),
        "产品总价": fields.String(attribute="total_price", default=""),
    }

    excel_work = {
        "单位详细地址": fields.String(attribute="company_addr", default=""),
        "单位性质": fields.String(attribute="nature", default=""),
        "单位联系人姓名": fields.String(attribute="contacts_name", default=""),
        "单位联系人电话": fields.String(attribute="contacts_tel", default=""),
        "工作单位名称": fields.String(attribute="company_name", default=""),
        "单位规模": fields.String(attribute="scale", default=""),
        "职位": fields.String(attribute="position", default=""),
        "月收入": fields.Integer(attribute="income", default=""),
        "所属行业": fields.String(attribute="industry", default=""),
        "单位所在省份": fields.String(attribute="province", default=""),
        "单位所在城市": fields.String(attribute="city", default=""),
        "单位所在区县": fields.String(attribute="district", default=""),
    }

    excel_school = {
        "学院名称": fields.String(attribute="college", default=""),
        "入学时间": fields.String(attribute="enter_time", default=-1),
        "学校联系人姓名": fields.String(attribute="contacts_name", default=""),
        "学校联系人电话": fields.String(attribute="contacts_tel", default=""),
        "与联系人关系": fields.String(attribute="relation", default=""),
        "专业名称": fields.String(attribute="major", default=""),
        "学校名称": fields.String(attribute="school", default=""),
    }

    excel_family = {
        "现居省份": fields.String(attribute="province", default=""),
        "现居城市": fields.String(attribute="city", default=""),
        "现居区县": fields.String(attribute="district", default=""),

        "与申请人关系": fields.String(attribute="mem_relation", default=""),
        "小区信息": fields.String(attribute="community", default=""),
        "community_num": fields.String(attribute="community_num", default=""),
        "联系电话": fields.String(attribute="mem_telephone", default=""),
        "现居地址": fields.String(attribute="address", default=""),
        "家庭成员姓名": fields.String(attribute="family_mem", default=""),
        "住房类型": fields.String(attribute="house_type", default=""),
        "现住址居住时间": fields.String(attribute="live_time", default=""),
        "婚姻状况": fields.String(attribute="marriage", default=""),
        "配偶姓名": fields.String(attribute="mate_name", default=""),
        "配偶联系电话": fields.String(attribute="mate_tel", default=""),
    }

