#! /usr/bin/env python
# -*- coding = utf-8 -*-

import json

from app import create_app
from app.models import Maintenance


def process_result(data):

    chart_info = data["chart_info"]

    if not chart_info:
        return []

    l = []
    d = {}
    for i in chart_info:
        item = i.pop("0")
        for k, v in i.items():
            if k not in d:
                d[k] = {}
            d[k][item] = v
    for k, v in d.items():
        l.append({
            "distance": k,
            "chartInfo": sorted([(p, q) for p, q in v.items()]),
        })

    # print(json.dumps(d, ensure_ascii=False))

    return l


def main():

    filename = "result.data.2"

    with open(filename) as f:
        while True:
            line = f.readline()
            if not line:
                break

            line = json.loads(line)
            brand = line["brand"]
            group = line["group"]
            serial = line["serial"]
            result = line["result"]
            result = process_result(result)

            Maintenance(
                MasterBrandName=brand["MasterBrandName"],
                MasterBrandID=brand["MasterBrandID"],
                FirstLetter=brand["FirstLetter"],
                GroupName=group["GroupName"],
                GroupID=group["GroupID"],
                DefaulCarID=group["DefaulCarID"],
                SerialAllSpell=serial["SerialAllSpell"],
                SerialID=serial["SerialID"],
                SerialName=serial["SerialName"],
                result=result
            ).save()


if __name__ == '__main__':
    create_app()
    main()
