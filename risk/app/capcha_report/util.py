# coding: utf-8
import datetime
from collections import Counter
from operator import itemgetter, attrgetter
import re
import time
from functools import partial
from ..constants import RiskEvaluation
from app.core.functions import save_to_cache


def judge_day_serial():
    """ 判断两个时间是否连续 """
    pass


def second_to_minute(t):
    t = int(t or 0)
    # if t % 60 == 0:
    #     return t // 60
    # return t // 60 + 1
    return float('%.2f' % (t / 60))

def two_num(d):
    if d == 0:
        return float(d)
    return float('%.2f' % d)

def cao_time_time_to_str(d):

    if d == 0:
        return ''

    if not d:
        return d
    timeArray = time.localtime(d)
    otherStyleTime = time.strftime("%Y-%m-%d", timeArray)
    return otherStyleTime


class UserExceptionAction:
    """
    用户异常行为分析
    """
    __slots__ = ('data')

    def time_trans(self, t_s):
        return datetime.datetime.strptime(t_s, "%Y%m%d")

    def __init__(self, data):
        self.data = data

    def long_time_slicense(self, data_r, flag, now=None):
        """ 长时间静默 """
        # data = self.data.get('silenceInfo', []).copy()
        data = data_r.copy()
        key = 'connDate'
        data = sorted(data, key=lambda x:int(x.get(key, 0)))
        if not data and flag is False:

            return {
                "name": "手机长时间静默情况",
                "result": '',
                "accord": '',
                "assess": 6,
            }
        if not data:
            return {
                "name": "手机长时间静默情况",
                "result": '0',
                "accord": '近6个月出现0次手机长时间静默情况，失联风险低',
                "assess": 1,
            }
        try:
            result = []
            if now is None:
                now = datetime.datetime.now().strftime('%Y%m%d')
            data.append({'connDate': now, 'connTimes': 1})
            last_t = self.time_trans(data[0].get(key))
            for index in range(1, len(data)):
                now_t = self.time_trans(data[index].get(key))
                if (now_t - last_t).days > 10:
                    result.append({'days': (now_t - last_t).days, "st": last_t, "end": now_t})
                last_t = now_t
            result = sorted(result, key=itemgetter('days', "st"), reverse=False)

            def out_put(src):
                """ 整理成前端所需要的格式 """
                out_put = []
                template = "静默{0}天，时间{1}~{2}"
                for value in src:
                    out_put.append(template.format(
                        value['days'], value['st'].strftime("%Y-%m-%d"), value['end'].strftime("%Y-%m-%d")
                    ))
                # l = '<ul>近6个月出现3次手机长时间静默情况，失联风险{}'
                risk = {
                    0: '低',
                    1: '关注',
                    2: '高'
                }
                level = 0
                if len(src):
                    if src[-1]['days'] <= 10:
                        level = 0
                    elif src[-1]['days'] <= 30:
                        level = 1
                    else:
                        level = 2
                l = '近6个月出现{}次长时间手机静默情况，失联风险{}<ul>'.format(len(result), risk[level])

                for i in out_put:
                    l = l + '<li>' + i + '</li>'
                l = l + '</ul>'
                if len(result) == 0:
                    l = '近6个月无连续10天通话记录为空情况'
                return len(result), l, level

            max_result = result[-1]['days'] if result else 0
            assess, name, result = out_put(result)
            d = {
                0: 1,
                1: 2,
                2: 4
            }
            return {
                "name": "手机长时间静默情况",
                "result": assess,
                "accord": name,
                "assess": d[result],
                'max_result': max_result,
            }
        except:
            import traceback
            traceback.print_exc()
            return {
                "name": "手机长时间静默情况",
                "result": '0',
                "accord": '近6个月出现0次手机长时间静默情况，失联风险低',
                "assess": 1,
                'max_result': 0,
            }

    def night_phone(self, data_r, flag):
        """ 夜间通话占比 """
        if data_r is None:
            data_r = {}

        def judge_night(d):
            def calcu(t):
                try:
                    if 0 <= int(t[0:2]) <= 4:
                        return True
                    return False
                except:
                    return False

            if d['connTime'] == '2330' or d['connTime'] == '0500' or calcu(d['connTime']):
                return True
            return False

        # data = self.data.get('deceitRisk', {}).get('callDuration', []).copy()
        data = data_r.copy()
        if not data and flag is False:

            return {
                "name": "夜间通话占比",
                "result": '',
                "accord": '',
                "assess": 6,
            }
        try:
            night_count, sum_ = 0, 0
            for ele in data:
                sum_ += int(ele.get('connTimes', 0))
                if judge_night(ele) is True:
                    night_count += int(ele.get('connTimes', 0))

            def out_put(night, sum_):
                template1 = '近6个月夜间通话占比≦10%，违约风险低'
                template2 = '近6个月夜间通话占比10%~30%，有违约风险'
                template3 = '近6个月夜间通话占比>30%，违约风险较高'

                r = two_num(night_count * 100 / sum_ if sum_ else 0)
                level = None
                if r <= 10:
                    ret_ = template1
                    level = 1
                elif r < 30:
                    ret_ = template2
                    level = 2
                else:
                    ret_ = template3
                    level = 4

                return {
                    "name": "夜间通话占比",
                    "result": ('%.2f' % r if r else '0.0') + '%',
                    "accord": ret_,
                    "assess":level
                }

            return out_put(night_count, sum_)
        except:
            return {
                "name": "夜间通话占比",
                "result": 0,
                "accord": '近6个月夜间通话占比≦10%，违约风险低',
                "assess": 1,
            }

    def contract_num(self, data_r, flag):
        """ 联系人数量 (6个月)"""
        # data = self.data.get("monthCallInfo").copy()
        if data_r is None:
            data_r = {}

        data = data_r.copy()
        data = data.get('sixMonth', {})
        if not data and flag is False:

            return {
                "name": "联系人数量",
                "result": '',
                "accord": '',
                "assess": 6,
            }
        try:
            template = {
                0: '近6个月联系人数量大于10人时，失联风险低',
                1: '近6个月联系人数量低于10人时，有失联风险' }

            num = int(data.get("contactsNum", 0))
            level = 0
            if num < 10:
                level = 1
            return {
                'name': '联系人数量',
                'result': num,
                "accord": template[level],
                'assess': level + 1}
        except:
            return {
                'name': '联系人数量',
                'result': 0,
                "accord": "近6个月联系人数量低于10人时，有失联风险",
                'assess': 1}

    def contact_phone_num(self, data_r, flag):
        """ 互通电话数量 """
        # data = self.data.get("monthCallInfo").copy()
        if data_r is None:
            data_r = {}
        data = data_r.copy()
        data = data.get('sixMonth', {})
        if not data and flag is False:

            return {
                "name": "互通电话数量",
                "result": '',
                "accord": '',
                "assess": 6,
            }
        try:
            template = {
                1: '近6个月互通电话数小于5人时，有失联风险',
                0: '近6个月互通电话数大于5人时，失联风险低'}

            num = int(data.get("mutualNum", 0))
            level = 0
            if num < 5:
                level = 1
            return {
                'name': '互通电话数量',
                'result': num,
                "accord": template[level],
                'assess': level + 1}
        except:
            return {
                "name": "互通电话数量",
                "result": 0,
                "accord": '近6个月互通电话数小于5人时，有失联风险',
                "assess": 1,
            }

    def remote_phone_rate(self, data_r, flag):
        """ 异地通话占比 """
        if data_r is  None:
            data_r = {}
        data = data_r.copy()
        data = data.get('deceitRisk', {}).get("monthCallInfo", {}).get("oneMonth", {})
        # 进入到这个函数说明已经查询良，但是没有查询到数据而已
        if not data:
            return {
                "name": "异地通话记录",
                "result": 0,
                "accord": '近1个月异地通话时间占比小于30%时，违约风险低',
                "assess": 1,
            }
        all_num = data.get('allNum', 1)
        template = {
            0: '近1个月异地通话时间占比小于30%时，违约风险低',
            1: '近1个月异地通话时间占比小于50%时，有违约风险',
            2: '近1个月异地通话时间占比大于50%时，违约风险高'
        }
        template_li = '<li>{0}通话{1}次，通话时间{2}分钟，主叫{3}次、被叫{4}次，最近通话时间{5}</li>'
        self_phone_area = data_r.get("baseInfo", {}).get("phoneBelongArea", "")
        city = data_r.get("baseInfo", {}).get("city", "")
        province = data_r.get("baseInfo", {}).get("province", "")
        self_phone_type = data_r.get("phoneInfo", {}).get("operator", "")

        def num_(d):
            try:
                return int(d)
            except:
                return 0

        def init_dict(d, key):
            if key in d:
                return
            d[key] = {
                'times': 0,
                "duration": 0, # 通话时间
                "callTimes": 0,
                "calledTimes": 0,
                "lastTime": datetime.datetime.strptime("1970-01-01", "%Y-%m-%d")
            }

        def cus_time_handle(d):
            try:
                return datetime.datetime.strptime(d, "%Y-%m-%d %H:%M:%S")
            except:
                return datetime.datetime.strptime("1970-01-01", "%Y-%m-%d")

        def cus_time_str(d):
            try:
                if d == datetime.datetime.strptime("1970-01-01", "%Y-%m-%d"):
                    return '--'
                return d.strftime("%Y-%m-%d %H:%M:%S")
            except:
                return '--'

        def ratio_han(a, b):
            try:
                return float('%.2f' % (a*100/b))
            except:
                return 0

        def dict_num_handle(src, dest):
            area = src.get("location", "") or ""
            init_dict(dest, area)
            dest[area]['duration'] = num_(dest[area].get("duration", "")) + num_(src.get("duration", 0))
            dest[area]['callTimes'] = num_(dest[area].get("callTimes", "")) + (1 if src.get("dial_type", '') == 'DIAL' else 0)
            dest[area]['calledTimes'] = num_(dest[area].get("calledTimes", "")) + (0 if src.get("dial_type", '') == 'DIAL' else 1)
            dest[area]['lastTime'] = dest[area]['lastTime'] if dest[area]['lastTime'] < cus_time_handle(src.get("time")) else cus_time_handle(src.get("time"))
            dest[area]['times'] += 1

        remote_result = {}
        remote_count = 0

        def remote(city, province, location, location_type):
            mobileCity = city # 帐号归属城市
            mobileProvince = province # 帐号归属省份
            ROAM_1 = u"漫游"
            ROAM_2 = u"非"
            ROAM_3 = u"异地"
            ROAM_4 = u"边漫"
            # 判定为非异地通话
            if mobileCity and mobileProvince and location:
                if mobileProvince == location or mobileProvince + u"省" == location:
                    return False
                # 判定为异地通话
                if location not in mobileCity and mobileCity not in location:
                    return True
            else:

                # 通话地类型是漫游的判定为漫游
                if not location_type:
                    return False
                # 通话地类型是漫游的判定为漫游
                if (ROAM_1 in location_type and ROAM_2 in location_type) or ROAM_3 in location_type or ROAM_4 in location_type:
                    # 判定为异地通话
                    return True
            # 判定为非异地通话
            return False

        def map_f(ele, sum_d):
            nonlocal city, province, self_phone_area, remote_count

            # if self_phone_type is True and (ele.get("location", "") != self_phone_area): # 联通
            #    return
            # if self_phone_type is False and ('本地' not in ele.get("location_type", '')):
            #    return
#            location = ele.get("location", "")
#            if not location:
#                location = ""
#            if not isinstance(self_phone_area, str) and len(self_phone_area) <= 2:
#                return
#            if self_phone_area[2:] in location:
#                return
            if not remote(city, province, ele.get("location", ""), ele.get("location_type", "")):
                return
            remote_count += 1
            # 数据计算
            dict_num_handle(ele, sum_d)

        def result_handle(key, value):
            """ """
            return template_li.format(key, value['times'], '%.2f' % float(two_num(value['duration'] / 60)), value['callTimes'],
                                      value['calledTimes'], cus_time_str(value.get('lastTime', '')))

        map_f_par = partial(map_f, sum_d=remote_result)
        import json
        list(map(map_f_par, data.get("callList", [])))

        # d = list(map(result_handle, remote_result))
        html_lis = ''.join([result_handle(key, value) for key, value in remote_result.items()])
        ratio = ratio_han(remote_count, all_num)

        url = "<ul>"
        result = 0
        if ratio < 30:
            url += template[0]
            result = 1
        elif ratio <= 50:
            url += template[1]
            result = 2
        else:
            url += template[2]
            result = 4

        url += '</ul>'
        url += html_lis
        return {
                "name": "异地通话记录",
                "result": (('%.2f' % ratio) if ratio else ('%.1f' % ratio)) + "%",
                "accord": url,
                "assess": result
        }

    def collection_list(self, data_r, flag):
        """ 疑似催收 """
        data = data_r.copy()
        if not data and flag is False:

            return {
                "name": "疑似催收号码",
                "result": '',
                "accord": '',
                "assess": 6,
            }
        try:
            cuishou_list = data
            sum_ = len(cuishou_list)
            if sum_:
                ll = "<br><ul><li>" + "</li><li>".join(cuishou_list) + "</li></ul>"
            else:
                ll = ""
            level = 1
            if 3 <= sum_ <= 5:
                level = 2
            elif sum_ > 5:
                level = 4
            temp = {
                1: "近3个月未发现连续号段疑似催收号码{0}",
                2: "近3个月与3~5个连续号段号码有联系，风险等级关注{0}",
                4: "近3个月与5个以上连续号段号码有联系，风险等级高{0}"
            }
            return {
                "name": "疑似催收号码",
                "accord": temp[level].format(ll),
                "assess": level,
                "result": 0 if sum_ < 3 else sum_
            }
        except:
            return {
                "name": "疑似催收号码",
                "accord": "近3个月未发现连续号段疑似催收号码",
                "assess": 1,
                "result": 0
            }

    def contact_tel_risk(self, data_r, flag):
        """ 联系人电商平台高危客户 """
        template0 = '检测到电商平台高危客户：</br>'
        template1 = '<li>{0}主动呼叫次数{1}次，最近通话时间{2}；</li>'
        template = '未检测到电商平台高危客户'
        deceit_risk = data_r.get('deceitRisk', {}) or {}
        tel_risk_list = deceit_risk.get('telRiskList', []) or []
        tel_risk = len(tel_risk_list)
        call_records_info = data_r.get('callRecordsInfo', []) or []
        if not tel_risk_list and flag is False:
            return {
                "name": "联系人电商平台高危客户",
                "result": '',
                "accord": '',
                "assess": 6,
            }
        elif not tel_risk_list:
            return {
                "name": "联系人电商平台高危客户",
                "result": 0,
                "accord": template,
                "assess": 1,
            }

        def level_handle(le):
            if le == 0:
                return 1
            elif le < 3:
                return le + 1
            else:
                return 4

        call_records_info_dict = {}
        [call_records_info_dict.update({i['phoneNo']: i}) for i in call_records_info]

        def _time(t):
            try:
                return datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
            except:
                return '2016-01-01 00:00:00'
        accord = [template1.format(i, call_records_info_dict[i]['callTimes'], _time(call_records_info_dict[i]['lastCallTime'])) for i in tel_risk_list if i in call_records_info_dict]
        accord = template0 + "<ul>" + ''.join(accord) + "</ul>"
        return {
            'name': "联系人电商平台高危客户",
            'result': tel_risk,
            'accord': accord,
            'assess': level_handle(tel_risk)
        }

    def contact_xinfo_risk(self, data_r, flag):
        """ 联系人信息台高危客户 """
        template0 = '检测到信息平台高危客户：</br>'
        template1 = '<li>{0}主动呼叫次数{1}次，最近通话时间{2}；</li>'
        template = '未检测到信息平台高危客户'
        deceit_risk = data_r.get('deceitRisk', {}) or {}
        info_risk_list = deceit_risk.get('infoRiskList', []) or []
        info_risk = len(info_risk_list)
        call_records_info = data_r.get('callRecordsInfo', []) or []
        if not info_risk_list and flag is False:

            return {
                "name": "联系人信息平台高危客户",
                "result": '',
                "accord": '',
                "assess": 6,
            }

        elif not info_risk_list:
            return {
                "name": "联系人信息平台高危客户",
                "result": 0,
                "accord": template,
                "assess": 1,
            }

        def level_handle(le):
            if le == 0:
                return 1
            elif le < 3:
                return le + 1
            else:
                return 4

        call_records_info_dict = {}
        [call_records_info_dict.update({i['phoneNo']: i}) for i in call_records_info]

        def _time(t):
            try:
                return datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
            except:
                return '2016-01-01 00:00:00'
        accord = [template1.format(i, call_records_info_dict[i]['callTimes'], _time(call_records_info_dict[i]['lastCallTime'])) for i in info_risk_list if i in call_records_info_dict]
        accord = template0 + "<ul>" + ''.join(accord) + "</ul>"
        return {
            'name': "联系人信息平台高危客户",
            'result': info_risk,
            'accord': accord,
            'assess': level_handle(info_risk)
        }

    def contact_social_risk(self, data_r, flag):
        """ 联系人社交平台高危客户 """
        template0 = '检测到社交平台高危客户'
        template1 = '<li>{0}主动呼叫次数{1}次，最近通话时间{2}；</li>'
        template = '未检测到社交平台高危客户'
        deceit_risk = data_r.get('deceitRisk', {}) or {}
        social_risk_list = deceit_risk.get('socialRiskList', []) or []
        social_risk = len(social_risk_list)
        call_records_info = data_r.get('callRecordsInfo', []) or []

        if not social_risk_list and flag is False:

            return {
                "name": "联系人社交平台高危客户",
                "result": '',
                "accord": '',
                "assess": 6,
            }

        elif not social_risk_list:
            return {
                "name": "联系人社交平台高危客户",
                "result": 0,
                "accord": template,
                "assess": 1,
            }

        def level_handle(le):
            if le == 0:
                return 1
            elif le < 3:
                return le + 1
            else:
                return 4

        call_records_info_dict = {}
        [call_records_info_dict.update({i['phoneNo']: i}) for i in call_records_info]

        def _time(t):
            try:
                return datetime.datetime.fromtimestamp(t).strftime('%Y-%m-%d %H:%M:%S')
            except:
                return '2016-01-01 00:00:00'
        accord = [template1.format(i, call_records_info_dict[i]['callTimes'], _time(call_records_info_dict[i]['lastCallTime'])) for i in social_risk_list if i in call_records_info_dict]
        accord = template0 + "<ul>" + ''.join(accord) + "</ul>"
        return {
            'name': "联系人社交平台高危客户",
            'result': social_risk,
            'accord': accord,
            'assess': level_handle(social_risk)
        }

    def risk_phone_analyze(self, data_r, flag):
        """ 风险号码标识记录分析 """
        risk_nums = ('贷款中介', '信用卡', '律师电话', '法院电话', '110电话', '澳门电话')
        data = self.data.get("callRecordsInfo", []).copy()
        # flag = True
        # if not data:
        #     flag = False

        ret = [0] * len(risk_nums)
        for i in range(len(ret)):
            ret[i] = {
                'callTimes': 0 if flag is True else '',
                'calledTimes': 0 if flag is True else '',
                "connCallTime": 0 if flag is True else '',
                "connCalledTimes": 0 if flag is True else '',
                "connTimes": 0 if flag is True else '',
                'lastCallTime': 0 if flag is True else '',
                "phoneSum": 0 if flag is True else '',
                'tag': risk_nums[i] if i != 1 else "信用卡中心",
            }
        if flag is False:
            for i in range(len(ret)):
                ret[i]['lastCallTime'] = ''
            return ret

        for ele in data:
            remark = ele.get('remark', '')
            # 没有标记的直接跳过
            if (not remark) or (remark not in risk_nums):
                continue

            sb_index = risk_nums.index(remark)

            # ret[sb_index] = {
            #     'callTimes': ret[remark].get('callTimes', 0),
            #     'calledTimes': 0,
            #     "connCallTime": 0,
            #     "connCalledTimes": 0,
            #     "connTimes": 0,
            #     'lastCallTime': 0,
            #     "phoneSum": 0
            # }

            ret[sb_index]['callTimes'] += int(ele.get('callTimes', 0))
            ret[sb_index]['calledTimes'] += int(ele.get('calledTimes', 0))
            ret[sb_index]['connCallTime'] += int(ele.get('connCallTime', 0))
            ret[sb_index]['connCalledTimes'] += int(ele.get('connCalledTimes', 0))
            ret[sb_index]['connTimes'] += int(ele.get('connTimes', 0))
            if ele.get('lastCallTime') > int(ret[sb_index]['lastCallTime']):
                ret[sb_index]['lastCallTime'] = int(ele.get('lastCallTime'))
            ret[sb_index]['phoneSum'] += 1

        result = []

        for ele in ret:
            result.append({
                "callTimes": ele.get("connTimes", 0),  # 通话次数
                "calledMinute": second_to_minute(int(ele.get("connCalledTime", 0))), # 被叫时间
                "calledTimes": ele.get("calledTimes", 0), # 被叫次数
                "callingMinute": second_to_minute(int(ele.get("connCallTime", 0))), # 主叫时间
                "callingTimes": ele.get("callTimes"), # 主叫次数
                "lastConnTime": cao_time_time_to_str(int(ele.get("lastCallTime", 0))),
                "tag": ele.get("tag", ''),
                "telNum": ele.get("phoneSum", 0), # 号码数量
            })

        return result

    def important_conn_analysis(self, data_r, relation=None, work=None, school=None, flag=True):
        """ 重要联系人分析 """
        if data_r is None:
            data_r = {}
        data = data_r.copy()
        data = data.get("callRecordsInfo", []).copy()

        def get_relation_phone(ph, d):
            if d is None:
                return False
            if ph == d['phone']:
                return True
            return False

        def num_handle(d):
            try:
                return int(d)
            except:
                return 0

        def add_ele(list_, v2):
            phone_n = v2.get("phoneNo", '')
            flag = False
            indexs = []
            # 如果几个联系人号码一样， 那么后面那个起作用
            if get_relation_phone(phone_n, relation):
                indexs.append(0)
                flag = True
            if get_relation_phone(phone_n, work):
                indexs.append(1)
                flag = True
            if get_relation_phone(phone_n, school):
                indexs.append(2)
                flag = True

            if flag is True:
                for index in indexs:
                    v1 = list_[index]
                    count = num_handle(v2.get('callTimes')) + num_handle(v2.get("calledTimes"))
                    v1["callTimes"] = count
                    v1["ratio"] = ""
                    v1["address"] = v2.get("belongArea", "")
                    v1["callingTimes"] = v2.get("callTimes", 0)
                    v1["calledTimes"] = v2.get("calledTimes", 0)
                    v1["coverageCallMinute"] = '%.2f' % float(two_num(second_to_minute(num_handle(v2.get("connCallTime", 0)) + num_handle(v2.get("connCalledTime", 0))) / count))

        def my_list(iter_l):
            l = []
            tmp_d = {
                "type": "",
                "relation": '',
                "name": '',
                "telphone": '',
                "callTimes": 0,
                # "ratio": "",
                "address": '',
                "callingTimes": 0,
                "calledTimes": 0,
                "coverageCallMinute": '0.00'
            }

            def map_f(key):
                nonlocal tmp_d
                d = tmp_d.copy()
                if key is None:
                    return d
                d.update({
                    "type": key['type'],
                    'relation': key['relation'],
                    'name': key['name'],
                    'telphone': key['phone']
                })
                return d
            l = list(map(map_f, iter_l))
            return l

        sum_ = 0

        def map_func(old, ele):
            # nonlocal sum_, r, w, s

            sum_, tuple_import = old[0], old[1]

            sum_ += num_handle(ele.get("connTimes"))
            # if relation.get("")
            # if get_relation_phone(phone_n, relation) or get_relation_phone(phone_n, work) or \
            #         get_relation_phone(phone_n, school):
            # for index, _ in enumerate(tuple_import):
            add_ele(tuple_import, ele)
            return sum_, tuple_import

        init_param = my_list([relation, work, school])
        from functools import reduce
        sum_, ret = list(reduce(map_func, data, (0, init_param)))

        for i in range(len(ret)):
            x = ret[i]
            ret[i]['ratio'] = '%.2f' % two_num(num_handle(x.get('callTimes', 0))*100 / sum_) if sum_ != 0 else 0
        ret = list(filter(lambda x: x['telphone'], ret))
        return ret

    def important_conn_chart(self, data, rel, work, school):
        """ 中套联系人趋势分析 """
        d = (rel, work, school)
        today_ = data.get("baseInfo", {}).get("reportTime", "")
        try:
            today_ = datetime.datetime.strptime(today_, '%Y-%m-%d %H:%M:%S')
        except:
            today_ = datetime.datetime.now()

        ret, today =[], today_
        six_month = {}
        data = data.get("deceitRisk", {}).get("monthCallInfo", {}).get("sixMonth", {}).get("callList", [])

        def time_handle(current_day, index):
            nonlocal six_month

            six_month[current_day.strftime('%Y%m')] = 0
            if index >= 6:
                return
            last_month = datetime.timedelta(days=current_day.day)
            a = current_day - last_month
            time_handle(a, index + 1)

        time_handle(today, 1)
        # time_keys = .keys()
        relation = (six_month.copy(), six_month.copy(), six_month.copy())

        def map_f(ele):
            nonlocal ret, six_month, d, data
            if ele is None:
                return
            index = d.index(ele)
            for record in data:
                # print("\mbudeg : ", record.get("peer_number"), ele.get("phone"))
                if record.get("peer_number", '') == ele.get("phone"):
                    month = record.get('month', '')
                    if month in relation[index]:
                        relation[index][month] += 1

        list(map(map_f, d))

        def map_ret(ele):
            nonlocal d, relation, ret
            index = d.index(ele)
            if ele is None:
                return
            d2 = [{"callTimes": value, 'time': datetime.datetime.strptime(key, '%Y%m')
              } for key, value in relation[index].items()]
            d2 = sorted(d2, key=lambda  x: x['time'])
            ret.append({
                "name": ele.get("type", ''),
                "value": d2
            })
        list(map(map_ret, d))
        return ret

    def connection_top_analyze(self, data_r, top_n=5):
        """ 联系人top分析 """
        data = data_r.copy()
        data = data.get("callRecordsInfo", {}).copy()
        # 倒序
        data = sorted(data, key=lambda x: int(x.get('connTimes', 0)), reverse=True)
        ret, sum_ = [], 0

        for i in range(len(data)):
            sum_ += int(data[i].get("connTimes"))
            if i >= top_n:
                continue

            ret.append({
                "address": data[i].get("belongArea", ''),
                "callTimes": int(data[i].get("connTimes", 0)),
                "calledTimes": data[i].get("calledTimes", 0),
                "callingTimes": data[i].get("callTimes", 0),
                'tag': data[i]['remark'],
                "coverageCallTime": two_num((second_to_minute(int(data[i].get("connCallTime", 0)) + int(data[i].get("connCalledTime", 0)))) / int(data[i].get("connTimes", 0))),
                "ratio": "",
                "label": data[i].get("label", "--"),
                "telphone": data[i].get("phoneNo", '')
            })
        for i in range(top_n):
            if i >= len(data):
                break
            if sum_ != 0:
                ret[i]['ratio'] ='%.2f' % two_num(int(ret[i]['callTimes'])*100 / sum_)
            else:
                ret[i]['ratio'] = 0

        return ret

    def phone_region_top5(self, data_r, top_n=5):
        """ 本人通话区域top5分析 """
        data = data_r.get('callPlaceInfo', {}).copy()
        data = sorted(data, key=lambda x: int(x['dayStop']), reverse=True)
        ret, sum_ = [], 0

        def time_str_handler(d):
            if isinstance(d, str) and d[0:4] == '1970':
                return ''

            # if isinstance(d, str) and len(d) == 8:
            #     return d[0:4] + '-' +d[4:6] + '-' + d[6:]
            return cao_time_time_to_str(d)
            # return d

        for index in range(top_n):
            if index >= len(data):
                break
            ele = data[index]
            sum_ += ele.get('connTimes', 0)
            if index > top_n:
                continue

            ret.append({
                "address": ele.get("commType", ''),
                "callTimes": ele.get("connTimes", ''),
                'days': ele.get("dayStop", ''),
                "firstTime": time_str_handler( int(ele.get("firstCallTime", 0)) ) or '',
                "lastTime": time_str_handler( int(ele.get("lastCallTime", 0)) ) or '',
                "ratio": ''
            })
        for i in range(top_n):
            if i >= len(data):
                break
            if sum_ != 0:
                ret[i]['ratio'] = '%.2f' % two_num(int(ret[i]['callTimes'])*100 / sum_)
            else:
                ret[i]['ratio'] = 0

        return ret

    def contract_area(self, data_r, top_n=5):
        """ 联系人区域top5分析 """
        if data_r is None:
            data_r = {}
        data = data_r.get('contactsPlaceInfo', {}).copy()
        data = sorted(data, key=lambda x: int(x.get("phoneNum", 0)), reverse=True)
        ret, sum = [], 0

        for index in range(top_n):
            if index >= len(data):
                break
            ele = data[index]
            sum += int(ele.get('phoneNum', 0))
            if index > top_n:
                continue

            ret.append({
                "address": ele.get("commPlac", ''),
                "calledSecond": '%.2f' % second_to_minute(int(ele.get("calledTime", 0))),
                "calledTimes": ele.get("calledTimes", 0),
                "callingSecond": '%.2f' % second_to_minute(int(ele.get("callTime", 0))),
                "callingTimes": ele.get("callTimes", 0),
                "ratio": '',
                "telNum": ele.get("phoneNum")
            })
        for i in range(top_n):
            if  i >= len(data):
                break
            ret[i]['ratio'] = '%.2f' % two_num(int(ret[i]['telNum'])*100 / sum if sum != 0 else 0)
        return ret

    def conversation_slot(self, data_r):
        """ 通话时段 """
        data = data_r.get("callDuration", {}).copy()
        data = sorted(data, key=lambda x: int(x.get("startTime", 0)))

        def encode_(d):
            d = int(d)
            if 530 <= d <900:
                return 0
            elif 900 <= d < 1130:
                return 1
            elif 1130 <= d < 1330:
                return 2
            elif 1330 <= d < 1730:
                return 3
            elif 1730 <= d < 2330:
                return 4
            elif 130 <= d < 530:
                return 6
            else:
                return 5
        d = {
            0: 0,
            1: 0,
            2: 0,
            3: 0,
            4: 0,
            5: 0,
            6: 0}
        duation = ['05:30-09:00', '09:00-11:30', '11:30-13:30', '13:30-17:30', '17:30-23:30', '23:30-01:30', '01:30-05:30']
        ret, sum_ = [], 0

        def map_f(x):
            nonlocal sum_
            n = encode_(x['connTime'])
            d[n] += int(x['connTimes'])
            sum_ += int(x['connTimes'])

        list(map(map_f, data))

        for i in range(7):
            ele = {
                'ratio': '%.2f' % two_num(d[i] * 100 / sum_ if sum_ != 0 else 0),
                'contactTimes': d[i],
                'time': duation[i]
            }
            ret.append(ele)
        return ret

    def average_consume(self, data):
        """ 计算每个月平均消费 """
        if not isinstance(data, list):
            return ''
        sum_, count = 0, 0

        def money_unit_trans(d, rate=1, type_=0):
            try:
                ret = float(d) / rate
                if type_ != 0:
                    ret = float('%.2f' % ret)
                return ret
            except:
                return 0

        for i in data:
            count += 1
            sum_ += money_unit_trans(i.get("billFee", 0))

        if count == 0:
            return ''

        sum_ = sum_ / count
        sum_ = money_unit_trans(sum_, type_=1)
        sum_ = two_num(sum_/100)
        return sum_

    # 用户异常行为分析
    def user_exception_handler(self, data_r, flag, token=None, now=None):
        data = data_r.copy()
        if not data:
            if token:
                word = '查询中'
            else:
                word = '未查询'
            ret = [
                {
                    "name": "手机长时间静默情况",
                    "result": '',
                    "accord": word,
                    "assess": 6,
                },
                {
                    "name": "夜间通话占比",
                    "result": '',
                    "accord": word,
                    "assess": 6,
                },
                {
                    "name": "联系人数量",
                    "result": '',
                    "accord": word,
                    "assess": 6,
                },
                {
                    "name": "互通电话数量",
                    "result": '',
                    "accord": word,
                    "assess": 6,
                },
                {
                    "name": "异地通话记录",
                    "result": '',
                    "accord": word,
                    "assess": 6,
                },
                {
                    "name": "疑似催收号码",
                    "result": '',
                    "accord": word,
                    "assess": 6,
                },
                {
                    "name": "联系人电商平台高危客户",
                    "result": '',
                    "accord": word,
                    "assess": 6,
                },
                {
                    "name": "联系人信息平台高危客户",
                    "result": '',
                    "accord": word,
                    "assess": 6,
                },
                {
                    "name": "联系人社交平台高危客户",
                    "result": '',
                    "accord": word,
                    "assess": 6,
                }

            ]
            return ret

        ret = []
        ret.append(self.long_time_slicense(data.get('deceitRisk', {}).get("silenceInfo", []), flag, now))
        ret.append(self.contract_num(data.get('deceitRisk', {}).get("monthCallInfo", {}), flag))
        ret.append(self.contact_phone_num(data.get('deceitRisk', {}).get("monthCallInfo", {}), flag))
        ret.append(self.night_phone(data.get('deceitRisk', {}).get('callDuration', []), flag))
        # ret.append(self.remote_phone_rate(data.get('deceitRisk', {}).get("monthCallInfo", {}), flag))
        ret.append(self.remote_phone_rate(data, flag))
        ret.append(
            self.collection_list(data.get("deceitRisk", {}).get("monthCallInfo", {}
            ).get("threeMonth", {}).get("collectionList", []), flag))
        # ret.append(self.contact_tel_risk( data, flag))
        # ret.append(self.contact_xinfo_risk(data, flag))
        # ret.append(self.contact_social_risk(data, flag))
        return ret

    @classmethod
    def contract_record(cls, data_r,  s_type, page, count, apply_number=None):
        """ 通话记录分析 """
        if data_r is None:
            data_r = []
        data = data_r.copy()
        def key_f(d):
            nonlocal s_type
            if s_type == 1 and (not (d['remark'] or d.get('label'))):
                return False
            return True
        total_remark = None
        if s_type == 0:
            total_remark = 0
            for i in data:
                if i['remark'] or i.get('label'):
                    total_remark += 1

        data = sorted(filter(key_f, data), key=lambda x: int(x.get("connTimes", 0)), reverse=True)

        total, ret = len(data), []
        if total_remark is None:
            total_remark = total

        if count == -1:
            start, end = 0, total
        else:
            start, end = (page - 1) * count, page * count

        def _ret(i):

            return {
                "belongArea": i.get('belongArea', ''),
                "callTimes": i.get('callTimes', ''),
                "calledTimes": i.get("calledTimes", ''),
                "connTime": two_num(second_to_minute(int(i.get('connCallTime', 0))) + second_to_minute(int(i.get('connCalledTime', 0)))),
                "connTimes": i.get("connTimes", ''),
                "identifyInfo": i.get("remark", ''),
                "label": i.get("label", "--"),
                "phoneNo": i.get("phoneNo")
            }

        ret = [_ret(i) for i in data]
        res = {
            'total': total,
            'callDetail': ret,
            'totalRemark': total_remark
        }
        if apply_number:
            save_to_cache(apply_number, res, 'call_record_view')

        res['callDetail'] = res['callDetail'][start: end]

        return res

    @classmethod
    def sms_record_analyze(self, data_r,  s_type, page, count, apply_number=None):
        """ 短信记录分析 """
        data = data_r.copy()

        def key_f(d):
            nonlocal s_type
            # if s_type == 1 and not d['remark']:
            if s_type == 1 and (not (d['remark'] or d.get('label'))):
                return False
            return True

        total_remark = None
        if s_type == 0:
            total_remark = 0
            for i in data:
                if i['remark'] or i.get('label'):
                    total_remark += 1

        data = sorted(filter(key_f, data), key=lambda x: int(x.get("totalSmsNumber", 0)), reverse=True)
        total, ret = len(data), []

        if total_remark is None:
            total_remark = total
        if count == -1:
            start, end = 0, total
        else:
            start, end = (page - 1) * count, page * count

        def _detail(i):

            return {
                "belongArea": i.get('belongArea', ''),
                "identifyInfo": i.get("remark", ''),
                "phoneNo": i.get("phoneNo"),
                "label": i.get("label", '--'),
                "totalSmsNumber": i.get("totalSmsNumber", '')
            }

        ret = [_detail(i) for i in data]

        res = {
            'total': total,
            'msgDetail': ret,
            "totalRemark": total_remark
        }

        if apply_number:
            save_to_cache(apply_number, res, 'msg_record_view')

        res['msgDetail'] = res['msgDetail'][start: end]

        return res

    def credit_risk_calculate(self, data=None, online_data=None, now=None, source='mashang'):
        """ 贷前风险评估 失联风险 """

        assess = {
            RiskEvaluation.O: 0,
            RiskEvaluation.N: 0,
            RiskEvaluation.S: 0,
            RiskEvaluation.M: 0,
            RiskEvaluation.L: 0,
            RiskEvaluation.XL: 0,
        }
        ret_lis = []

        if data is None:
            data = self.data
        if not data:
            assess[RiskEvaluation.N] += 1
            ret_lis.append('未进行运营商授权，无法判断')
            return {
                'assess': assess,
                'result': ret_lis,
            }
        result = {
            1: 0, # 低
            2: 0,
            3: 0,
            4: 0}
        # 手机在网时长
        phone_register_t = data.get("phoneInfo", {}).get("inNetDate", "6月")
        has_time = data.get("phoneInfo", {}).get("netAge", "6月")
        # has_time = data.get("")

        ###############################################
        # 这是从运营商数据获取在网时长的版本, 现在不要了
        ###############################################
        # def long_time_handler(m):
        #     d = m
        #     all_nums_char = [str(i) for i in range(0, 11)]
        #     other_char = set()

        #     for i in d:
        #         if i not in all_nums_char:
        #             other_char.add(i)
        #     for i in other_char:
        #         d = d.replace(i, ';')
        #     d = d.split(';')
        #     d = list(filter(lambda x: x, d))
        #     if len(d) == 0:
        #         return True
        #     elif len(d) == 1:
        #         if '月' in m and int(d[0]) > 3:
        #             return True
        #         if '年' in m and int(d[0]) > 0:
        #             return True
        #         return False
        #     elif len(d) >= 2:
        #         if int(d[0]) > 0 or int(d[1]) >= 3:
        #             return True
        #     return False

        ################################
        # 这是从查询的在网时长接口的版本
        ################################
        def long_time_handler_mashang(m):

            from app.credit.pipeline import mashang_online
            parsed_online_data = mashang_online(online_data)['timeRange']

            # 没查在网时长接口默认风险低
            if not online_data:
                return True
            p1 = re.compile('(\d+)-(\d+)个月')
            p2 = re.compile('(\d+)个月以上')
            r1 = p1.match(parsed_online_data)
            r2 = p2.match(parsed_online_data)
            if r1:
                online_int = int(r1.groups()[1])
            elif r2:
                online_int = int(r2.groups()[0])
            else:
                online_int = 1000

            if online_int < 3:
                return False

            return True

        ################################
        # 这是查询中诚信在网时长的版本
        ################################
        def long_time_handler_zhongchengxin(m):

            from app.credit.pipeline import handle_operator_phonetime
            parsed_online_data = handle_operator_phonetime(online_data)['timeRange']

            # 没查在网时长接口默认风险低
            if not online_data:
                return True
            p1 = re.compile('(\d+)-(\d+)个月')
            p2 = re.compile('(\d+)个月以上')
            r1 = p1.match(parsed_online_data)
            r2 = p2.match(parsed_online_data)
            if r1:
                online_int = int(r1.groups()[1])
            elif r2:
                online_int = int(r2.groups()[0])
            else:
                online_int = 1000

            if online_int < 3:
                return False

            return True

        if source == 'mashang':
            if long_time_handler_mashang(has_time) is False:
                assess[RiskEvaluation.M] += 1
                ret_lis.append('手机号使用时间低于正常值范围')
                result[2] += 1
        elif source == 'zhongchengxin':
            if long_time_handler_zhongchengxin(has_time) is False:
                assess[RiskEvaluation.M] += 1
                ret_lis.append('手机号使用时间低于正常值范围')
                result[2] += 1

        today_t = datetime.datetime.now()
        today_str = '%d%02d%02d'.format(today_t.year, today_t.month, today_t.day)
        if phone_register_t == today_str:
            assess[RiskEvaluation.L] += 1
            ret_lis.append('手机号为申请日当天注册，借款人失联风险高')
            result[4] += 1
        # 联系人数量
        obj = self.contract_num(data.get('deceitRisk', {}).get("monthCallInfo", {}), True)

        if (obj.get("result", 0) or 0) < 10:
            assess[RiskEvaluation.M] += 1
            ret_lis.append('近6个月联系人数量{}人，低于正常值范围</li>'.format(obj.get("result", 0)))
            result[2] += 1

        obj = self.contact_phone_num(data.get('deceitRisk', {}).get("monthCallInfo", {}), True)

        if (obj.get("result", 0) or 0) <= 5:
            assess[RiskEvaluation.M] += 1
            ret_lis.append("近6个月互通电话数量{}个，低于正常值范围".format(obj.get("result", 0)))
            result[2] += 1

        obj = self.long_time_slicense(data.get('deceitRisk', {}).get("silenceInfo", []), False, now)
        max_result = obj.get('max_result', 0) or 0

        if 10 < max_result < 30:
            assess[RiskEvaluation.M] += 1
            ret_lis.append("手机号连续静默时间{}天，超过正常值范围".format(max_result))
            result[2] += 1
        elif max_result >= 30:
            assess[RiskEvaluation.L] += 1
            ret_lis.append("手机号连续静默时间{}天，静默时间过长，借款人失联风险高".format(max_result))
            result[4] += 1

        level = 1
        li_ = list(range(1, 4))
        li_.reverse()
        for i in li_:
            if result[i] > 0:
                level = i
                break

        return {
            'assess': assess,
            'result': ret_lis,
        }


if __name__ == '__main__':

    data = None
    with open("data.json", 'r') as fp:
        data = fp.read()
    import json
    data = json.loads(data)
    d = UserExceptionAction(data.get('data'))
    ret = d.credit_risk_calculate(data.get('data'))

