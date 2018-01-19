# -*- coding: utf-8 -*-

import time
import datetime
from queue import Queue
from threading import Thread
import traceback
import json
import copy
import requests

from flask import jsonify, g
from sqlalchemy.orm import scoped_session

from app.models.mongos import MonitorSearch
from app.models.sqlas import Monitor as MonitorSql
from app.constants import MonitorStatus, Code
from .monitor import tel_list, sync_search
from app.core.functions import (
    datetime2timestamp, make_response, period2datetime,
    timestamp2datetime, age_from_idcard, sex_from_idcard
)
from app.databases import Session
from app.credit.utils import check_whether_self
from app.user.function import current_user


def get_single_monitor(monitor_id):
    """获取贷中监控详情"""

    session = scoped_session(Session)
    monitor = MonitorSearch.objects(monitor_id=monitor_id).first()
    monitor_sql = session.query(MonitorSql).get(monitor_id)

    if not monitor:
        return 'not exist'

    if monitor_sql.status == MonitorStatus.DOING:
        return 'not ready'

    if not check_whether_self(monitor):
        return 'not allowed'

    res = {
        'basicInfo':{
            'age': age_from_idcard(monitor_sql.idcard),
            'idCard': monitor_sql.idcard,
            'name': monitor_sql.name,
            'phone': monitor_sql.phone,
            'sex': sex_from_idcard(monitor_sql.idcard) if monitor_sql.idcard else '--',
            'status': 1 if monitor_sql.status == MonitorStatus.DONE else 0,
        },
        'eBusinessDanger': monitor.e_business_danger,
        'infoDanger': monitor.info_danger,
        'loanOverTimeBlackList': monitor.loan_over_time_blacklist,
        'multipleLoan': monitor.multiple_loan,
        'noFaithList': monitor.no_faith_list,
        'phoneMarkBlackList': monitor.phone_mark_blaklist,
        'phoneRelative': monitor.phone_relative,
        'socialDanger': monitor.social_danger,
        'break_num': monitor.break_num,
    }
    monitor.update(
        set__e_business_danger=remove_new(monitor.e_business_danger),
        set__info_danger=remove_new(monitor.info_danger),
        set__loan_over_time_blacklist=remove_new(monitor.loan_over_time_blacklist),
        set__multiple_loan=remove_new(monitor.multiple_loan),
        set__no_faith_list=remove_new(monitor.no_faith_list),
        set__phone_mark_blaklist=remove_new(monitor.phone_mark_blaklist),
        set__social_danger=remove_new(monitor.social_danger),
    )
    session.remove()
    return res


def single_monitor(*args):
    """添加单个贷中监控"""

    now = datetime.datetime.now()

    result_queue = Queue()
    func_queue = Queue()

    func_queue.put(tel_list)
    func_queue.put(sync_search)

    def _func(p, q, *args):
        func = p.get()
        try:
            result = func(*args)
        except:
            traceback.print_exc()
            result = {'targetList': [], 'isTarget': 0, 'targetNum': 0}
        q.put({func.__name__: result})
        p.task_done()

    for i in range(func_queue.qsize()):
        Thread(
            target=_func,
            args=(func_queue, result_queue, *args),
        ).start()

    func_queue.join()
    result_dict = {}
    while not result_queue.empty():
        result_dict.update(result_queue.get())

    result_tel_list = result_dict['tel_list']
    result_sync_search = result_dict['sync_search']

    def _break_list(r):
        l = []
        r = copy.deepcopy(r)
        r.pop('break_num')
        for k, v in r.items():
            if v['isTarget'] == 1:
                l.append(k)
        return l
    break_list = _break_list(result_sync_search)
    session = Session()
    try:
        monitor = MonitorSearch.objects.get(monitor_id=args[3])
        monitor_sql = session.query(MonitorSql).get(args[3])
    except:
        traceback.print_exc()
        return
    monitor.unusual_trend = change_unusual(monitor, result_sync_search["break_num"])
    monitor.e_business_danger = check_new(monitor.e_business_danger, result_sync_search['eBusinessDanger'])
    monitor.info_danger = check_new(monitor.info_danger, result_sync_search['infoDanger'])
    monitor.loan_over_time_blacklist = check_new(monitor.loan_over_time_blacklist, result_sync_search['loanOverTimeBlackList'])
    monitor.multiple_loan = check_new(monitor.multiple_loan, result_sync_search['multipleLoan'])
    monitor.no_faith_list = check_new(monitor.no_faith_list, result_sync_search['noFaithList'])
    monitor.social_danger = check_new(monitor.social_danger, result_sync_search["socialDanger"])
    monitor.phone_mark_blaklist = check_new(monitor.phone_mark_blaklist, result_sync_search['phoneMarkBlackList'])
    monitor.phone_relative = result_sync_search['phoneRelative']
    monitor.time_line_data = result_tel_list
    if result_sync_search['break_num'] > monitor.break_num:
        monitor.break_num = result_sync_search['break_num']
        monitor_sql.break_num = result_sync_search['break_num']
        monitor_sql.last_break_time = now
    monitor.last_update_time = now
    monitor.status = MonitorStatus.DONE
    monitor.save()

    monitor_sql.status = MonitorStatus.DONE
    monitor_sql.exception_list = ','.join(break_list)
    session.merge(monitor_sql)
    session.commit()
    return monitor


def change_unusual(monitor, number):
    """贷中异常监控"""
    now_day = datetime.datetime.now()
    unusual_trend_data = monitor.unusual_trend
    def _fun(data):
        a = datetime.datetime.fromtimestamp(data/1000)
        return a.year == now_day.year and a.month == now_day.month and a.day == now_day.day
    if unusual_trend_data:
        data_time = unusual_trend_data[-1].get("timestamp")
        if _fun(data_time):
            if number > monitor.break_num:
                return unusual_trend_data[:-1] + [{"unusualNum": number, "timestamp": int(time.time()*1000)}]
            else:
                return unusual_trend_data[:-1] + [{"unusualNum": monitor.break_num, "timestamp": int(time.time()*1000)}]
        else:
            if number > monitor.break_num:
                return unusual_trend_data + [{"unusualNum": number, "timestamp": int(time.time()*1000)}]
            else:
                return unusual_trend_data + [{"unusualNum": monitor.break_num, "timestamp": int(time.time()*1000)}]
    else:
        return [{"unusualNum": number, "timestamp": int(time.time()*1000)}]


def check_new(old, new):
    """判断是否需要填补覆盖，加上new标签"""

    old = copy.deepcopy(old)
    result = copy.deepcopy(old.get('targetList', []))

    def _process(dic):
        if 'isNew' in dic:
            dic.pop('isNew')
        return json.dumps(dic)

    old_without_new_json = set([_process(i) for i in old.get('targetList', [])])
    old_without_new_dict = [json.loads(i) for i in old_without_new_json]
    new_json = set([_process(i) for i in new.get('targetList', [])])

    union_json = old_without_new_json | new_json
    union_dict = [json.loads(i) for i in union_json]

    for i in union_dict:
        if i not in old_without_new_dict:
            d = copy.deepcopy(i)
            d['isNew'] = 1
            result.append(d)

    res = {
        'isTarget': max([old.get('isTarget', -1), new.get('isTarget', 0)]),
        'targetNum': len(result),
        'targetList': result,
    }

    if "loanNum" in new:
        res.update({"loanNum": len(result)})
    if "attentionList" in new:

        response_result = copy.deepcopy(old.get('attentionList', []))

        old_without_new_json = set([_process(i) for i in old.get('attentionList', [])])
        old_without_new_dict = [json.loads(i) for i in old_without_new_json]
        new_json = set([_process(i) for i in new.get('attentionList', [])])

        union_json = old_without_new_json | new_json
        union_dict = [json.loads(i) for i in union_json]

        for i in union_dict:
            if i not in old_without_new_dict:
                d = copy.deepcopy(i)
                d['isNew'] = 1
                response_result.append(d)
        res.update({"attentionList": response_result})
    return res


def remove_new(dic):
    """去掉new"""

    def _process(d):
        if 'isNew' in d:
            d['isNew'] = 0
        return d

    if 'targetList' in dic:
        dic['targetList'] = [_process(d) for d in dic['targetList']]
    if 'attentionList' in dic:
        dic['attentionList'] = [_process(d) for d in dic['attentionList']]
    return dic


def modify_phone(phone):
    """根据手机号格式不同修改成统一格式"""

    phone = str(phone)
    l = phone.split('.')
    if len(l) == 2:
        return l[0]
    return phone


def gen_search_number(company_id=None):
    """生成反欺诈的序列号"""
    if company_id is None:
        return

    if isinstance(company_id, int):
        company_id = str(company_id).zfill(3)
        company = Company.objects(company_id=company_id).first()
        if company is None:
            return

    elif isinstance(company_id, str) and len(company_id) == 3:
        company = Company.objects(company_id=company_id).first()
        if company is None:
            return

    elif isinstance(company_id, str) and len(company_id) == 24:
        company = Company.objects(id=company_id).first()
        company_id = company.company_id
        if company is None:
            return

    elif isinstance(company_id, bytes) and len(company_id) == 3:
        company_id = company_id.decode()
        company = Company.objects(company_id=company_id).first()
        if company is None:
            return
    elif isinstance(company_id, bytes) and len(company_id) == 24:
        company = Company.objects(id=company_id.decode()).first()
        company_id = company.company_id
        if company is None:
            return
    else:
        return

    company_objectid = str(company.id)

    today = datetime.date.today()
    timestamp = today.strftime('%Y%m%d')

    user_num = company_id.zfill(3)

    count = SingleSearch.objects(
        company_id=company_objectid,
        create_time__gte=today
    ).count()
    num = str(count + 1).zfill(6)

    return '{0}{1}{2}{3}'.format('A', user_num, timestamp, num)


def get_args(args, index, default):

    if len(args) > index and args[index] != '':
        return args[index]
    else:
        return default


def dict_list_util(ret):
     """字典和列表有空数据全部改成×××"""

     if isinstance(ret, list):
         for i in ret:
             dict_list_util(i)

     if isinstance(ret, dict):
         for k, v in ret.items():
             if v == '-':
                 ret[k] = ""
             if isinstance(ret[k], dict):
                 dict_list_util(ret[k])

             if isinstance(ret[k], list):
                 dict_list_util(ret[k])
