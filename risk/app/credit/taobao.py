# -*- coding: utf-8 -*-
import time
import datetime
import operator
from itertools import groupby


now_time = time.time() * 1000

def handler_data(result, name, phone):
    """处理过滤数据"""

    _userinfo = user_info(result, name, phone)
    _address, default_address = address(result)
    _userinfo.update({"address": default_address})
    _orders, month_detail, top_three= orders_detail(result)

    return {
        "userInfo": _userinfo,
        "address": _address,
        "orders": _orders,
        "month_orders": orders_mon(result, name),
        "top_three": top_three,
        "month_detail": month_detail
    }


def user_info(result, name, phone):

    data = result.get("userinfo", {})
    huabei_amount = data.get("huabeiAmount", "") or ""
    huabei_total = data.get("huabeiTotal", "") or ""
    phone_auth, name_auth = 0, 0
    if data.get("name") == name:
        name_auth = 1
    if data.get("phone") == phone[:3] + "****" + phone[-4:]:
        phone_auth= 1
    return {
            "name": data.get("name", "") or "", # 姓名
            "username": data.get("username", "") or "", # 用户名
            "nikname": data.get("nikname", "") or "", # 昵称
            "email": data.get("email", "") or "", # 登录邮箱
            "phone": data.get("phone", "") or "", # 手机号
            "sex": data.get("sex", "") or "", # 性别
            "birthday": data.get("birthday", "") or "", # 生日
            "integral": data.get("integral", "") or "", # 用户积分
            "level": data.get("level", "") or "", # 会员等级
            "authStatus": data.get("authStatus", "") or "",# 支付宝实名认证状况
            "id": data.get("id", "") or "", # 身份证好
            "zfbPhone": data.get("zfbPhone", "") or "", # 支付宝账号
            "zfbType": data.get("zfbType", "") or "", # 账户类型
            "huabeiAmount": huabei_amount[:-2], # 花呗可用额度
            "huabeiTotal": huabei_total[:-2], # 花呗总额度
            "zfbBalance": data.get("zfbBalance", "") or "", # 支付宝余额
            "yuebaoTotal": data.get("yuebaoTotal", "") or "", # 余额宝收益
            "yuebao": data.get("yuebao", "") or "", # 余额宝
            "phoneAuth": phone_auth,
            "nameAuth": name_auth
    }


def address(data):
    address_resp = []
    default_address = ""
    for i in data.get("address", []) or []:
        if i.get("status") == "1":
            default_address = i.get("addressDetail")
        address_resp.append({
                "city": i.get("city", "") or "", # 城市
                "province": i.get("province", "") or "", # 省
                "area": i.get("area", "") or "", # 地区
                "mobile": i.get("mobile", "") or "", # 电话
                "status": i.get("status", "") or "", # 是否默认
                "addressDetail": i.get("addressDetail", "") or "", #详细地址
                "post": i.get("post", "") or "", # 邮箱
                "fullName": i.get("fullName", "") or "", #名字
            })
    return address_resp, default_address


def month_fun(result):

    if not result:
        return {
            "orderNum": 0,
            "orderAddressNum": 0,
            "name": "",
            "nameNum": 0,
            "phone": "",
            "address": ""
        }
    order_num = len(result)
    address_dict = {}
    name_dict = {}
    phone_dict = {}
    for i in result:
        receiver_name = i.get("receiverName")
        if receiver_name:
            if receiver_name not in name_dict:
                name_dict[receiver_name] = 1
            else:
                name_dict[receiver_name] += 1
        receiver_addr = i.get("receiverAddress")
        if receiver_addr:
            if receiver_addr not in address_dict:
                address_dict[receiver_addr] = 1
            else:
                address_dict[receiver_addr] += 1
        receiver_mobile = i.get("receiverMobile")
        if receiver_mobile:
            if receiver_mobile not in phone_dict:
                phone_dict[receiver_mobile] = 1
            else:
                phone_dict[receiver_mobile] += 1
    _address, _phone, _name = "", "", ("", "")
    if address_dict:
        _address = max(address_dict.items(), key=operator.itemgetter(1))[0]
    if name_dict:
        _name = max(name_dict.items(), key=operator.itemgetter(1))
    if phone_dict:
        _phone = max(phone_dict.items(), key=operator.itemgetter(1))[0]

    return {
        "orderNum": order_num,
        "orderAddressNum": len(address_dict),
        "name": _name[0],
        "nameNum": _name[1],
        "phone": _phone,
        "address": _address,
    }


def orders_detail(data):
    """订单详情"""

    orders_list = []
    one_month = []
    three_month = []
    six_month = []
    twelve_month = []
    phone_dict = {}
    name_dict = {}
    for i in data.get("orders", []) or []:
        address = i.get("receiverAddress", "") or "" # 收货地址
        ordTime = time_change_phone(i.get("ordTime", "")) # 订单日期
        receiver_mobile = i.get("receiverMobile", "") or ""
        receiver_name = i.get("receiverName", "") or ""
        orderStatus = i.get("orderStatus", "") or ""
        if "成功" not in orderStatus and "收货" not in orderStatus:
            continue
        result = {
                "actualFee": i.get("actualFee", "") or "",
                "receiverMobile": receiver_mobile, # 收货电话
                "orderStatus": orderStatus, # 订单状态
                "receiverName": receiver_name, # 收货人姓名
                "receiverAddress": address.strip(),
                "ordTime": ordTime,
                "goods": [{
                    "goodsName": a.get("goodsName", "") or "",
                    } for a in i.get("goodsInfo", []) or []], # 商品名称
        }

        if receiver_name not in name_dict:
            name_dict[receiver_name] = 1
        else:
            name_dict[receiver_name] += 1

        if receiver_mobile not in phone_dict:
            phone_dict[receiver_mobile] = 1
        else:
            phone_dict[receiver_mobile] += 1

        orders_list.append(result)
        time_diff = int(now_time - ordTime)
        if time_diff < 2592000000:
            one_month.append(result)
        if time_diff < 2592000000 *3:
            three_month.append(result)
        if time_diff < 2592000000 *6:
            six_month.append(result)
        if time_diff < 2592000000 *12:
            twelve_month.append(result)

    latest_list = sorted(orders_list, key=operator.itemgetter("ordTime"), reverse=True)
    lateAddress = ""
    lateTime = ""
    for i in range(len(latest_list)):
        if latest_list[i].get("receiverAddress"):
            lateAddress = latest_list[i].get("receiverAddress")
            lateTime = latest_list[i].get("ordTime")
            break
    month_detail = {
        "one_month": month_fun(one_month),
        "three_month": month_fun(three_month),
        "six_month": month_fun(six_month),
        "twelve_month": month_fun(twelve_month),
        "lateAddress": lateAddress,
        "lateTime": lateTime
    }
    address_list = []
    orders_list = sorted(orders_list, key=operator.itemgetter("receiverAddress"))
    for k, v in groupby(orders_list, operator.itemgetter("receiverAddress")):
        if k:
            data = list(v)
            _num = len(data)
            try:
                late_time = max([i.get("ordTime") for i in data])
                first_time = min([i.get("ordTime") for i in data])
            except ValueError:
                late_time, first_time = 0, 0
            address_list.append({"address": k, "num": _num, "lateTime": late_time, "firstTime": first_time})

    address_top = sorted(address_list, key=operator.itemgetter("num"))[:3]
    phone_top = sorted(phone_dict.items(), key=operator.itemgetter(1))
    name_top = sorted(name_dict.items(), key=operator.itemgetter(1))
    top_three = []
    for k,i in enumerate(address_top):
        try:
            name = name_top[k][0]
        except:
            name = ""
        try:
            phone = phone_top[k][0]
        except:
            phone = ""

        top_three.append({
            "address": i.get("address"),
            "lateTime": i.get("lateTime"),
            "firstTime": i.get("firstTime"),
            "name": name,
            "phone": phone
        })

    return orders_list, month_detail, top_three


def orders_mon(data, name):
    """按月份聚合"""

    order_list = [{
            "actualFee": i.get("actualFee", "") or "", # 实际付款
            "receiverMobile": i.get("receiverMobile", "") or "", # 收货电话
            "ordTime": i.get("ordTime", "")[:7], # 订单日期
            "receiverName": i.get("receiverName", "") or "",# 收货人姓名
            "receiverAddress": i.get("receiverAddress", "") or "", # 收货地址
            } for i in data.get("orders", []) or []\
                    if "成功" in i.get("orderStatus", "") or "收货" in i.get("orderStatus", "")
    ]
    response = []
    order_list = sorted(order_list, key=operator.itemgetter("ordTime"), reverse=True)
    for k, v in groupby(order_list, operator.itemgetter("ordTime")):
        data = list(v)
        order_num = len(data)
        order_money = sum([float(i.get("actualFee").replace("￥", "")) for i in data if i.get("actualFee").replace("￥", "")])
        order_month = [float(i.get("actualFee").replace("￥", "")) for i in data if i.get("receiverName") == name]
        self_order = len(order_month)
        self_money = sum(order_month)
        response.append({
            "orderMonth": k,
            "orderNum": order_num,
            "orderFee": round(order_money, 2),
            "orderOwnNum": self_order,
            "orderOwnfFee": round(self_money, 2),
            })

    return response


def time_change_phone(data):
    """时间转换为时间搓"""

    if not data:
        return 0
    if data is None:
        return 0
    try:
        return time.mktime(datetime.datetime.strptime(str(data), "%Y-%m-%d %H:%M:%S").timetuple()) * 1000
    except ValueError:
        return 0
