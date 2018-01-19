# -*- coding: utf-8 -*-

import datetime
import operator
from itertools import accumulate

from flask_restful import Resource

from ..models import SingleSearch, MonitorSearch as Monitor
from ..constants import ApproveStatus, MonitorStatus, SearchStatus
from .parsers import cumulate_stat
from ..core.functions import make_response, somedate2timestamp
from ..core.utils import get_monitor_cumulate, get_credit_cumulate, get_review_cumulate

from app.user.function import login_required, current_user


class TodayStatView(Resource):

    @login_required
    def get(self, *args, **kwargs):
        """今日统计"""

        yesterday = datetime.date.today()
        today = yesterday + datetime.timedelta(days=1)

        searches = SingleSearch.objects(
            create_time__gte=yesterday,
            create_time__lt=today,
            company_id=str(current_user.company_id),
            status__ne=SearchStatus.NO,
        ).all()

        today_search = searches.count()
        today_rule = searches.filter(is_break_rule=1).count()

        today_break = Monitor.objects(
            last_break_time__gte=yesterday,
            last_break_time__lt=today,
            company_id=current_user.company_id,
            break_num__gt=0,
            status__ne=MonitorStatus.DOING,
        ).count()

        today_monitor = Monitor.objects(
            company_id=current_user.company_id,
            status__ne=MonitorStatus.DOING,
        ).count()

        search = SingleSearch.objects(
            approve_time__gte=yesterday,
            approve_time__lt=today,
            company_id=str(current_user.company_id),
            approve_status__in=[ApproveStatus.PASS, ApproveStatus.DENY],
        ).all()

        today_approve = search.filter(approve_status=ApproveStatus.PASS).count()
        today_deny = search.filter(approve_status=ApproveStatus.DENY).count()

        return make_response(
            data={
                'todayInto': today_search,
                'todayRule': today_rule,
                'todayError': today_break,
                'todayMonitor': today_monitor,
                'todayApprove': today_approve,
                'todayDeny': today_deny,
            }
        )


class MonitorCumulateView(Resource):

    @login_required
    def get(self):
        """贷中监控统计累计"""

        total_monitor, total_break = get_monitor_cumulate()

        return make_response(
            data={
                'totalMonitor': total_monitor,
                'totalError': total_break,
            },
        )


class MonitorStatView(Resource):

    @login_required
    def get(self):
        """贷中监控统计"""

        result = Monitor._get_collection().aggregate([
            {
                '$match': {
                    'company_id': current_user.company_id,
                    'status': {'$ne': MonitorStatus.DOING},
                },
            },
            {
                '$group': {
                    '_id': {
                        'year': {'$year': '$create_time'},
                        'month': {'$month': '$create_time'},
                        'day': {'$dayOfMonth': '$create_time'},
                    },
                    'monitorNum': {'$sum': 1},
                    'breakNumList': {'$push': {'$cond': [{'$gt': ['$break_num', 0]}, 1, 0]}},
                }
            },
            {'$unwind': '$breakNumList'},
            {
                '$group': {
                    '_id': '$_id',
                    'monitorNum': {'$first': '$monitorNum'},
                    'errorNum': {'$sum': '$breakNumList'},
                },
            },
            # {'$sort': {'_id.year': 1, '_id.month': 1, '_id.day': 1}},
        ])

        def _func(dic):
            date = dic.pop('_id')
            dic['timestamp'] = somedate2timestamp(date['year'], date['month'], date['day'])
            return dic

        result = list(map(_func, result))
        result.sort(key=operator.itemgetter('timestamp'))

        monitor_nums = [i['monitorNum'] for i in result]
        error_nums = [i['errorNum'] for i in result]
        monitor_num_accumulate = list(accumulate(monitor_nums))
        error_num_accumulate = list(accumulate(error_nums))
        for i in range(len(result)):
            result[i]['monitorNum'] = monitor_num_accumulate[i]
            result[i]['errorNum'] = error_num_accumulate[i]

        return make_response(
            data={
                'timeLineData': result,
            }
        )


class VerifyStatView(Resource):

    @login_required
    def get(self, *args, **kwargs):
        """反欺诈验证统计"""

        result = SingleSearch._get_collection().aggregate([
            {
                '$match': {
                    'company_id': current_user.company_id,
                    'status': {'$ne': SearchStatus.NO},
                },
            },
            {
                '$group': {
                    '_id': {
                        'year': {'$year': '$create_time'},
                        'month': {'$month': '$create_time'},
                        'day': {'$dayOfMonth': '$create_time'},
                    },
                    'intoNum': {'$sum': 1},
                    'errorNum': {'$sum': '$is_break_rule'},
                }
            },
            # {'$sort': {'_id.year': 1, '_id.month': 1, '_id.day': 1}},
        ])

        def _func(dic):
            date = dic.pop('_id')
            dic['timestamp'] = somedate2timestamp(date['year'], date['month'], date['day'])
            return dic

        result = list(map(_func, result))
        result.sort(key=operator.itemgetter('timestamp'))

        return make_response(
            data={
                'timeLineData': result,
            }
        )


class VerifyCumulateStatView(Resource):

    @login_required
    def get(self, *args, **kwargs):
        """反欺诈验证统计累计"""

        req = cumulate_stat.parse_args(strict=True)

        period = req['period']
        start_time = req['startTime']
        end_time = req['endTime']

        total_search, total_break = get_credit_cumulate(start_time, end_time, period)

        return make_response(
            data={
                'totalInto': total_search,
                'totalError': total_break,
            }
        )


class ReviewStatView(Resource):

    @login_required
    def get(self):
        """审批统计"""

        result = SingleSearch._get_collection().aggregate([
            {
                '$match': {
                    'company_id': current_user.company_id,
                    'approve_status': {'$in': [ApproveStatus.PASS, ApproveStatus.DENY]},
                },
            },
            {
                '$project': {
                    'create_time': '$approve_time',
                    'approve': {'$cond': [{'$eq': ['$approve_status',  ApproveStatus.PASS]}, 1, 0]},
                    'deny': {'$cond': [{'$eq': ['$approve_status',  ApproveStatus.DENY]}, 1, 0]},
                },
            },
            {
                '$group': {
                    '_id': {
                        'year': {'$year': '$create_time'},
                        'month': {'$month': '$create_time'},
                        'day': {'$dayOfMonth': '$create_time'},
                    },
                    'approveNum': {'$sum': '$approve'},
                    'denyNum': {'$sum': '$deny'},
                },
            },
        ])

        def _func(dic):
            date = dic.pop('_id')
            dic['timestamp'] = somedate2timestamp(date['year'], date['month'], date['day'])
            return dic

        result = list(map(_func, result))
        result.sort(key=operator.itemgetter('timestamp'))

        return make_response(
            data={
                'timeLineData': result,
            },
        )


class ReviewCumulateStatView(Resource):

    @login_required
    def get(self):
        """审批统计累计"""

        req = cumulate_stat.parse_args(strict=True)

        period = req['period']
        start_time = req['startTime']
        end_time = req['endTime']

        total_into, total_approve = get_review_cumulate(start_time, end_time, period)

        return make_response(
            data={
                'totalInto': total_into,
                'totalApprove': total_approve,
            }
        )
