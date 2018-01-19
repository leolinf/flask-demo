#! /usr/bin/env python
# -*- coding = utf-8 -*-

import json

from app import create_app
from app.models import SpecBySeriesId, Series, Spec


def main():

    filename = "car.info.3.20170926"

    with open(filename) as f:
        while True:
            line = f.readline()
            if not line:
                break

            line = json.loads(line)
            spec_group_list = line["SpecGroupList"]
            spec_stop_list = line["SpecStopList"]
            spec_upcoming_list = line["SpecUpcomingList"]
            spec_count = line["SpecCount"]
            type_id = str(line["type_id"])
            series_name = line["SeriesName"]
            series = Series.objects(series_id=type_id).first()
            SpecBySeriesId(
                series_id=type_id, series_name=series_name, spec_count=spec_count, spec_group_list=spec_group_list,
                spec_stop_list=spec_stop_list, spec_upcoming_list=spec_upcoming_list, brand_id=series.brand_id).save()
            l = spec_group_list + spec_stop_list + spec_upcoming_list
            for i in l:
                if "SpecList" in i:
                    for j in i["SpecList"]:
                        name = j["name"]
                        uid = j["id"]
                        Spec(spec_name=name, spec_id=uid, series_id=type_id, brand_id=series.brand_id).save()
                else:
                    name = i["name"]
                    uid = i["id"]
                    Spec(spec_name=name, spec_id=uid, series_id=type_id, brand_id=series.brand_id).save()


if __name__ == '__main__':
    create_app()
    main()
