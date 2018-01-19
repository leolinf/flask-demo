# -*- coding: utf-8 -*-

import datetime
import random
from decimal import Decimal
import logging

from sqlalchemy import and_, or_

from app import Config
from app.core.utils import query_location, query_address
from app.core.functions import time_change
from app.core.functions import period2datetime, timestamp2datetime
from app.models import InputApply, SingleSearch, FakeScore, Merchant, MerchantGoods
from app.databases import session_scope
from app.constants import SearchStatus, ApproveStatus, RiskEvaluation, TelPrice, Code, FieldType, LocalState
from itertools import groupby
import json
from app.core.decorators import cache_riskevaluation
from app.core.logger import project_logger
from app.core.baidu import BaiduMap


def custom_max(old, new):

    if old == RiskEvaluation.O:
        return new
    if old == RiskEvaluation.N:
        if new == RiskEvaluation.O:
            return old
        else:
            return new

    return max(old, new)


class CreditManager(object):

    def __init__(self, session, *args, **kwargs):

        self.session = session

    def get_list(self, company_id, offset=0, limit=10, number=None, intoTimeSort=1, approveTimeSort=1,
                 intoPeriod=None, intoStartTime=None, intoEndTime=None, isBreakRule=None,
                 approvePeriod=None, approveStartTime=None, approveEndTime=None,
                 approveStatus=None, searchStatus=None, localState=None,
                 **kwargs):

        ##########
        # 筛选
        ##########
        match = (
            InputApply.company_id == company_id,
            or_(
                InputApply.local_state == 1,
                and_(
                    InputApply.local_state == 2,
                    InputApply.search_status != SearchStatus.NO,
                ),
            ),
        )

        # 筛选手机号或身份证
        if number:
            match += (or_(
                InputApply.phone.like('%{0}%'.format(number)),
                InputApply.idcard.like('%{0}%'.format(number)),
                InputApply.id.like('%{0}%'.format(number)),
                InputApply.name.like('%{0}%'.format(number)),
            ),)
        # 筛选进件时间
        if intoPeriod and intoPeriod != 'all':
            start, end = period2datetime(intoPeriod)
            match += (InputApply.apply_time > start, InputApply.apply_time < end)
        elif intoStartTime and intoEndTime:
            start = timestamp2datetime(intoStartTime)
            end = timestamp2datetime(intoEndTime)
            match += (InputApply.apply_time > start, InputApply.apply_time < end)

        # 筛选审核时间
        if approvePeriod and approvePeriod != 'all':
            start, end = period2datetime(approvePeriod)
            match += (InputApply.approve_time > start, InputApply.approve_time < end)
        elif approveStartTime and approveEndTime:
            start = timestamp2datetime(approveStartTime)
            end = timestamp2datetime(approveEndTime)
            match += (InputApply.approve_time > start, InputApply.approve_time < end)

        # 违反规则
        if isBreakRule == 1:
            match += (InputApply.is_break_rule == 1,)
        elif isBreakRule == 0:
            match += (InputApply.is_break_rule == 0,)

        # 审批状态
        if approveStatus == ApproveStatus.WAITING:
            match += (
                and_(
                    or_(
                        InputApply.approve_status == ApproveStatus.WAITING,
                        InputApply.approve_status == None
                    ),
                    InputApply.search_status == SearchStatus.DONE,
                    InputApply.local_state == LocalState.MOBILE,
                ),
            )
        elif approveStatus and approveStatus != 0:
            match += (
                InputApply.approve_status == approveStatus,
            )

        # 查询状态
        if searchStatus == SearchStatus.DOING:
            match += (
                InputApply.search_status == searchStatus,
            )
        elif searchStatus == SearchStatus.NO:
            match += (
                or_(
                    InputApply.search_status == searchStatus,
                    InputApply.search_status == None,
                ),
            )

        elif searchStatus == SearchStatus.ADD_TO_MONITOR:
            match += (
                InputApply.monitor_id != None,
            )
        elif searchStatus == SearchStatus.DONE:
            match += (
                InputApply.search_status == SearchStatus.DONE,
                InputApply.monitor_id == None,
            )

        if localState:
            match += (
                InputApply.local_state == localState,
            )

        ##########
        # 排序
        ##########
        order = (
        )

        if intoTimeSort == 1:
            order += (InputApply.apply_time,)
        elif intoTimeSort == 2:
            order += (InputApply.apply_time.desc(),)
        elif approveTimeSort == 1:
            order += (InputApply.approve_time, InputApply.apply_time.desc())
        elif approveTimeSort == 2:
            order += (InputApply.approve_time.desc(), InputApply.apply_time.desc())
        else:
            order = (InputApply.apply_time.desc(),)

        credits = self.session.query(InputApply).filter(and_(*match)).order_by(*order)
        total = credits.count()
        credits = credits.offset(offset).limit(limit).all()

        def _detail(credit):

            if credit.search_status == SearchStatus.DONE:
                approve_status = credit.approve_status if credit.approve_status else ApproveStatus.WAITING
                if credit.operator != 1:
                    is_break = int(credit.is_break_rule) if credit.is_break_rule else 0
                else:
                    is_break = -1
            else:
                approve_status = -1
                is_break = -1

            if credit.local_state == LocalState.WEB:
                approve_status = -1

            score = int(credit.score) if credit.score and credit.score.isdigit() else -1

            if credit.search_status == SearchStatus.DONE and credit.monitor_id:
                search_status = SearchStatus.ADD_TO_MONITOR
            else:
                search_status = credit.search_status if credit.search_status else SearchStatus.NO

            res = {
                'id': str(credit.id),
                'number': credit.id,
                'phone': credit.phone,
                'intoNumber': str(credit.id),
                'intoTime': credit.apply_time,
                'name': credit.name,
                'idCard': credit.idcard,
                'searchStatus': search_status,
                'approveStatus': approve_status,
                'approveTime': credit.approve_time if credit.approve_time else -1,
                'score': score,
                'isBreak': is_break,
                'isAddMonitor': bool(credit.monitor_id),
                'loanId': str(credit.monitor_id),
                'localState': credit.local_state,
                "merchantName": credit.merchant.name if credit.merchant and credit.local_state == LocalState.MOBILE else "--",
            }
            return res

        return list(map(_detail, credits)), total

    def gen_credit_id(self, company_id):

        today = datetime.date.today()
        timestamp = int(today.strftime('%Y%m%d'))

        count = self.session.query(InputApply).filter(
            and_(
                InputApply.company_id == company_id,
                InputApply.create_time >= today
            )
        ).count()
        return timestamp * 10 ** 9 + company_id * 10 ** 6 + count + 1

    def create_credit(self, company_id, apply_number, phone):

        credit_id = self.gen_credit_id(company_id)

        with session_scope(self.session) as session:
            credit = InputApply(id=credit_id, apply_number=apply_number, phone=phone, company_id=company_id)
            session.add(credit)

    def get_address(self, search_id):

        search = SingleSearch.objects(apply_number=search_id).first()
        input_apply = self.session.query(InputApply).get(search_id)

        if not search or not input_apply:
            return 'not exist'
        try:
            work_addr = json.loads(input_apply.work_address)
            work_addr_join = ''.join(work_addr)
        except:
            work_addr_join = ''

        work_address = '{0}{1}'.format(
            work_addr_join,
            input_apply.work_detail_address if input_apply.work_detail_address else ''
        )
        try:
            home_addr = json.loads(input_apply.home_live_address)
            home_addr_join = ''.join(home_addr)
        except:
            home_addr_join = ''

        home_address = '{0}{1}'.format(
            home_addr_join,
            input_apply.home_detail_address if input_apply.home_detail_address else ''
        )
        try:
            merchant_address = json.loads(input_apply.merchant_info).get('address', '')
        except:
            merchant_address = input_apply.merchant.address
        result = search.operator_data.get('callback_operator', {})
        if not result or result.get('code') != 31000:
            result = {}
        phone_address = result.get('data', {}).get('baseInfo', {}).get('phoneBelongArea', '')
        taobao = search.taobao_data
        if taobao and isinstance(taobao, dict) and taobao.get("code") != 41000:
            tel_address = ""
        else:
            from app.credit.taobao import handler_data
            resp = handler_data(taobao.get("data", {}) or {}, search.name, search.phone)
            address = resp["address"]
            if address:
                addr = address[0]
                tel_address = "".join((addr["province"], addr["city"], addr["area"], addr["addressDetail"]))
            else:
                tel_address = ""

        try:
            gps_location = json.loads(input_apply.location)
            gps_coordinates = "{0},{1}".format(gps_location["longitude"], gps_location["latitude"])
        except:
            gps_coordinates = ""

        baidu = BaiduMap(Config.BAIDU_AK)

        if search.gps_address:
            gps_address = search.gps_address
        else:
            gps_address = query_address(gps_coordinates)

            SingleSearch.objects(apply_number=search_id).update(
                set__gps_address=gps_address
            )

        res = {
            'addressList': [
                {
                    'title': '工作单位地址',
                    'detailAddress': work_address if work_address else '未填写单位地址',
                },
                {
                    'title': '手机通话所在地',
                    'detailAddress': phone_address if phone_address else '未获取到手机通话所在地',
                },
                {
                    'title': '进件GPS地址',
                    'detailAddress': gps_address if gps_address else '未获取到进件GPS地址',
                },
            ],
            'chart': {
                'businessAddress': merchant_address,
                'liveAddress': home_address,
                'thirdAddress': tel_address,
                "applyAddress": gps_address,
                "workAddress": work_address,
            },
        }

        if any(v for v in search.location.values()):
            d = search.location
            res['chart'].update(search.location)
        else:
            # 去请求高德地图
            _map = {
                'businessCoordinates': merchant_address,
                'liveCoordinates': home_address,
                'thirdCoordinates': tel_address,
                "workCoordinates": work_address,
            }
            d = {}
            for key, value in _map.items():
                if not value:
                    d[key] = ''
                    continue
                # r = query_location(value)
                # 换成百度的
                r = baidu.convert_address_to_coordinate(value)
                d[key] = r

            d.update({
                "applyCoordinates": gps_coordinates,
            })

            SingleSearch.objects(apply_number=search_id).update(
                set__location=d
            )
            res['chart'].update(d)

        bc = baidu.convert_gps_to_utm(d["businessCoordinates"])
        lc = baidu.convert_gps_to_utm(d["liveCoordinates"])
        tc = baidu.convert_gps_to_utm(d["thirdCoordinates"])
        wc = baidu.convert_gps_to_utm(d["workCoordinates"])
        gc = baidu.convert_gps_to_utm(gps_coordinates)

        # if any(v for v in search.distance.values()):
        #     res['chart'].update(search.distance)
        # else:
        distance = {
            'bussiness2live': baidu.calculate_distance(bc, lc),
            'live2third': baidu.calculate_distance(lc, tc),
            "work2apply": baidu.calculate_distance(wc, gc),
            "third2work": baidu.calculate_distance(tc, wc),
            "live2work": baidu.calculate_distance(lc, wc),
            "apply2live": baidu.calculate_distance(gc, lc),
            "apply2bussiness": baidu.calculate_distance(gc, bc),
        }
        SingleSearch.objects(apply_number=search_id).update(
            set__distance=distance
        )
        res["chart"].update(distance)

        return res

    def save_address(self, search_id, distance):

        search = SingleSearch.objects(apply_number=search_id).first()
        input_apply = self.session.query(InputApply).get(search_id)

        if not search or not input_apply:
            return Code.SINGLE_NOT_EXIST

        if 'id' in distance:
            distance.pop('id')
        search.update(
            set__distance=distance,
        )
        from .forcache import cache_address_verify_view
        cache_address_verify_view(self.session, {'id': search_id})
        return Code.SUCCESS


class InputApplyManager(object):
    @classmethod
    def get_by_id(cls, session, input_id):
        return session.query(InputApply).filter_by(id=input_id).first()

def trans(d):
    b = [chr(i) for i in range(65,91)]
    l = ''
    for index, v in enumerate(d):
        if v in b:
            l = l + ('_' + v.lower())
        else:
            l = l + v
    return l


class InputShow(object):
    """ 根据快照表得到当时的进件字段信息， 然后根据这个字段信息去 展示进件信息  """

    @classmethod
    def trans_field(cls, d, key):
        if key == 'home_live_address' or key == 'work_address':
            try:
                return ''.join(json.loads(d))
            except:
                return d
        if key == 'instalments':
            if d == 0 or not d:
                return '--'

        if isinstance(d, bool):
            if d is True:
                return '是'
            else:
                return "否"
        if isinstance(d, datetime.datetime):
            return d.strftime("%Y-%m-%d")
        return d

    @classmethod
    def format_input_info(cls, session, format_src, input_obj, search):
        """ the format_src is a json object """
        result = []
        flag = False
        is_student = input_obj.is_student if isinstance(input_obj.is_student, bool) else False

        for key, each_mod in format_src.items():
            lists = []
            # 上传资料的基本图片信息，归纳到基本信息页面 和其他资料页面
            if key == 'upload_info':
                flag = True
                continue
            # 运营商模块页不进行显示
            if key == 'cap_info_s_mod':
                continue

            _map = {
                'villageName': '小区名称',
                'houseValue': '房产价值',
                'houseArea': '面积',
                'propertyAddress': '房产地址',
                'carBrand': '汽车品牌',
                'carType': '汽车车型',
                'carValue': '汽车价值',
                'purchaseTime': '购买时间',
                'plateNumber': '车牌号',
            }

            _order = {
                'villageName': 1,
                'houseValue': 2,
                'houseArea': 3,
                'propertyAddress': 4,
                'carBrand': 5,
                'carType': 6,
                'carValue': 7,
                'purchaseTime': 8,
                'plateNumber': 9
            }

            _map_phone = {
                "shoujipinpai": "手机品牌",
                "shoujixinghao": "手机型号",
                "shoujineicun": "手机内存",
            }

            for each_field in each_mod['lists']:
                if 'isExt' in each_field and each_field['isExt'] and each_field['isShow']:
                    ret = InputShow.ext_field(each_field['key'], input_obj.id, session)

                    lists.append({
                        'key': each_field['name'],
                        'value': ret,
                    })
                elif InputShow.is_add_to_show(each_field):
                    # in this version, it always run
                    if each_field['key'] == 'smsCode':
                        continue
                    # 是学生身份，但是却填写工作信息， 此时也不展示。
                    if is_student is True:
                        if each_field['key'].startswith("work") or each_field["key"] in ["othersEarn", "unitPhone"]:
                            continue
                    if each_field['key'] in ['houseValue', 'houseArea', 'propertyAddress', 'carType', 'carValue',
                                             'purchaseTime', 'plateNumber', "shoujixinghao", "shoujineicun"]:
                        continue

                    # 有银行卡授权的  要展示本人银行卡号  真是醉
                    if each_field["key"] == "bankAuth":
                        res = [{'key': "本人银行卡号", 'value': input_obj.bank_num},
                               {"key": "银行预留手机号", "value": input_obj.bank_with_phone}]
                        lists.extend(res)
                        continue

                    def _process(name, key):

                        def _gen_key(k, index, max):

                            if max > 1 and k in ['villageName', 'carBrand']:
                                return '{0}{1}'.format(_map[k], index + 1)

                            return _map[k]

                        def _gen_type(k, index, max):

                            if max > 1:
                                return '{0}{1}'.format(k, index + 1)

                            return k

                        if key == 'villageName':

                            house_message = cls.trans_field(getattr(input_obj, trans('houses_message')), trans('houses_message'))
                            try:
                                house_message = json.loads(house_message)
                            except:
                                house_message = []

                            length = len(house_message)

                            res = []

                            for j, i in enumerate(house_message):
                                r = []
                                for k, v in i.items():
                                    r.append({'key': _gen_key(k, j, length), 'value': v, 'type': _gen_type('house', j, length), 'extra': k})
                                r.sort(key=lambda x: _order[x['extra']])
                                res.extend(r)

                            return res

                        if key == 'carBrand':

                            car_message = cls.trans_field(getattr(input_obj, trans('car_message')), trans('car_message'))
                            try:
                                car_message = json.loads(car_message)
                            except:
                                car_message = []

                            length = len(car_message)

                            res = []

                            for j, i in enumerate(car_message):
                                r = []
                                for k, v in i.items():
                                    r.append({'key': _gen_key(k, j, length), 'value': v, 'type': _gen_type('car', j, length), 'extra': k})
                                r.sort(key=lambda x: _order[x['extra']])
                                res.extend(r)

                            return res

                        if key == 'housesNum':

                            return {'key': name, 'value': cls.trans_field(getattr(input_obj, trans(key)), trans(key)), 'type': 'houseNum'}

                        if key == 'carNum':

                            return {'key': name, 'value': cls.trans_field(getattr(input_obj, trans(key)), trans(key)), 'type': 'carNum'}

                        if key == "location":
                            return {"key": name, "value": search.gps_address if search else ""}

                        if key == "shoujipinpai":
                            merchant_goods = session.query(MerchantGoods).filter(MerchantGoods.id ==
                                                                                 input_obj.interest_id).one_or_none()
                            if not merchant_goods:
                                return

                            try:
                                describes = json.loads(merchant_goods.describes)
                            except Exception:
                                logging.error("保存的describes是\t{0}".format(merchant_goods.describes))
                                return

                            return [{"key": _map_phone.get(k, "-"), "value": v} for k, v in describes.items()]

                        return {'key': name, 'value': cls.trans_field(getattr(input_obj, trans(key)), trans(key))}

                    processed = _process(each_field['name'], each_field['key'])

                    if isinstance(processed, list):
                        lists.extend(processed)
                    elif processed:
                        lists.append(processed)

            images = []
            if key == 'base_info':
                InputShow.img_handler(images, session, input_obj)
            # 处理额外添加的图片
            result.append({
                "moduleName": each_mod['name'],
                "lists": lists.copy(),
                'images': images
            })
        InputShow.other_info(result, input_obj)
        # other photo
        if flag is True:
            InputShow.handle_other_photo(result, input_obj, session)
        return result

    @classmethod
    def other_info(cls, result, input_obj):
        """ 商户信息需要从快照信息中获取 """
        merchant_json_str = input_obj.merchant_info
        try:
            merchant_json = json.loads(merchant_json_str)
        except:
            from app.core.logger import project_logger
            project_logger.error("\n merchant_info json error , input_apply id: %s" % (input_obj.id))
            merchant_json = {"name": input_obj.merchant.name}

        result.append({
            "moduleName": "其他信息",
            "lists": [
                {
                    'key': "商户名称",
                    "value": merchant_json.get("name", "")
                }
            ]
        })

    @classmethod
    def handle_other_photo(cls, result, input_obj, session):
        """ 基本信息里面的图片除外的其他图片 """
        images = []
        # if input_obj.is_student:
        if input_obj.student_phone:
            images.append({"imageUrl": cls.img_url_handler(input_obj.student_phone or ''), "imageDesc": "学生证/学信网截图"})
        if input_obj.seasame_credit:
            images.append({"imageUrl": cls.img_url_handler(input_obj.seasame_credit or ''), "imageDesc": "芝麻信用分截图"})
        img_result = input_obj.others_img.split(',') if input_obj.others_img else []
        index_ = 1
        for _, ele in enumerate(img_result):
            if ele:
                images.append({"imageUrl": cls.img_url_handler(ele), "imageDesc": "其他资料" + str(index_)})
                index_ += 1

        from app.models import ExtField

        ext_imgs = session.query(ExtField).filter(ExtField.field_type == FieldType.IMAGE, ExtField.input_apply_id == input_obj.id).all()
        if ext_imgs:
            images.extend([{'imageUrl': cls.img_url_handler(i.value), 'imageDesc': i.name} for i in ext_imgs])

        result.append({"moduleName": "其他资料", "images": images})

    @classmethod
    def is_add_to_show(cls, data):
        """ 判断当前字段是否应该进行显示 """
        if data['isShow'] is True or data['isShow'] == 1:
            return True
        return False

    @classmethod
    def img_url_handler(cls, img_url):
        """ 从风控访问的图片url需要加上/?from=riskbackend"""
        if img_url is None or img_url == '':
            return ''
        if img_url.endswith("/"):
            img_url = img_url[0:-1] + '?from=riskbackend'
        else:
            img_url = img_url + "?from=riskbackend"
        return img_url

    @classmethod
    def img_handler(cls, result, session, input_obj):
        """ 图片特殊化处理"""

        result.extend([
                {
                    "imageUrl": cls.img_url_handler(input_obj.id_face),
                    "imageDesc": "身份证正面"
                },
                {
                    "imageUrl": cls.img_url_handler(input_obj.id_back),
                    "imageDesc": "身份证背面"
                },
                {
                    "imageUrl": cls.img_url_handler(input_obj.photo_with_card),
                    "imageDesc": "手持身份证现场照"
                },
                {
                    "imageUrl": cls.img_url_handler(input_obj.bank_card),
                    "imageDesc": "银行卡照片"
                },
            ])

    @classmethod
    def ext_field(cls, field_key, input_apply_id, session):
        """ 对自定义的字段进行控制 """
        from app.models import ExtField

        ext = session.query(ExtField).filter(ExtField.key == field_key, ExtField.input_apply_id == input_apply_id).one_or_none()

        if not ext:
            return None
        return ext.value


class RiskManager(object):

    def __init__(self, session):

        self.session = session
        self.conclusion = None

    def get_conclusion(self, search_id):

        conclusion = self.risk_evaluation(search_id)['conclusion']
        self.conclusion = conclusion
        return conclusion

    def modify_score(self, search_id, mashang_score, phone):

        _map = {
            1: (600, 700),
            2: (600, 650),
            3: (550, 600),
            4: (450, 550),
            5: (300, 450),
        }
        _map2 = {
            1: 'one',
            2: 'two',
            3: 'three',
            4: 'four',
            5: 'five',
        }

        if self.conclusion:
            conclusion = self.conclusion
        else:
            conclusion = self.risk_evaluation(search_id)['conclusion']

        logging.info('伪造单号{0}的评分时计算的风险等级值是{1}, 马上评分是{2}'.format(search_id, conclusion, mashang_score))

        key = _map2[conclusion]
        scale = _map[conclusion]
        logging.info('正常的范围应该是{0}'.format(scale))

        fake = FakeScore.objects(phone=phone).first()
        # 有伪造记录
        if fake:
            fake_score = getattr(fake, key)
            # 有对应风险等级的伪造分
            if fake_score:
                logging.info('曾经等级{0}的分是{1}'.format(conclusion, fake_score))
            else:
                logging.info('曾经等级{0}没分'.format(conclusion))
                fake_score = -1
        else:
            logging.info('曾经没有伪造过')
            fake_score = -1

        # 马上没有分，但是历史对应等级有分
        if not mashang_score and fake_score != -1:
            logging.info('最后得分{0}'.format(fake_score))
            return fake_score

        # 马上有份但是历史没有分
        if mashang_score and fake_score == -1:
            # 不在范围
            if float(mashang_score) not in range(*scale):
                mashang_score = random.randint(*scale)

        # 马上有份历史也有份
        elif mashang_score and fake_score != -1:
            # 不在范围
            if mashang_score not in range(*scale):
                mashang_score = fake_score

        # 马上没分历史也没分
        else:
            mashang_score = random.randint(*scale)

        FakeScore.objects(phone=phone).update(
            upsert=True,
            set__phone=phone,
            **{'set__{0}'.format(key): mashang_score},
        )
        logging.info('最后得分{0}'.format(mashang_score))
        return mashang_score

    @staticmethod
    def return_assess(assess, result, msg):
        assess_list = [k for k in assess if assess[k] > 0]
        if assess_list:
            max_assess = max(assess_list)
        else:
            max_assess = RiskEvaluation.S
        _front_map = {
            RiskEvaluation.O: 6,
            RiskEvaluation.N: 7,
            RiskEvaluation.S: 1,
            RiskEvaluation.M: 3,
            RiskEvaluation.L: 4,
            RiskEvaluation.XL: 5,
        }
        if result:
            result = set(result)
            result = '<br/>'.join(result)
        else:
            result = msg.get(max_assess)
        return {
                'assess': _front_map[max_assess],
                'result': result,
        }

    @cache_riskevaluation
    def risk_evaluation(self, search_id):
        """贷前风险评估"""

        search = SingleSearch.objects(apply_number=search_id).first()
        input_apply = self.session.query(InputApply).get(search_id)

        if not search or not input_apply:
            return 'not exist'

        from app.credit.utils import check_whether_self
        if not check_whether_self(search):
            return 'not allowed'

        permissions = input_apply.merchant.company.permissions
        func_list = [i['func_name'] for i in json.loads(permissions)]

        result = search.operator_data.get('callback_operator', {})

        idAssess, idResult = self.id_verify(search.mashang_idcard, search.mashang_phone, search.channel_cellphone)
        noFaithAssess, noFaithResult = self.no_faith(search.no_faith_list, search.mashang_negative,
                                                     search.undesirable_info, search.blacklist_check,
                                                     search.obtain_riskinfocheck_data, search.financial_bad)
        overdueAssess, overdueResult = self.overdue(search.loan_over_time_blacklist, search.mashang_overdue,
                                                    search.channel_riskinfocheck, search.channel_netloanblacklist,
                                                    search.overdue_b, search.overdue_c)
        multiLoanAssess, multiLoanResult = self.multi_loan(search.multiple_loan, search.operator_multiplatform_data,
                                                           search.multiple_loan_apply_a, search.multiple_loan_apply_b,
                                                           search.multiple_loan_register_b)
        addressAssess, addressResult = self.address_match(search.distance, input_apply.work_address, input_apply.home_live_address)

        if 'operator_phonetime' in func_list:
            online_data = search.operator_phonetime_data
            online_source = 'zhongchengxin'
        elif 'mashang_online' in func_list:
            online_data = search.mashang_online
            online_source = 'mashang'
        else:
            online_data = {}
            online_source = ''

        if input_apply.token and not result:
            assess = {
                RiskEvaluation.O: 0,
                RiskEvaluation.N: 1,
                RiskEvaluation.S: 0,
                RiskEvaluation.M: 0,
                RiskEvaluation.L: 0,
                RiskEvaluation.XL: 0,
            }
            defaultRiskAssess = lostAssess = loanAssess = assess
            defaultRiskResult = lostResult = loanResult = [RiskEvaluation.SEARCHING]
        else:
            defaultRiskAssess, defaultRiskResult = self.default_risk(result, search.phone_home, search.phone_work, search.phone_school)
            loanAssess, loanResult = self.loan_contract(result)
            from app.capcha_report.util import UserExceptionAction
            ret = UserExceptionAction(result.get('data', {})).credit_risk_calculate(online_data=online_data, now=search.create_time.strftime('%Y%m%d'), source=online_source)
            lostAssess = ret['assess']
            lostResult = ret['result']

        _all = [
            idAssess, noFaithAssess, overdueAssess, multiLoanAssess, addressAssess,
            defaultRiskAssess, loanAssess, lostAssess,
        ]
        XL = sum([i[RiskEvaluation.XL] for i in _all])
        L = sum([i[RiskEvaluation.L] for i in _all])
        M = sum([i[RiskEvaluation.M] for i in _all])

        if XL >= 1 or L >= 2:
            conclusion = 5
        elif L == 1 or M >= 3:
            conclusion = 4
        elif M == 2:
            conclusion = 3
        elif M == 1:
            conclusion = 2
        else:
            conclusion = 1

        return {
            'conclusion': conclusion,
            'idVerify': self.return_assess(idAssess, idResult, RiskEvaluation.ID_VERIFY),
            'noFaith': self.return_assess(noFaithAssess, noFaithResult, RiskEvaluation.NOFAITH_VERIFY),
            'overdue': self.return_assess(overdueAssess, overdueResult, RiskEvaluation.OVERDUE_VERIFY),
            'multiLoan': self.return_assess(multiLoanAssess, multiLoanResult, RiskEvaluation.MULTI_VERIFY),
            'addrsesVerify': self.return_assess(addressAssess, addressResult, RiskEvaluation.ADDRESS_MATCH),
            'defaultRisk': self.return_assess(defaultRiskAssess, defaultRiskResult, RiskEvaluation.DEFAULT_RISK),
            'loanContact': self.return_assess(loanAssess, loanResult, RiskEvaluation.LOAN_CONTRACT),
            'lostContact': self.return_assess(lostAssess, lostResult, RiskEvaluation.LOST_VERIFY),
        }

    def id_verify(self, mashang_idcard, mashang_phone, channel_cellphone):

        assess = {
            RiskEvaluation.O: 0,
            RiskEvaluation.N: 0,
            RiskEvaluation.S: 0,
            RiskEvaluation.M: 0,
            RiskEvaluation.L: 0,
            RiskEvaluation.XL: 0,
        }
        result = []

        if mashang_idcard:
            if 'result' in mashang_idcard:
                t = mashang_idcard.get('result', {}).get('MC_IDENT_IDS', {}).get('IDENT_NAME', '')
                if not t or '不' in t:
                    assess[RiskEvaluation.XL] += 1
                    result.append(RiskEvaluation.ID_VERIFY.get(RiskEvaluation.XL))
                else:
                    assess[RiskEvaluation.S] += 1

        if channel_cellphone:
            # if channel_cellphone.get('code') == TelPrice.CODE:
            #     res_code = channel_cellphone.get('data', {}).get('res_code', 2)

            #     if res_code == -1:
            #         assess[RiskEvaluation.M] += 1
            #         result.append(RiskEvaluation.ID_VERIFY.get(RiskEvaluation.M))
            #     elif res_code == 1:
            #         assess[RiskEvaluation.S] += 1
            #     else:
            #         assess[RiskEvaluation.N] += 1
            from app.credit.pipeline import handle_cellphone
            r = handle_cellphone(channel_cellphone)
            if r['isPhone'] == 3:
                assess[RiskEvaluation.M] += 1
                result.append(RiskEvaluation.ID_VERIFY.get(RiskEvaluation.M))
            elif r['isPhone'] == 4:
                assess[RiskEvaluation.S] += 1
            else:
                assess[RiskEvaluation.N] += 1

        elif mashang_phone:
            if mashang_phone.get('is_pass') is True:
                assess[RiskEvaluation.O] += 1

            if 'result' in mashang_phone:
                t = mashang_phone.get('result', {}).get('MC_TECHK', {}).get('RUL_PHONE', '')
                if '不' in t:
                    assess[RiskEvaluation.M] += 1
                    result.append(RiskEvaluation.ID_VERIFY.get(RiskEvaluation.M))
                elif '一致' in t:
                    assess[RiskEvaluation.S] += 1
                else:
                    assess[RiskEvaluation.N] += 1

        return assess, result

    def no_faith(self, no_faith_list, mashang_negative, undesirable_info, blacklist_check, obtain_riskinfocheck,
                 financial_bad):

        assess = {
            RiskEvaluation.O: 0,
            RiskEvaluation.N: 0,
            RiskEvaluation.S: 0,
            RiskEvaluation.M: 0,
            RiskEvaluation.L: 0,
            RiskEvaluation.XL: 0,
        }
        result = []

        if no_faith_list and no_faith_list.get('code') == TelPrice.CODE:
            info = no_faith_list.get('data').get('info_list')
            if info:
                assess[RiskEvaluation.XL] += 1
                result.append(RiskEvaluation.NOFAITH_VERIFY.get('a'))

        if undesirable_info:
            from app.credit.pipeline import handle_undesirable_info
            res = handle_undesirable_info(undesirable_info)

            if res['isTarget'] == 2:
                assess[RiskEvaluation.XL] += 1
                result.append(RiskEvaluation.NOFAITH_VERIFY.get('c'))

        if obtain_riskinfocheck:
            from app.credit.pipeline import handle_obtain_riskinfocheck
            res = handle_obtain_riskinfocheck(obtain_riskinfocheck)

            if res['isTarget'] == 2:
                assess[RiskEvaluation.XL] += 1
                result.append(RiskEvaluation.NOFAITH_VERIFY.get('c'))

        if blacklist_check and isinstance(blacklist_check, dict) and blacklist_check.get('data'):
            assess[RiskEvaluation.L] += 1
            result.append(RiskEvaluation.NOFAITH_VERIFY.get('d'))

        if financial_bad:
            from app.credit.pipeline import handle_financial_bad
            res = handle_financial_bad(financial_bad)
            levels = [i["level"] for i in res["targetList"]]
            if "high" in levels:
                assess[RiskEvaluation.L] += 1
                result.append(RiskEvaluation.NOFAITH_VERIFY.get('f'))
            elif "medium" in levels:
                assess[RiskEvaluation.M] += 1
                result.append(RiskEvaluation.NOFAITH_VERIFY.get('f'))
            elif "low" in levels:
                assess[RiskEvaluation.M] += 1
                result.append(RiskEvaluation.NOFAITH_VERIFY.get('f'))

        return assess, result

    def overdue(self, loan_over_time_blacklist, mashang_overdue, channel_riskinfocheck, channel_netloanblacklist,
                overdue_b, overdue_c):

        assess = {
            RiskEvaluation.O: 0,
            RiskEvaluation.N: 0,
            RiskEvaluation.S: 0,
            RiskEvaluation.M: 0,
            RiskEvaluation.L: 0,
            RiskEvaluation.XL: 0,
        }
        result = []

        if loan_over_time_blacklist and loan_over_time_blacklist.get('code') == TelPrice.CODE:
            info = loan_over_time_blacklist.get('data').get('info_list')
            if info:
                def _day(d):
                    try:
                        day = int(d[:-1])
                    except:
                        day = 0
                    return day

                # total = sum([_day(i.get('time_out_days', '')) for i in info])
                try:
                    total = max([_day(i.get('time_out_days', '')) for i in info])
                except Exception as e:
                    project_logger.warn(e)
                    project_logger.warn(info)
                    total = 0

                if total > 60:
                    assess[RiskEvaluation.XL] += 1
                    result.append(RiskEvaluation.OVERDUE_VERIFY.get('a').format(total))
                elif 30 <= total <= 60:
                    assess[RiskEvaluation.L] += 1
                    result.append(RiskEvaluation.OVERDUE_VERIFY.get('b').format(total))
                elif 1 <= total < 30:
                    assess[RiskEvaluation.M] += 1
                    result.append(RiskEvaluation.OVERDUE_VERIFY.get('c').format(total))

        if channel_riskinfocheck and channel_riskinfocheck.get('data'):
            assess[RiskEvaluation.L] += 1
            result.append(RiskEvaluation.OVERDUE_VERIFY.get('g'))

        if channel_netloanblacklist and channel_netloanblacklist.get('data'):
            assess[RiskEvaluation.L] += 1
            result.append(RiskEvaluation.OVERDUE_VERIFY.get('e'))

        if overdue_b:
            from app.credit.pipeline import handle_overdue_b
            res = handle_overdue_b(overdue_b)
            if res["isTarget"]:
                assess[RiskEvaluation.L] += 1
                result.append(RiskEvaluation.OVERDUE_VERIFY.get('e'))

        if overdue_c:
            from app.credit.pipeline import handle_overdue_c
            res = handle_overdue_c(overdue_c)
            if res["isTarget"]:
                assess[RiskEvaluation.L] += 1
                result.append(RiskEvaluation.OVERDUE_VERIFY.get('e'))

        return assess, result

    def multi_loan(self, multiple_loan, operator_multiplatform_data, multiple_loan_apply_a, multiple_loan_apply_b, multiple_loan_register_b):

        assess = {
            RiskEvaluation.O: 0,
            RiskEvaluation.N: 0,
            RiskEvaluation.S: 0,
            RiskEvaluation.M: 0,
            RiskEvaluation.L: 0,
            RiskEvaluation.XL: 0,
        }
        result = []

        num_c = 0
        num_d = 0
        if multiple_loan and multiple_loan.get('code') == TelPrice.CODE:
            plat_num = multiple_loan.get("data").get("plat_num")
            if plat_num and isinstance(plat_num, str) and plat_num.isdigit():
                total = int(plat_num)
            elif plat_num and isinstance(plat_num, int):
                total = plat_num
            else:
                total = 0
            num_c = total

        elif operator_multiplatform_data and operator_multiplatform_data.get('code') == TelPrice.CODE:

            from app.credit.pipeline import handle_operator_multiplatform
            r = handle_operator_multiplatform(operator_multiplatform_data)
            total = r['loanNum']
            num_c = total
        if multiple_loan_register_b:
            from app.credit.pipeline import handle_multiple_loan_register_b
            res = handle_multiple_loan_register_b(multiple_loan_register_b)

            if res["isTarget"]:
                num_d = sum([i["platformNum"] if isinstance(i["platformNum"], int) else 0 for i in res["targetList"]])

        total = max(num_c, num_d)

        if total > 8:
            assess[RiskEvaluation.L] += 1
            result.append(RiskEvaluation.MULTI_VERIFY.get('a').format(total))
        elif 3 < total <= 8:
            assess[RiskEvaluation.M] += 1
            result.append(RiskEvaluation.MULTI_VERIFY.get('b').format(total))

        num_a = 0
        num_b = 0
        if multiple_loan_apply_a:
            from app.credit.pipeline import handle_multiple_loan_apply_a
            res = handle_multiple_loan_apply_a(multiple_loan_apply_a)
            num_a = len(res["targetList"])
        if multiple_loan_apply_b:
            from app.credit.pipeline import handle_multiple_loan_apply_b
            res = handle_multiple_loan_apply_b(multiple_loan_apply_b)
            if res["isTarget"]:
                steps = []
                _dict = {}

                def _process(d):
                    if d["timeNum"] <= 6 * 30:
                        steps.append(d["timeNum"])
                    _dict[d["timeNum"]] = d["total"]
                [_process(i) for i in res["targetList"]]
                num_b = _dict[max(steps)]
        num = max(num_a, num_b)
        if 4 <= num <= 8:
            assess[RiskEvaluation.M] += 1
            result.append(RiskEvaluation.MULTI_VERIFY.get('c').format(num))
        elif num >= 9:
            assess[RiskEvaluation.L] += 1
            result.append(RiskEvaluation.MULTI_VERIFY.get('c').format(num))
        elif num > 0:
            assess[RiskEvaluation.S] += 1
            result.append(RiskEvaluation.MULTI_VERIFY.get('c').format(num))

        return assess, result

    def third_risk(self, self_social_danger, self_tel_record, self_info_danger, social_dangers, tel_records, info_dangers):

        assess = {
            RiskEvaluation.O: 0,
            RiskEvaluation.N: 0,
            RiskEvaluation.S: 0,
            RiskEvaluation.M: 0,
            RiskEvaluation.L: 0,
            RiskEvaluation.XL: 0,
        }
        result = []

        def _third_risk(social_danger, tel_record, info_danger, people):

            if social_danger and social_danger.get('code') == TelPrice.CODE:
                info_list = social_danger.get('data').get('info_list')
                hit = 0
                if info_list:
                    social_info = []
                    for i in info_list:
                        keyword = ""
                        content = ""
                        if i.get("desc_keywords", ""):
                            keyword = i.get("desc_keywords")
                        if i.get("nick_keywords", ""):
                            keyword += i.get("nick_keywords")
                        if i.get("description", ""):
                            content = i.get("description")
                        if i.get("screen_name", ""):
                            content += i.get("screen_name")
                        if keyword and content:
                            social_info.append({"keyword": keyword, "content": content})
                    hit = len(info_list)
                    info = []
                    for social in social_info:
                        if any(social.values()):
                            info.append(social)
                    hit = len(info)
                    if hit:
                        assess[RiskEvaluation.L] += 1
                        result.append(RiskEvaluation.THIRD_RISK.get('a').format(people))
            if tel_record and tel_record.get('code') == TelPrice.CODE:
                hit = 0
                info_list = tel_record.get("data").get("info_list")
                if info_list:
                    for i in info_list:
                        if "phone" in i:
                            i.pop("phone")
                        if "keywords" in i:
                            i["keyword"] = i.pop("keywords")
                        if "buytime" in i:
                            i["orderTime"] = time_change(i.pop("buytime"))
                    hit = len(info_list)
                    if hit:
                        assess[RiskEvaluation.L] += 1
                        result.append(RiskEvaluation.THIRD_RISK.get('c').format(people))

            if info_danger and info_danger.get('code') == TelPrice.CODE:
                hit = 0
                info = None
                info_list = info_danger.get("data").get("info_list")
                if info_list:
                    info = [{"keyword": i.get("keywords", ""), "content": i.get("title", "")} for i in info_list]
                    hit = len(info_list)
                    if hit:
                        assess[RiskEvaluation.L] += 1
                        result.append(RiskEvaluation.THIRD_RISK.get('b').format(people))

        ############
        # 为关注的情况
        ############

        maps = {
            0: '家庭联系人',
            1: '单位联系人',
            2: '学校联系人',
        }

        result = []
        for i in range(3):
            social_danger = social_dangers[i]
            tel_record = tel_records[i]
            info_danger = info_dangers[i]

            _third_risk(social_danger, tel_record, info_danger, maps[i])

        ############
        # 为高的情况
        ############

        _third_risk(self_social_danger, self_tel_record, self_info_danger, '借款人')

        return assess, result

    def address_match(self, distance, work, home):

        assess = {
            RiskEvaluation.O: 0,
            RiskEvaluation.N: 0,
            RiskEvaluation.S: 0,
            RiskEvaluation.M: 0,
            RiskEvaluation.L: 0,
            RiskEvaluation.XL: 0,
        }
        result = []

        threshold = 3000
        if distance:
            d1 = distance.get("live2third", -1) or -1
            d2 = distance.get("third2work", -1) or -1

            if d1 == d2 == -1:
                # 没填家庭和工作地址
                if not work and not home:
                    assess[RiskEvaluation.O] += 1
                    result.append(RiskEvaluation.ADDRESS_MATCH.get(RiskEvaluation.O))
                    return assess, result
                else:
                    assess[RiskEvaluation.N] += 1
                    result.append(RiskEvaluation.ADDRESS_MATCH.get(RiskEvaluation.N))
                    return assess, result
            elif 0 <= d1 < threshold or 0 <= d2 < threshold:
                assess[RiskEvaluation.S] += 1
                result.append(RiskEvaluation.ADDRESS_MATCH.get(RiskEvaluation.S))
                return assess, result
            else:
                assess[RiskEvaluation.L] += 1
                result.append(RiskEvaluation.ADDRESS_MATCH.get(RiskEvaluation.L))
                return assess, result
        # 正常情况不会走到这一步
        else:
            # 没填家庭和工作地址
            if not work and not home:
                assess[RiskEvaluation.O] += 1
                result.append(RiskEvaluation.ADDRESS_MATCH.get(RiskEvaluation.O))
                return assess, result
            else:
                assess[RiskEvaluation.N] += 1
                result.append(RiskEvaluation.ADDRESS_MATCH.get(RiskEvaluation.N))
                return assess, result

    def default_risk(self, operator_data, phone_home, phone_work, phone_school):

        assess = {
            RiskEvaluation.O: 0,
            RiskEvaluation.N: 0,
            RiskEvaluation.S: 0,
            RiskEvaluation.M: 0,
            RiskEvaluation.L: 0,
            RiskEvaluation.XL: 0,
        }
        result = []

        if not operator_data or operator_data.get('code') != 31000:
            assess[RiskEvaluation.N] += 1
            result.append(RiskEvaluation.DEFAULT_RISK.get(RiskEvaluation.N))
            return assess, result

        if operator_data.get('code') != 31000:
            assess[RiskEvaluation.S] += 1
            result.append(RiskEvaluation.DEFAULT_RISK.get(RiskEvaluation.S))
            return assess, result

        one_month = operator_data.get('data', {}).get('deceitRisk', {}).get('monthCallInfo', {}).get('oneMonth', {})
        three_month = operator_data.get('data', {}).get('deceitRisk', {}).get('monthCallInfo', {}).get('threeMonth', {})

        home_num_default = 0 if phone_home else -1
        work_num_default = 0 if phone_work else -1
        school_num_default = 0 if phone_school else -1
        d = {}
        
        three_month_sorted = sorted(three_month.get('callList', []), key=lambda x: x.get('peer_number', 'default'))

        for nm, nm_info in groupby(three_month_sorted, key=lambda x: x.get('peer_number', 'default')):
            d[nm] = len(list(nm_info))

        home_num = d.get(phone_home, home_num_default)
        work_num = d.get(phone_work, work_num_default)
        school_num = d.get(phone_school, school_num_default)

        if 0 < home_num <= 300 and 0 < work_num <= 300 and 0 < school_num <= 300:
            assess[RiskEvaluation.S] += 1
            # result.append(RiskEvaluation.DEFAULT_RISK.get(RiskEvaluation.S))
        if home_num == 0:
            assess[RiskEvaluation.M] += 1
            result.append(RiskEvaluation.DEFAULT_RISK.get('a').format('家庭联系人'))
        if work_num == 0:
            assess[RiskEvaluation.M] += 1
            result.append(RiskEvaluation.DEFAULT_RISK.get('a').format('单位联系人'))
        if school_num == 0:
            assess[RiskEvaluation.M] += 1
            result.append(RiskEvaluation.DEFAULT_RISK.get('a').format('学校联系人'))
        if home_num > 300:
            assess[RiskEvaluation.L] += 1
            result.append(RiskEvaluation.DEFAULT_RISK.get('b').format('家庭联系人', home_num))
        if work_num > 300:
            assess[RiskEvaluation.L] += 1
            result.append(RiskEvaluation.DEFAULT_RISK.get('b').format('单位联系人', work_num))
        if school_num > 300:
            assess[RiskEvaluation.L] += 1
            result.append(RiskEvaluation.DEFAULT_RISK.get('b').format('学校联系人', school_num))

        one_month = operator_data.get('data', {}).get('deceitRisk', {}).get('monthCallInfo', {}).get('oneMonth', {})
        three_month = operator_data.get('data', {}).get('deceitRisk', {}).get('monthCallInfo', {}).get('threeMonth', {})
        """
        if one_month:
            remote_rate = one_month.get('remoteNum', 0) / (one_month.get('allNum', 1) or 1)
        else:
            remote_rate = -1
        """

        from app.capcha_report.util import UserExceptionAction
        ret = UserExceptionAction({}).remote_phone_rate(operator_data.get('data', {}), True)['result']
        remote_rate = float(ret[:-1]) / 100 if ret else 0

        if remote_rate > 0.5:
            assess[RiskEvaluation.L] += 1
            result.append(RiskEvaluation.DEFAULT_RISK.get('c').format(int(remote_rate * 100)))
        elif 0.5 >= remote_rate >= 0.3:
            assess[RiskEvaluation.M] += 1
            result.append(RiskEvaluation.DEFAULT_RISK.get('d').format(int(remote_rate * 100)))

        if three_month:
            collection_num = three_month.get('collectionNum', 0)
        else:
            collection_num = -1

        if collection_num > 5:
            assess[RiskEvaluation.L] += 1
            result.append(RiskEvaluation.DEFAULT_RISK.get('e').format(collection_num))
        elif 5 >= collection_num >= 3:
            assess[RiskEvaluation.M] += 1
            result.append(RiskEvaluation.DEFAULT_RISK.get('f').format(collection_num))

        callDuration = operator_data.get('data', {}).get('deceitRisk', {}).get('callDuration', [])

        night = ['2330', '0000', '0030', '0100', '0130', '0200', '0230', '0300', '0330', '0400', '0430', '0500', '0530']
        night_num = sum([i['connTimes'] for i in callDuration if i['connTime'] in night])
        all_num = sum([i['connTimes'] for i in callDuration])
        night_rate = float(night_num) / all_num if all_num else -1
        if night_rate > 0.3:
            assess[RiskEvaluation.L] += 1
            result.append(RiskEvaluation.DEFAULT_RISK.get('g').format(night_rate * 100))
        elif 0.3 >= night_rate > 0.1:
            assess[RiskEvaluation.M] += 1
            result.append(RiskEvaluation.DEFAULT_RISK.get('h').format(night_rate * 100))

        return assess, result

    def loan_contract(self, operator_data):

        assess = {
            RiskEvaluation.O: 0,
            RiskEvaluation.N: 0,
            RiskEvaluation.S: 0,
            RiskEvaluation.M: 0,
            RiskEvaluation.L: 0,
            RiskEvaluation.XL: 0,
        }
        result = []

        if not operator_data or operator_data.get('code') != 31000:
            assess[RiskEvaluation.N] += 1
            result.append(RiskEvaluation.LOAN_CONTRACT.get(RiskEvaluation.N))
            return assess, result

        assess[RiskEvaluation.S] += 1
        # result.append(RiskEvaluation.LOAN_CONTRACT.get(RiskEvaluation.S))

        call_records_info = operator_data.get('data', {}).get('deceitRisk', {}).get('monthCallInfo', {}).get('oneMonth', {}).get('callList', [])
        call_list = [i for i in call_records_info if '贷款中介' in (i.get('remark', '') or '')]
        call_set = []
        for i in call_list:
            if i in call_set:
                continue
            call_set.append(i.get("peer_number"))

        num = len(set(call_set))

        if num > 5:
            assess[RiskEvaluation.L] += 1
            result.append(RiskEvaluation.LOAN_CONTRACT.get(RiskEvaluation.L).format(num))
        elif 5 >= num >= 1:
            assess[RiskEvaluation.M] += 1
            result.append(RiskEvaluation.LOAN_CONTRACT.get(RiskEvaluation.M).format(num))

        return assess, result
