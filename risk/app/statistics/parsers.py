# -*- coding: utf-8 -*-

from flask_restful import reqparse


cumulate_stat = reqparse.RequestParser(bundle_errors=True)
cumulate_stat.add_argument('period', location='args', type=str, choices=('all', 'week', 'month'))
cumulate_stat.add_argument('startTime', location='args', type=int)
cumulate_stat.add_argument('endTime', location='args', type=int)
cumulate_stat.add_argument('userId', location='args', type=int)
