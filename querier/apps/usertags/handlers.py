# -*- coding: utf-8 -*-
import time
import datetime
import numpy as np
from framework.logger import project_logger
from utils.extract_dir import cat_map


def get_price():
    """读取品类均价和品类名称"""
    price_map = {}
    root_cat_map = {}
    with open("dat/cat_avg_consume.format", "r") as f:
        for line in f:
            ls = line.strip().split("\001")
            price_map[ls[0]] = ls[2].decode("utf-8")
            root_cat_map[ls[0]] = ls[1].decode("utf-8")
    return price_map, root_cat_map


def get_tags_map():
    """读取自定义标签"""
    tag_map = {}
    with open("dat/tag_define.format", "r") as f:
        for line in f:
            ls = line.strip().split("\001")
            tag_map[ls[0]] =ls[1].decode("utf-8")
    return tag_map


def get_most_brand():
    """读取高端品牌"""
    brand_map = {}
    with open("dat/high_brand.format", "r") as f:
        for line in f:
            ls = line.strip().split("\001")
            brand_map[ls[0].decode("utf-8")] = 1
    return brand_map


def get_root_category():
    """品类名称替换"""
    root_map = {}
    root_map_sort = []
    with open("dat/root_cat_map.format", "r") as f:
        for line in f:
            ls = line.strip().split("\001")
            root_map_sort.append(ls[0])
            root_map[ls[1].decode("utf-8")] = ls[2].decode("utf-8")
    return root_map, root_map_sort


map_tag = get_tags_map()
brand_map = get_most_brand()
price_map, root_cat_map = get_price()
root_map, root_map_sort = get_root_category()


def top_all(basic_list):
    tags = {}
    cat_id_dict = {}
    brand_dict = {}
    root_cat_dict = {}
    price = {}

    a = 0
    length = 0.0
    all_prices = 0.0
    for x in basic_list:
        cat_id = x.get("cat_id")
        try:
            int(cat_id)
        except ValueError:
            continue
        root_id = x.get('root_cat_id')
        try:
            int(root_id)
        except ValueError:
            continue
        prices = float(x.get("price"))
        all_prices += prices
        if x.get('brand') not in brand_dict:
            brand_dict[x.get('brand')] =prices
        else:
            brand_dict[x.get('brand')] += prices

        cat_tag_id = map_tag.get(cat_id, '-')

        if cat_tag_id != '-':
            tags[cat_tag_id] = 1

        if cat_id not in cat_id_dict:
            cat_id_dict[cat_id] = prices
        else:
            cat_id_dict[cat_id] += prices

        price[root_id] = prices
        if root_id not in root_cat_dict:
            root_cat_dict[root_id] = prices
        else:
            root_cat_dict[root_id] += prices

        if brand_map.has_key(x.get("brand")):
            a += 1
        length += 1
    if length == 0:
        return None
    # 高端品牌占比
    most_brand_rate = round(a *100 / length, 2)
    sorted_cat_id = sorted(cat_id_dict.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)[:5]
    sorted_brand = sorted(brand_dict.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)[:5]
    sorted_root_cat_id = sorted(root_cat_dict.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)[:5]
    # 取出品牌top5的占比
    brand_top = {}
    for brand in sorted_brand:
        brand_name = brand[0].replace(".", "_").replace(" ", '')
        brand_top[brand_name] = str(round(brand[1] * 100 / all_prices, 2)) + "%"
    # 取出子品类top5的占比
    cat_id_top = {}
    for cat_id in sorted_cat_id:
        cat_id_top[cat_map.get(cat_id[0])] = str(round(cat_id[1] * 100 /all_prices, 2)) + "%"
    # 取出品类top5的占比和价格对比
    root_cat_id_top = {}
    comp_avg_list = []
    for root_id in sorted_root_cat_id:
        category = root_map.get(root_cat_map.get(root_id[0]))
        root_cat_id_top[category] = str(round((root_id[1] *100 /all_prices), 2)) + "%"
        sum_price = float(price.get(root_id[0])) - float(price_map.get(root_id[0]))
        comp_avg = round(sum_price *100 / float(price_map.get(root_id[0])), 2)
        comp_avg_list.append({"category": category, "comp_avg": str(comp_avg) + '%'})

    # 取出最高价格及品类
    price_max = []
    for k, v in price.items():
        if not price_max:
            price_max = [k, v]
        if float(v) > float(price_max[1]):
            price_max = [k, v]
    cost_most = {"cost": str(price_max[1]), "category": root_map.get(root_cat_map.get(price_max[0]))}

    return {
        "favor_high_brand_per": str(most_brand_rate) + '%',
        "tag": tags,
        "favor_comp_avg": comp_avg_list,
        "favor_brand": brand_top,
        "favor_leaf_cat": cat_id_top,
        "favor_cat": root_cat_id_top,
        "favor_cost_most": cost_most
    }


def tel_time_change(data):
    """电商消费"""
    return time.mktime(datetime.datetime.strptime(str(data), "%Y%m").timetuple())


def filter_by_time(resp, mon_ago, end_time=None):
    """筛选几个月以前"""
    if mon_ago == 0:
        return []
    if not mon_ago and not end_time:
        return resp
    if not resp:
        return []

    ends_time = int(time.time())
    today = datetime.date.today()
    if end_time:
        ends_time = end_time
        today = datetime.datetime.fromtimestamp(int(end_time))

    if mon_ago:
        filter_data = []
        mon_ago = -mon_ago
        m, y = (today.month+mon_ago) % 12, today.year + ((today.month)+mon_ago-1) // 12
        if not m: m = 12
    # start_time = time.mktime(today.replace(today.year-int(mon_ago/12), today.month-mon_ago%12, 1).timetuple())
        start_time = time.mktime(today.replace(day=1, month=m, year=y).timetuple())
        project_logger.warn("[DATETIME|%s]", datetime.datetime.fromtimestamp(start_time))
        for res in resp:
            if ends_time >= tel_time_change(res.get("purchase_time")) >= start_time:
                filter_data.append(res)
        return filter_data
    else:
        filter_data = []
        for res in resp:
            if ends_time >= tel_time_change(res.get("purchase_time")):
                filter_data.append(res)
        return filter_data


def portrait_online(response):
    """计算数据"""
    # 统计相同月份
    pur_month_num_dict = {}
    # 统计相同月份购物金额
    pur_month_price = {}
    # 统计相同的品牌数
    brand_num_dict = {}
    # 品牌为空
    brand_null_price = 0.0
    brand_null_cnt = 0.0
    # 一级类消费
    root_price_dict = {}
    # 一级类购物次数
    root_cnt_dict = {}
    # 总消费
    all_prices = 0.0
    # 天猫消费
    b_prices = 0.0
    # 天猫购物次数
    b_cnt = 0.0
    # 50 元一下消费
    fifty_price = 0.0
    # 50 元一下次数
    fifty_cnt = 0.0
    # 总长度
    lenth = 0.0
    for resp in response:
        root_id = resp.get('root_cat_id')
        try:
            int(root_id)
        except ValueError:
            continue
        lenth += 1.0
        prices = float(resp.get("price"))
        # 一级类目
        if root_id not in root_price_dict:
            root_price_dict[root_id] = prices
            root_cnt_dict[root_id] = 1.0
        else:
            root_price_dict[root_id] += prices
            root_cnt_dict[root_id] += 1.0
        all_prices += prices
        # 月份
        purchase_time = resp.get("purchase_time")
        if purchase_time not in pur_month_num_dict:
            pur_month_num_dict[purchase_time] = 1
            pur_month_price[purchase_time] = prices
        else:
            pur_month_num_dict[purchase_time] += 1
            pur_month_price[purchase_time] += prices
        # 品牌
        if resp.get('brand') not in brand_num_dict:
            brand_num_dict[resp.get('brand')] =prices
        else:
            brand_num_dict[resp.get('brand')] += prices
        # 品牌为其他或者空格
        if resp.get('brand') != u'其他' or not resp.get("brand"):
            brand_null_price += prices
            brand_null_cnt += 1.0

        # 统计天猫消费
        if resp.get("bc_type") == "B":
            b_prices += prices
            b_cnt += 1.0
        # 50元一下消费
        if prices < 50.0:
            fifty_price += prices
            fifty_cnt += 1.0

    # 每月购物次数
    month_num = len(pur_month_num_dict)
    month_all_list = [v for k, v in pur_month_num_dict.items()]
    month_avg = sum(month_all_list) / float(month_num)
    # 每月价格
    month_all_price = [v for k, v in pur_month_price.items()]
    month_avg_price = sum(month_all_price) / float(month_num)
    month_root_ave_price = {}
    # 一级类目全网平均综合值
    for root_id, value in root_price_dict.items():
        month_root_ave_price[root_id] = (value / root_cnt_dict[root_id]) / float(price_map.get(root_id))
    m_general_ratio = sum([v for k, v in month_root_ave_price.items()]) / float(len(month_root_ave_price))

    m_cnt_ratio_list = []
    m_price_ratio_list = []
    for root_id in root_map_sort:
        root_price = root_price_dict.get(root_id)
        root_cnt = root_cnt_dict.get(root_id)
        m_price_ratio_list.append( str(round((root_price if root_price else 0) / all_prices, 4)*100) + '%')
        m_cnt_ratio_list.append( str(round((root_cnt if root_cnt else 0) / lenth, 4)*100) + '%')

    return {
        "m_pur_month_num": str(month_num),
        "m_avg_month_cnt": '%.2f'%(month_avg),
        "m_std_month_cnt": '%.2f'%(np.std(month_all_list)),
        "m_brand_num": str(len(brand_num_dict)),
        "m_rt_cat_num": str(len(root_price_dict)),
        "m_b_price_ratio": str(round(b_prices*100/all_prices, 2)) + '%',
        "m_b_cnt_ratio": str(round(b_cnt*100/lenth, 2)) + "%",
        "m_brand_price_ratio": str(round(brand_null_price*100/all_prices, 2)) + '%',
        "m_brand_cnt_ratio": str(round(brand_null_cnt*100/lenth, 2)) + '%',
        "m_pur_price_sum": '%.2f'%(all_prices),
        "m_bfifty_price_ratio": str(round(fifty_price*100/all_prices, 2)) + '%',
        "m_bfifty_cnt_ratio": str(round(fifty_cnt*100/lenth, 2)) + '%',
        "m_avg_month_price": '%.2f'%(month_avg_price),
        "m_std_month_price": '%.2f'%(np.std(month_all_price)),
        "m_general_ratio": '%.2f'%(m_general_ratio),
        "m_cnt_ratio_list": m_cnt_ratio_list,
        "m_price_ratio_list": m_price_ratio_list,
    }
