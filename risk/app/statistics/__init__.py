# -*- coding: utf-8 -*-

from flask import Blueprint
from flask_restful import Api

from .views import TodayStatView, MonitorStatView, MonitorCumulateView, VerifyStatView, VerifyCumulateStatView, ReviewStatView, ReviewCumulateStatView


statistics = Blueprint('statistics', __name__)
statistics_wrap = Api(statistics)

statistics_wrap.add_resource(TodayStatView, '/api/statistics/')
statistics_wrap.add_resource(MonitorStatView, '/api/monitor_statistics/')
statistics_wrap.add_resource(MonitorCumulateView, '/api/monitor_statistics_cumulative/')
statistics_wrap.add_resource(VerifyStatView, '/api/into_statistics/')
statistics_wrap.add_resource(VerifyCumulateStatView, '/api/into_statistics_cumulative/')
statistics_wrap.add_resource(ReviewStatView, '/api/approve_statistics/')
statistics_wrap.add_resource(ReviewCumulateStatView, '/api/approve_statistics_cumulative/')
