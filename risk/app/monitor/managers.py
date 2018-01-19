# -*- coding: utf-8 -*-

import datetime
import random

from sqlalchemy import or_, and_

from app.models import Monitor, InputApply, MonitorSearch
from app.core.functions import period2datetime, timestamp2datetime
from app.constants import MonitorStatus, Code
from app.databases import session_scope
from app.config import Config


class MonitorManager(object):

    def __init__(self, session):

        self.session = session
        self.now = datetime.datetime.now()

    def get_list(self, company_id, offset=0, limit=10, period=None, phone=None, startTime=None,
                 endTime=None, isUnusual=None, exponentNum=None, monitorStartTime=None,
                 monitorEndTime=None, monitorPeriod=None, status=None, exponentSort=None, monitorSort=None,
                 unusalSort=None):

        ##########
        # 筛选
        ##########
        match = (
            Monitor.company_id==company_id,
        )

        # 筛选最后违规时间
        if period and period != 'all':
            start_time, end_time = period2datetime(period)
            match += (
                Monitor.last_break_time > start_time,
                Monitor.last_break_time < end_time,
            )
        elif startTime and endTime:
            start = timestamp2datetime(startTime)
            end = timestamp2datetime(endTime)
            match += (
                Monitor.last_break_time > start,
                Monitor.last_break_time < end,
            )

        # 开始监控时间
        if monitorPeriod and monitorPeriod != 'all':
            start_time, end_time = period2datetime(monitorPeriod)
            match += (
                Monitor.create_time > start_time,
                Monitor.create_time < end_time,
            )
        elif monitorStartTime and monitorEndTime:
            start = timestamp2datetime(monitorStartTime)
            end = timestamp2datetime(monitorEndTime)
            match += (
                Monitor.create_time > start,
                Monitor.create_time < end,
            )

        # 是否停止
        if status == 0:
            match += (Monitor.status == MonitorStatus.STOP, )
        elif status == 1:
            match += (Monitor.status == MonitorStatus.DONE, )
        else:
            match += (Monitor.status != MonitorStatus.DOING, )

        # 是否异常
        if isUnusual:
            match += (Monitor.break_num > 0, )

        # 手机号
        if phone:
            match += (or_(
                Monitor.phone.like('%{0}%'.format(phone)),
                Monitor.idcard.like('%{0}%'.format(phone)),
            ),)

        # 异常项数
        if exponentNum and exponentNum != '-1':
            nums = [int(i) for i in exponentNum.split(',') if i.isdigit()]
            match += (
                Monitor.break_num.in_(nums),
            )

        ##########
        # 排序
        ##########
        order = (
        )

        if exponentSort == 1:
            order += (Monitor.break_num, )
        elif exponentSort == 2:
            order += (Monitor.break_num.desc(), )
        elif monitorSort == 1:
            order += (Monitor.create_time, )
        elif monitorSort == 2:
            order += (Monitor.create_time.desc(), )
        elif unusalSort == 1:
            order += (Monitor.last_break_time, )
        elif unusalSort == 2:
            order += (Monitor.last_break_time.desc(), )
        else:
            order += (Monitor.create_time.desc(), )

        monitors = self.session.query(Monitor).filter(and_(*match)).order_by(*order)
        total = monitors.count()
        monitors = monitors.offset(offset).limit(limit).all()

        def _detail(monitor):
            res = {
                'id': str(monitor.id),
                'idCard': monitor.idcard,
                'monitorExponent': monitor.break_num,
                'monitorTime': monitor.create_time,
                'name': monitor.name,
                'newTime': monitor.last_break_time,
                'phone': monitor.phone,
                'status': monitor.status,
            }
            return res

        return list(map(_detail, monitors)), total

    @staticmethod
    def generate_id(session):

        total = session.query(Monitor).count()
        today = datetime.date.today()
        timestamp = int(today.strftime('%Y%m%d'))
        rand = random.randint(100, 999)
        return timestamp * 10 ** 9 + rand * 10 ** 6 + total + 1

    def _create_monitor(self, phone, name, idcard, current_user, input_apply_id):

        monitor_id = self.generate_id(self.session)

        monitor = Monitor(
            id=monitor_id,
            phone=phone,
            name=name,
            idcard=idcard,
            user_id=current_user.id,
            status=MonitorStatus.DOING,
            company_id=current_user.company_id,
            input_apply_id=input_apply_id,
        )
        return monitor

    def add_search_to_monitor(self, search_id, current_user):
        """添加信用报告进入贷后监控"""

        search = self.session.query(InputApply).get(search_id)
        if not search:
            return Code.SINGLE_NOT_EXIST

        phone = search.phone
        name = search.name
        idcard = search.idcard

        user_id = current_user.id
        company_id = current_user.company_id

        monitor = self.session.query(Monitor).filter(and_(
            Monitor.phone==phone,
            Monitor.name==name,
            Monitor.idcard==idcard,
            Monitor.company_id==company_id,
        )).one_or_none()

        if monitor:
            with session_scope(self.session) as session:
                search.monitor_id = monitor.id
                session.add(search)

            return Code.SUCCESS

        with session_scope(self.session) as session:
            monitor = self._create_monitor(phone, name, idcard, current_user, search_id)
            session.add(monitor)
            session.flush()
            monitor_id = monitor.id
            search.monitor_id = monitor_id
            session.add(search)

        monitor = MonitorSearch(
            monitor_id=str(monitor_id),
            name=name,
            phone=phone,
            id_num=idcard,
            status=MonitorStatus.DOING,
            create_time=self.now,
            user_id=user_id,
            company_id=company_id,
        ).save()

        from task.tasks import monitor_single

        monitor_single.apply_async(
            queue=Config.MONITOR_QUEUE,
            args=(
                phone,
                name,
                idcard,
                str(monitor_id),
                True,
            ),
        )

        return Code.SUCCESS

    def switch_monitor(self, monitor_id, status):
        """停止或重启贷后监控"""

        with session_scope(self.session) as session:
            monitor = session.query(Monitor).get(monitor_id)

            if not monitor:
                return Code.MONITOR_NOT_EXIST
            monitor.status = status
            session.add(monitor)

            return Code.SUCCESS
