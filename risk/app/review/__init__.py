# -*- coding: utf-8 -*-

from flask import Blueprint
from flask_restful import Api

from app.review import views

review = Blueprint('review', __name__)
review_wrap = Api(review)

review_wrap.add_resource(views.CheckLockView, '/api/credit/is_blocked/')
review_wrap.add_resource(views.AddLockView, '/api/credit/block/')
review_wrap.add_resource(views.FirstApproveView, '/api/first_examine/')
review_wrap.add_resource(views.SecondApproveView, '/api/re_examine/')
review_wrap.add_resource(views.ThirdApproveView, '/api/last_examine/')
review_wrap.add_resource(views.ReviewContentView, '/api/check_content/')
review_wrap.add_resource(views.ReviewLogView, "/api/approve_log/")
review_wrap.add_resource(views.SaveApproveView, "/api/save_approve")
review_wrap.add_resource(views.GetApproveView, "/api/get_approve")
