_config = {
	"name": "申请表名字",
	"status": 1,
	"modules":[
		{
			"name": "基本信息",
			"immutable": 1,
			"index": 1,
			"totalMustWrite": 4,
			"totalShow": 4,
			"pages": [
				{
					"modulars": [
						{
							"name": "基本信息",
							"key": "base_info",
							"totalShow": 6,
							"labels": [
								{
									"name": "姓名",
									"key": "name",
									"isShow": 1,
									"mustWrite": 1,
									"type": 1,
									"remarks": "系统默认必填项",
									"unchanged": 1,
									'field_index': 1
								},
								{
									"name": "手机号",
									"key": "phone",
									"isShow": 1,
									"mustWrite": 1,
									"type": 1,
									"remarks": "系统默认必填项",
									"unchanged": 1,
									'field_index': 2
								},
								{
									"name": "身份证号码",
									"key": "idcard",
									"isShow": 1,
									"mustWrite": 1,
									"type": 1,
									"remarks": "系统默认必填项",
									"unchanged": 1,
									'field_index': 3
								},
								{
									"name": "短信验证码",
									"key": "sms_code",
									"isShow": 1,
									"mustWrite": 1,
									"type": 4,
									"remarks": "",
									"unchanged": 0,
									'field_index': 4
								},
								{
									"name": "QQ号码",
									"key": "qq_num",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 5
								},
								{
									"name": "电子邮箱",
									"key": "email",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 6
								},
								{
									"name": "是否学生",
									"key": "is_student",
									"isShow": 0,
									"mustWrite": 0,
									"type": 2,
									"remarks": "用户为学生时不显示工作信息",
									"unchanged": 0,
									'field_index': 7
								},
								{
									"index": 0,
									"name": "获取进件GPS",
									"key": "location",
									"isShow": 1,
									"mustWrite": 1,
									"type": 2,
									"remarks": "",
									"unchanged": 0,
									'field_index': 8
								},
								{
									"name": "用户申请协议",
									"key": "application_protocol",
									"isShow": 1,
									"mustWrite": 1,
									"type": 3,
									"remarks": "系统默认必填项",
									"unchanged": 1,
									'field_index': 9
								}
							]
						}
					]
				}]
		},
		{
			"name": "借款信息",
			"immutable": 0,
			"index": 2,
			"totalMustWrite": 9,
			"totalShow": 2,
			"pages": [
				{
					"modulars": [
						{
							"name": "借款信息",
							"key": "loan_info",
							"totalShow": 9,
							"labels": [
								{
									"name": "商品类别",
									"key": "product_type",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 1
								},
								{
									"name": "商品名称",
									"key": "product_name",
									"isShow": 1,
									"mustWrite": 1,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 2
								},
								{
									"name": "商品总价",
									"key": "product_money",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 3
								},
								{
									"name": "借款金额",
									"key": "loan_money",
									"isShow": 1,
									"mustWrite": 1,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 4
								},
								{
									"name": "手机品牌",
									"key": "shoujipinpai",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 5
								},
								{
									"name": "手机型号",
									"key": "shoujixinghao",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 6
								},
								{
									"name": "手机内存",
									"key": "shoujineicun",
									"isShow": 1,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 7
								},
								{
									"name": "分期期数",
									"key": "instalments",
									"isShow": 1,
									"mustWrite": 1,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 8
								},
								{
									"name": "借款用途",
									"key": "loan_use",
									"isShow": 0,
									"mustWrite": 0,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 9
								},
								{
									"name": "月还款金额",
									"key": "each_month_repay",
									"isShow": 1,
									"mustWrite": 1,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 10
								},
								{
									"name": "本人银行卡号",
									"key": "bank_num",
									"isShow": 1,
									"mustWrite": 1,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 11
								},
								{
									"name": "账户名",
									"key": "account",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 12
								},
								{
									"name": "银行预留手机号",
									"key": "bank_with_phone",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 13
								},
								{
									"index": 0,
									"name": "银行卡代扣授权",
									"key": "bank_auth",
									"isShow": 1,
									"mustWrite": 1,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 14
								}
							]
						}
					]
				}]
		},
		{
			"name": "综合信息",
			"immutable": 0,
			"index": 3,
			"totalShow": 19,
			"totalMustWrite": 19,
			"pages": [
				{
					"modulars": [
						{
							"name": "家庭及居住情况",
							"key": "home_info",
							"totalShow":6 ,
							"labels": [
								{
									"name": "婚姻状况",
									"key": "home_marriage",
									"isShow": 1,
									"mustWrite": 1,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 1
								},
								{
									"name": "户口所在地",
									"key": "registered_residence",
									"isShow": 1,
									"mustWrite": 1,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 2
								},
								{
									"name": "供养人数",
									"key": "home_num_support",
									"isShow": 0,
									"mustWrite": 0,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 3
								},
								{
									"name": "住房类型",
									"key": "home_house_type",
									"isShow": 1,
									"mustWrite": 1,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 4
								},
								{
									"name": "现居住时间",
									"key": "home_live_time",
									"isShow": 0,
									"mustWrite": 0,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 5
								},
								{
									"name": "现居住地址",
									"key": "home_live_address",
									"isShow": 1,
									"mustWrite": 1,
									"type": 5,
									"remarks": "",
									"unchanged": 0,
									'field_index': 6
								},
								{
									"name": "详细地址",
									"key": "home_detail_address",
									"isShow": 1,
									"mustWrite": 1,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 7
								},

							]
						},
						{
							"name": "联系人信息",
							"key": "contacts_info",
							"totalShow":6 ,
							"labels": [
								{
									"name": "家庭成员姓名",
									"key": "home_mem_name",
									"isShow": 1,
									"mustWrite": 1,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 1
								},
								{
									"name": "与申请人关系",
									"key": "home_mem_relation",
									"isShow": 1,
									"mustWrite": 1,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 2
								},
								{
									"name": "联系人电话",
									"key": "home_mem_phone",
									"isShow": 1,
									"mustWrite": 1,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 3
								},
								{
									"name": "联系人身份证号码",
									"key": "contacts_idcard",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 4
								},
								{
									"name": "联系人学历",
									"key": "contacts_school_record",
									"isShow": 0,
									"mustWrite": 0,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 5
								},
								{
									"name": "联系人工作单位",
									"key": "contacts_work_unit",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 6
								},
								{
									"name": "联系人职位",
									"key": "contacts_position",
									"isShow": 0,
									"mustWrite": 0,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 7
								},
								{
									"name": "联系人年收入",
									"key": "contacts_year_income",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 8
								},
								{
									"name": "联系人其他收入",
									"key": "contacts_others_income",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 9
								},
							]
						},
						{
							"name": "工作及收入信息",
							"key": "work_info",
							"totalShow": 6,
							"labels": [
								{
									"name": "工作单位名称",
									"key": "work_company_name",
									"isShow": 1,
									"mustWrite": 1,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 1
								},
								{
									"name": "职位",
									"key": "work_position",
									"isShow": 0,
									"mustWrite": 0,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 2
								},
								{
									"name": "年收入",
									"key": "work_year_income",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 3
								},
								{
									"name": "其他收入",
									"key": "others_earn",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 4
								},
								{
									"name": "工作年限",
									"key": "work_year",
									"isShow": 0,
									"mustWrite": 0,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 5
								},
								{
									"name": "现单位工作年限",
									"key": "work_year_unit",
									"isShow": 0,
									"mustWrite": 0,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 6
								},
								{
									"name": "所属行业",
									"key": "work_industry",
									"isShow": 0,
									"mustWrite": 0,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 7
								},
								{
									"name": "单位性质",
									"key": "work_nature",
									"isShow": 0,
									"mustWrite": 0,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 8
								},
								{
									"name": "单位规模",
									"key": "work_scale",
									"isShow": 0,
									"mustWrite": 0,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 9
								},
								{
									"name": "单位固话",
									"key": "unit_phone",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 10
								},
								{
									"name": "单位地址",
									"key": "work_address",
									"isShow": 1,
									"mustWrite": 1,
									"type": 5,
									"remarks": "",
									"unchanged": 0,
									'field_index': 11
								},
								{
									"name": "单位详细地址",
									"key": "work_detail_address",
									"isShow": 1,
									"mustWrite": 1,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index':12
								},
								{
									"name": "单位联系人姓名",
									"key": "work_contact_name",
									"isShow": 1,
									"mustWrite": 1,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 13
								},
								{
									"name": "与联系人关系",
									"key": "work_contact_relation",
									"isShow": 1,
									"mustWrite": 1,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 14
								},
								{
									"name": "单位联系人电话",
									"key": "work_contact_phone",
									"isShow": 1,
									"mustWrite": 1,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 15
								},

							]
						},
						{
							"name": "教育信息",
							"key": "education_info",
							"totalShow": 3,
							"labels": [
								{
									"name": "学校名称",
									"key": "school_name",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 1
								},
								{
									"name": "学历",
									"key": "school_education",
									"isShow": 0,
									"mustWrite": 0,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 2
								},
								{
									"name": "入学时间",
									"key": "school_start",
									"isShow": 0,
									"mustWrite": 0,
									"type": 7,
									"remarks": "",
									"unchanged": 0,
									'field_index': 3
								},
								{
									"name": "专业名称",
									"key": "school_major",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 4
								},
								{
									"name": "政治面貌",
									"key": "political_status",
									"isShow": 0,
									"mustWrite": 0,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 5
								},
								{
									"name": "学校联系人姓名",
									"key": "school_contact",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 6
								},
								{
									"name": "与联系人关系",
									"key": "school_contact_relation",
									"isShow": 0,
									"mustWrite": 0,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 7
								},
								{
									"name": "学校联系人电话",
									"key": "school_contact_phone",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 8
								}
							]
						},
						{
							"name": "资产及信贷情况",
							"key": "credit_info",
							"totalShow": 4,
							"labels": [
								{
									"name": "房产数量",
									"key": "houses_num",
									"isShow": 0,
									"mustWrite": 0,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 1
								},
								{
									"name": "小区名称",
									"key": "villageName",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 1,
									'field_index': 2
								},
								{
									"name": "房产价值",
									"key": "houseValue",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 1,
									'field_index': 3
								},
								{
									"name": "面积",
									"key": "houseArea",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 1,
									'field_index': 4
								},
								{
									"name": "房产地址",
									"key": "propertyAddress",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 1,
									'field_index': 5
								},
								{
									"name": "汽车数量",
									"key": "car_num",
									"isShow": 0,
									"mustWrite": 0,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 6
								},
								{
									"name": "汽车品牌",
									"key": "carBrand",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 1,
									'field_index': 7
								},
								{
									"name": "汽车车型",
									"key": "carType",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 1,
									'field_index': 8
								},
								{
									"name": "汽车价值",
									"key": "carValue",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 1,
									'field_index': 9
								},
								{
									"name": "购买时间",
									"key": "purchaseTime",
									"isShow": 0,
									"mustWrite": 0,
									"type": 7,
									"remarks": "",
									"unchanged": 1,
									'field_index': 10
								},
								{
									"name": "车牌号",
									"key": "plateNumber",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 1,
									'field_index': 11
								},
								{
									"name": "银行借款",
									"key": "bank_loan",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 12
								},
								{
									"name": "私人借款",
									"key": "private_loan",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 13
								},
								{
									"name": "其他负债",
									"key": "others_liabilities",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 14
								},
								{
									"name": "是否有信用卡",
									"key": "credit_crecard",
									"isShow": 0,
									"mustWrite": 0,
									"type": 2,
									"remarks": "",
									"unchanged": 0,
									'field_index': 15
								},
								{
									"name": "信用卡数量",
									"key": "credit_crecard_num",
									"isShow": 0,
									"mustWrite": 0,
									"type": 6,
									"remarks": "",
									"unchanged": 0,
									'field_index': 16
								},
								{
									"name": "最高额度",
									"key": "maximum_amount",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 17
								},
							]
						}
					]
				}
			]
		},
		{
			"name": "证件资料",
			"immutable": 0,
			"index": 4,
			"totalShow": 3,
			"pages": [
				{
					"modulars": [
						{
							"name": "上传资料",
							"key": "upload_info",
							"totalShow": 3,
							"labels": [
								{
									"name": "身份证正面",
									"key": "id_face",
									"isShow": 1,
									"mustWrite": 1,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 1
								},
								{
									"name": "身份证背面",
									"key": "id_back",
									"isShow": 1,
									"mustWrite": 1,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 2
								},
								{
									"name": "手持身份证现场照",
									"key": "photo_with_card",
									"isShow": 1,
									"mustWrite": 1,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 3
								},
								{
									"name": "学生证/学信网截图",
									"key": "student_phone",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 4
								},
								{
									"name": "芝麻信用截图",
									"key": "seasame_credit",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 5
								}
							]
						}
					]
				}
			]
		},
		{
			"name": "授权认证",
			"immutable": 0,
			"index": 5,
			"totalShow": 1,
			"totalMustWrite": 1,
			"pages": [
				{
					"modulars": [
						{
							"name": "运营商授权",
							"key": "cap_info_s_mod",
							"labels": [
								{
									"index": 0,
									"name": "运营商授权",
									"key": "is_capcha",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 1
								},
								{
									"index": 0,
									"name": "淘宝授权",
									"key": "isTaobao",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 2
								},
								{
									"index": 0,
									"name": "人行征信报告授权",
									"key": "is_renhangzhengxin",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 3
								},
								{
									"index": 0,
									"name": "社保授权",
									"key": "is_socialsecurity",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 4
								},
								{
									"index": 0,
									"name": "公积金授权",
									"key": "is_publicfunds",
									"isShow": 0,
									"mustWrite": 0,
									"type": 1,
									"remarks": "",
									"unchanged": 0,
									'field_index': 5
								},
                            ]
						}

					]
				}
			]
		}
	]

}
