# -*- encoding: utf-8 -*-

from flask import Blueprint
from flask_restful import Api

from .restful import MonitorListView, AddMonitor, SwitchMonitor, NewMonitorListView

from .views import (
    MonitorDetailView, ApiUnusualView, ApiShopTrendView, UploadView,
    MonitorTemplateView, MonitorMultiView, MonitorSearchView
)


monitor = Blueprint('monitor', __name__)
monitor_wrap = Api(monitor)

# monitor_wrap.add_resource(MonitorListView, '/api/monitor/search_list/')
# monitor_wrap.add_resource(NewMonitorListView, '/api/monitor/search_list/')
monitor_wrap.add_resource(AddMonitor, '/api/add_monitor/')
monitor_wrap.add_resource(SwitchMonitor, '/api/monitor/change_status/')

monitor_wrap.add_resource(MonitorDetailView, '/api/monitor/search_result/')
monitor_wrap.add_resource(ApiUnusualView, '/api/monitor/unusual_trend/')
monitor_wrap.add_resource(ApiShopTrendView, '/api/monitor_shopping_trend/')
monitor_wrap.add_resource(UploadView, '/api/monitor/import_add/')
monitor_wrap.add_resource(MonitorTemplateView, '/api/download/monitor/import/')
monitor_wrap.add_resource(MonitorMultiView, '/api/monitor/multiple_add/')
monitor_wrap.add_resource(MonitorSearchView, '/api/monitor/single_search/')
