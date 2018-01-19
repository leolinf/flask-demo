# -*- coding: utf-8 -*-

import requests
import time

from flask import g, jsonify, current_app
from sqlalchemy.orm import scoped_session

from app import make_response, Session, Config
from app.bases import BaseResource
from .parsers import monitor_list, add_monitor, switch_monitor
from .managers import MonitorManager
from app.models import Uploading
from app.constants import Code
from app.core.logger import project_logger
from app.user.function import  current_user, login_required


class MonitorListView(BaseResource):

    @login_required
    def post(self):
        """贷中监控列表查询列表"""

        req = monitor_list.parse_args()

        count = req['count']
        page = req['page']
        period = req['period']
        phone = req['phone']
        startTime = req['startTime']
        endTime = req['endTime']
        isUnusual = req['isUnusual']
        exponentSort = req['exponentSort']
        monitorSort = req['monitorSort']
        unusalSort = req['unusalSort']
        exponentNum = req['exponentNum']
        monitorStartTime = req['monitorStartTime']
        monitorEndTime = req['monitorEndTime']
        monitorPeriod = req['monitorPeriod']
        status = req['status']

        session = scoped_session(Session)
        monitor_manager = MonitorManager(session)

        monitors, total = monitor_manager.get_list(
            current_user.company_id,
            offset=(page - 1) * count,
            limit=count,
            period=period,
            phone=phone,
            startTime=startTime,
            endTime=endTime,
            isUnusual=isUnusual,
            exponentNum=exponentNum,
            monitorStartTime=monitorStartTime,
            monitorEndTime=monitorEndTime,
            monitorPeriod=monitorPeriod,
            status=status,
            exponentSort=exponentSort,
            monitorSort=monitorSort,
            unusalSort=unusalSort,
        )

        uploading = Uploading.objects(
            user_id=current_user.id,
            upload_type='B',
        ).first()

        if not uploading:
            total_import = 0
            duplicate = 0
            doing = 0
            success = 0
        else:
            total_import = uploading.total
            duplicate = uploading.duplicate
            doing = uploading.doing
            success = uploading.success

        session.remove()

        return make_response({
            'antiFraudList': monitors,
            'total': total,
            'totalImport': total_import,
            'duplicate': duplicate,
            'doing': doing,
            'success': success,
        })


class AddMonitor(BaseResource):

    @login_required
    def get(self):
        """加入贷中监控"""

        req = add_monitor.parse_args()
        search_id = req['id']

        session = scoped_session(Session)
        monitor_manager = MonitorManager(session)
        status = monitor_manager.add_search_to_monitor(search_id, current_user)
        session.remove()

        return make_response(status=status)


class SwitchMonitor(BaseResource):

    @login_required
    def get(self):
        """停止或重启贷后监控"""

        req = switch_monitor.parse_args()
        search_id = req['id']
        status = req['status']

        session = scoped_session(Session)
        monitor_manager = MonitorManager(session)
        status = monitor_manager.switch_monitor(search_id, status)

        session.remove()
        return make_response(status=status)


class NewMonitorListView(BaseResource):

    @login_required
    def post(self):

        req = monitor_list.parse_args()

        data = req.copy()
        data['company_id'] = current_user.company_id

        url = Config.JAVA_HOST + '/api/monitor_search_list'

        try:
            start = time.time()
            r = requests.post(url, json=data, timeout=5)
            project_logger.info('java透传耗时{0}秒'.format(time.time() - start))
        except Exception as e:
            project_logger.error(e)
            res = {
                'code': Code.SYSTEM_ERROR,
            }
            return jsonify(res)

        try:
            res = r.json()
        except Exception as e:
            project_logger.error('status_code: {0}'.format(r.status_code))
            project_logger.error(r.text)
            project_logger.error(e)
            res = {
                'code': Code.SYSTEM_ERROR,
            }
            return jsonify(res)

        uploading = Uploading.objects(
            user_id=current_user.id,
            upload_type='B',
        ).first()

        if not uploading:
            total_import = 0
            duplicate = 0
            doing = 0
            success = 0
        else:
            total_import = uploading.total
            duplicate = uploading.duplicate
            doing = uploading.doing
            success = uploading.success

        if isinstance(res, dict) and 'data' in res and isinstance(res['data'], dict):
            res['data'].update({
                'totalImport': total_import,
                'duplicate': duplicate,
                'doing': doing,
                'success': success,
            })

        return jsonify(res)
