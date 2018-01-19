# -*- coding: utf-8 -*-

from flask_restful import reqparse
from werkzeug.datastructures import FileStorage
from app.core.validators import phone, name, idnum


monitor_list = reqparse.RequestParser(bundle_errors=True)
monitor_list.add_argument('count', location='json', type=int, default=10)
monitor_list.add_argument('page', location='json', type=int, default=1)
monitor_list.add_argument('isUnusual', location='json', type=bool)
monitor_list.add_argument('period', location='json', type=str, choices=('all', 'today', 'week', 'month'))
monitor_list.add_argument('phone', location='json', type=str)
monitor_list.add_argument('startTime', location='json', type=int)
monitor_list.add_argument('endTime', location='json', type=int)
monitor_list.add_argument('exponentSort', location='json', type=int, choices=(1, 2, 3))
monitor_list.add_argument('monitorSort', location='json', type=int, choices=(1, 2, 3))
monitor_list.add_argument('unusalSort', location='json', type=int, choices=(1, 2, 3))
monitor_list.add_argument('exponentNum', location='json', type=str)
monitor_list.add_argument('monitorStartTime', location='json', type=int)
monitor_list.add_argument('monitorEndTime', location='json', type=int)
monitor_list.add_argument('monitorPeriod', location='json', type=str, choices=('all', 'today', 'week', 'month'))
monitor_list.add_argument('status', location='json', type=int, choices=(-1, 0, 1))
monitor_list.add_argument('exceptionList', location='json', type=str)
monitor_list.add_argument('userId', location='args', type=int)

add_monitor = reqparse.RequestParser(bundle_errors=True)
add_monitor.add_argument('id', location='args', type=int, required=True)
add_monitor.add_argument('userId', location='args', type=int)

switch_monitor = reqparse.RequestParser(bundle_errors=True)
switch_monitor.add_argument('id', location='args', type=int, required=True)
switch_monitor.add_argument('status', location='args', type=int, required=True, choices=(1, 0))
switch_monitor.add_argument('userId', location='args', type=int)

monitor_add_parser= reqparse.RequestParser(bundle_errors=True)
monitor_add_parser.add_argument('id', location='args', type=str, required=True)
monitor_add_parser.add_argument('userId', location='args', type=int)

monitor_single_parser= reqparse.RequestParser(bundle_errors=True)
monitor_single_parser.add_argument('id', location='args', type=str, required=True)
monitor_single_parser.add_argument('userId', location='args', type=int)


import_search_parser = reqparse.RequestParser(bundle_errors=True)
import_search_parser.add_argument('searchData', location='files', type=FileStorage, required=True)
import_search_parser.add_argument('userId', location='args', type=int)

monitor_multi_parser = reqparse.RequestParser(bundle_errors=True)
monitor_multi_parser.add_argument('id', location='args', required=True, type=str)
monitor_multi_parser.add_argument('userId', location='args', type=int)

monitor_search = reqparse.RequestParser(bundle_errors=True)
monitor_search.add_argument('idNum', location='json', type=idnum)
monitor_search.add_argument('name', location='json', type=name)
monitor_search.add_argument('phone', location='json', type=phone, required=True)
monitor_search.add_argument('userId', location='args', type=int)
