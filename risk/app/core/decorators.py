# -*- coding: utf-8 -*-

from functools import wraps

from flask import request
from sqlalchemy.orm import scoped_session

from ..config import Config
from ..constants import Code
from .functions import make_response
from ..databases import Session


def access_restrict(req=request):
    """单个view的具体http方法的访问限制"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            # IP不在白名单内
            if req.remote_addr not in Config.API_WHITE_LIST:
                return make_response(status=Code.ACCESS_DENIED)

            return func(*args, **kwargs)
        return wrapper
    return decorator


def cache_riskevaluation(func):

    @wraps(func)
    def wrapper(self, search_id):

        search_id = int(search_id)

        from app.models import Caching, InputApply, SingleSearch
        from app.credit.utils import check_whether_self

        session = scoped_session(Session)
        input_apply = session.query(InputApply).get(search_id)
        search = SingleSearch.objects(apply_number=search_id).first()

        if not input_apply or not search or not check_whether_self(search):
            session.remove()
            return func(self, search_id)

        cache = Caching.objects(search_id=search_id).first()
        if cache:
            session.remove()
            return cache.resp

        resp = func(self, search_id)

        # 没有运营商授权或者授权完了才缓存
        result = search.operator_data.get('callback_operator', {})
        if not input_apply.token or result:
            Caching.objects(search_id=search_id).update(
                upsert=True,
                set__search_id=search_id,
                set__resp=resp,
            )

        session.remove()

        return resp
    return wrapper
