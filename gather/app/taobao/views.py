# -*- coding: utf-8 -*-

import json
import time
import datetime
import operator
from flask_restful import Resource
from flask import jsonify, render_template
from flask.views import MethodView

from app.models import RequestRecord, OperatorRecord
from app.config import Config
from app.constant import Code


class TaobaoAuthView(MethodView):

    def get(self):
        date_time = datetime.datetime.now()
        start_time = date_time - datetime.timedelta(hours=Config.TIMES)
        api_type = "operator_tbAuth"
        record = RequestRecord.objects(api_type=api_type, create_time__gte=start_time).count()
        data = RequestRecord._get_collection().aggregate([
            {
                "$match": {
                    "api_type": api_type,
                    "create_time": {
                        "$gte": start_time,
                    }
                }
            },
            {
                "$group": {
                    "_id": "$result.code",
                    "count": {"$sum": 1}
                    }
            },
            {
                "$project": {
                    "_id": 0,
                    "errcode": "$_id",
                    "count": "$count",
                    "precent": {
                        "$divide":["$count", record]
                    }
                }
            }
        ])
        result = []
        for i in data:
            i["msg"] = Code.CODE_MSG.get(i.get("errcode"))
            i["precent"] = "%.2f" % (i.get("precent") * 100) + '%'
            result.append(i)
        for i in result:
            print(i)
        return render_template("first.html", result=result)
        # return jsonify({"all_count": record, "status": result})


class TaobaoLoginView(Resource):

    def get(self):
        date_time = datetime.datetime.now()
        start_time = date_time - datetime.timedelta(hours=Config.TIMES)
        api_type = "operator_tbLogin"
        record = RequestRecord.objects(api_type=api_type, create_time__gte=start_time).count()
        data = RequestRecord._get_collection().aggregate([
            {
                "$match": {
                    "api_type": api_type,
                    "create_time": {
                        "$gte": start_time,
                    }
                }
            },
            {
                "$group": {
                    "_id": "$result.code",
                    "count": {"$sum": 1}
                    }
            },
            {
                "$project": {
                    "_id": 0,
                    "errcode": "$_id",
                    "count": "$count",
                    "precent": {
                        "$divide":["$count", record]
                    }
                }
            }
        ])
        result = []
        for i in data:
            i["msg"] = Code.CODE_MSG.get(i.get("errcode"))
            i["precent"] = "%.2f" % (i.get("precent") * 100) + '%'
            result.append(i)
        return render_template("second.html", result=result)
        # return jsonify({"all_count": record, "status": result})


class TaobaoResultView(Resource):

        def get(self):
            date_time = datetime.datetime.now()
            api_type = "operator_tbResult"
            start_time = date_time - datetime.timedelta(hours=Config.TIMES)
            record = RequestRecord.objects(api_type=api_type, create_time__gte=start_time).count()
            data = RequestRecord._get_collection().aggregate([
                {
                    "$match": {
                        "api_type": api_type,
                        "create_time": {
                            "$gte": start_time,
                        }
                    }
                },
                {
                    "$group": {
                        "_id": "$result.code",
                        "count": {"$sum": 1}
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "errcode": "$_id",
                        "count": "$count",
                        "precent": {
                            "$divide": ["$count", record]
                        }
                    }
                }
            ])
            result = []
            for i in data:
                i["msg"] = Code.CODE_MSG.get(i.get("errcode"))
                i["precent"] = "%.2f" % (i.get("precent") * 100) + '%'
                result.append(i)
            return render_template("three.html", result=result)
            # return jsonify({"all_count": record, "status": result})


class TaobaoAuthCrawlerView(Resource):

    def get(self):
        from itertools import groupby
        start_time = int(time.time()) - 60*60*Config.TIMES
        record = OperatorRecord.objects(create_time__gte=start_time)
        times = record.count()
        one = []
        two = []
        for i in record:
            one_setp = json.loads(i.one_setp or "{}")
            two_setp = json.loads(i.two_setp or "{}")
            if one_setp:
                one.append(one_setp)
            if two_setp:
                two.append(two_setp)
        a = sorted(one, key=operator.itemgetter("errcode"))
        b = sorted(two, key=operator.itemgetter("errcode"))
        first = []
        second = []
        for k, v in groupby(a, operator.itemgetter("errcode")):
            data = list(v)
            all_times = len(data)
            first.append({"errcode": k, "count": all_times, "precent": "%.2f" % ( all_times/times * 100) + '%', "msg": Code.ERROR_MSG.get(k)})
        for k, v in groupby(b, operator.itemgetter("errcode")):
            data = list(v)
            all_times = len(data)
            second.append({"errcode": k, "count": all_times, "precent": "%.2f" % ( all_times/times * 100) + '%', "msg": Code.ERROR_MSG.get(k)})
        return render_template("all.html", first=first, second=second)
        # return jsonify({"all_count": times, "one_status": first, "two_status": second})