# -*- coding: utf-8 -*-

from sqlalchemy.exc import IntegrityError

from flask_restful import Resource
from flask.views import MethodView
from flask import request, current_app, g
from werkzeug.exceptions import MethodNotAllowed

from .core.functions import make_response
from .constants import Code


class BaseResource(Resource):

    def dispatch_request(self, *args, **kwargs):

        try:
            return super(BaseResource, self).dispatch_request(*args, **kwargs)
        except IntegrityError as e:
            current_app.logger.error(e)
            return make_response(Code.SYSTEM_ERROR)
        finally:
            if hasattr(g, "session"):
                print("removing session")
                g.session.remove()


class BaseView(MethodView):

    pass
