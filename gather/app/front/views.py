# -*- coding: utf-8 -*-

import datetime
from flask_restful import Resource
from flask import jsonify, render_template
from flask.views import MethodView
from app.config import Config
from app.constant import Code



#class IndexView(MethodView):
#
#    def get(self):
#        return render_template('index.html')

class IndexView(MethodView):

    def get(self):
        return render_template('test.html')
