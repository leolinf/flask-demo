# -*- coding = utf-8 -*-

from app.common.conn import epc_brand
from app.config import Config

from app.common.function import make_response
from app.common.helper import exec_time
from app.common.constants import Code
from app.logger import project_logger

from .sessions import db


@exec_time("car_model", "nissan")
def nissan_car_model(vin):
    """车型查询"""

    project_logger.info("*******nissan*****%s**********", vin)
    return make_response(data=None)


@exec_time("structure", "nissan")
def nissan_structure(vin_id):
    """二三级目录查询"""

    vin_info = db.vin.find_one({"vin": vin_id})
    if not vin_info:
        return make_response(status=Code.SUCCESS_NOT_DATA)
    date = vin_info.get("date")
    cat_num = vin_info.get("cat_num")
    car_name = vin_info.get("model")

    first_group_list = []
    second_group_list = []
    second_group_dict = {}
    structureInfo = []
    for fisrtCode in ["BO", "EN", "AC", "CH", "TR", "EL"]:
        structureInfo.append({"firstCode": fisrtCode, "secondClass": []})
    # 车身系统
    BO = ["J", "K", "L", "M"]
    # 发动机系统
    EN = ["A", "B", "C", "D"]
    # 电器照明系统
    EL = ["E"]
    # 底盘系统
    CH = ["G", "H", "I"]
    # 变速系统
    TR = ["F"]
    # 附件
    AC = ["N"]

    for i in db.first_group.find({"cat_num": cat_num}):
        first_group_list.append(i.get('first_group_num'))
    for j in db.second_group.find({"cat_num": cat_num, "first_group_num": {"$in": first_group_list}}):
        second_group_list.append(j.get("second_group_num"))
        second_group_dict[j.get("second_group_num")] = j.get("second_group_name")
    for k in db.third_group.find({"cat_num": cat_num,
                                  "first_group_num": {"$in": first_group_list},
                                  "second_group_num": {"$in": second_group_list}}):
        start_date = k.get("start_date")
        end_date = k.get("end_date")
        first_group_num = k.get("first_group_num")

        if start_date <= date <= end_date:
            data = {
                    "name": second_group_dict[k.get("second_group_num")],
                    "secondNum": k.get("second_group_num") + "-2",
                    "picUrl": Config.IMG_URL + "/nissan/" + k.get("image_name") + '.jpg',
                    "thirdClass": [{
                        "name": k.get("third_group_name"),
                        "thirdNum": k.get("third_group_num") + "-3",
                        "picUrl": [Config.IMG_URL + "/nissan/" + k.get("image_name") + '.jpg'],
                        "search": {
                            "cat_num": cat_num,
                            "first_group_num": first_group_num,
                            "second_group_num": k.get("second_group_num"),
                            "third_group_num": k.get("third_group_num"),
                            "date": date,
                            "picUrl": Config.IMG_URL + "/nissan/" + k.get("image_name") + '.jpg'

                        }
                    }]
                }
            if first_group_num in BO:
                structureInfo[0].get("secondClass").append(data)
            elif first_group_num in EN:
                structureInfo[1].get("secondClass").append(data)
            elif first_group_num in AC:
                structureInfo[2].get("secondClass").append(data)
            elif first_group_num in CH:
                structureInfo[3].get("secondClass").append(data)
            elif first_group_num in TR:
                structureInfo[4].get("secondClass").append(data)
            elif first_group_num in EL:
                structureInfo[5].get("secondClass").append(data)

    return make_response(data={"carName": car_name, "structureInfo": structureInfo, "model": 63})


@exec_time('parts', "nissan")
def nissan_parts_get(kw):
    """具体的配件查询"""

    response = []
    for l in db.fourth_group.find({
        "cat_num": kw.get("cat_num"),
        "first_group_num": kw.get("first_group_num"),
        "second_group_num": kw.get("second_group_num"),
        "third_group_num": kw.get("third_group_num")}):

        start_date = l.get("start_date")
        end_date = l.get("end_date")
        try:
            if start_date <= kw.get("date") <= end_date:
                data = {
                   "local": l.get("part_index_num"),
                   "name": l.get("part_name"),
                   "others": "",
                   "picUrl": [kw.get("picUrl")],
                   "oem": l.get("part_num"),
                   "number": "",
                   "partNum": l.get("part_index_num"),
                }
                response.append(data)
        except:
            continue
    return make_response(data={"partsList": response})


@exec_time("all_parts", "nissan")
def nissan_all_parts(vin_id):
    """查询所有配件"""

    vin_info = db.vin.find_one({"vin": vin_id})
    if not vin_info:
        return make_response(status=Code.SUCCESS_NOT_DATA)
    date = vin_info.get("date")
    cat_num = vin_info.get("cat_num")
    first_group_list = []
    second_group_list = []
    third_group_list = []
    third_imge_dict = {}

    # 车身系统
    BO = ["J", "K", "L", "M"]
    # 发动机系统
    EN = ["A", "B", "C", "D"]
    # 电器照明系统
    EL = ["E"]
    # 底盘系统
    CH = ["G", "H", "I"]
    # 变速系统
    TR = ["F"]
    # 附件
    AC = ["N"]

    for i in db.first_group.find({"cat_num": cat_num}):
        first_group_list.append(i.get('first_group_num'))
    for j in db.second_group.find({"cat_num": cat_num, "first_group_num": {"$in": first_group_list}}):
        second_group_list.append(j.get("second_group_num"))
    for k in db.third_group.find({"cat_num": cat_num, "first_group_num": {"$in": first_group_list},
                                  "second_group_num": {"$in": second_group_list}}):
        start_date = k.get("start_date")
        end_date = k.get("end_date")
        if start_date <= date <= end_date:
            third_group_list.append(k.get("third_group_num"))
            third_imge_dict[k.get("third_group_num")] = k.get("image_name")

    response = []

    for l in db.fourth_group.find({"cat_num": cat_num, "first_group_num": {"$in": first_group_list},
                                   "second_group_num": {"$in": second_group_list},
                                   "third_group_num": {"$in": third_group_list}}):
        start_date = l.get("start_date")
        end_date = l.get("end_date")
        first_group_num = l.get("first_group_num")
        try:
            if start_date <= date <= end_date:
                if first_group_num in BO:
                    first_level = "BO"
                elif first_group_num in EN:
                    first_level = "EN"
                elif first_group_num in EL:
                    first_level = "EL"
                elif first_group_num in CH:
                    first_level = "CH"
                elif first_group_num in TR:
                    first_level = "TR"
                elif first_group_num in AC:
                    first_level = "AC"
                image_name = third_imge_dict.get(l.get("third_group_num"))
                data = {
                   "firstLevel": first_level,
                   "local": l.get("part_index_num"),
                   "number": "",
                   "others": "",
                   "picUrl": [Config.IMG_URL + '/nissan/' + image_name + '.jpg'],
                   "oem": l.get("part_num"),
                   "partName": l.get("part_name"),
                   "partNum": l.get("part_index_num"),
                   "secondName": l.get("second_group_name"),
                   "secondNum": l.get("second_group_num"),
                   "thirdName": l.get("third_group_name"),
                   "thirdNum": l.get("third_group_num")
                }
                response.append(data)
        except:
            continue

    return make_response(data={"partsList": response})
