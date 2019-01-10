#! /usr/bin/env python
# -*- coding = utf-8 -*-

import json

from app import create_app
from app.models import SeriesByBrandId, Brand, Series


def main():

    filename = "car.info.2.20170927"

    with open(filename) as f:
        while True:
            line = f.readline()
            if not line:
                break

            line = json.loads(line)
            fct_list = line["FctList"]
            brand_id = line["brand_id"]
            brand = Brand.objects(brand_id=brand_id).first()
            SeriesByBrandId(brand_id=brand_id, brand_name=brand.brand_name, fct_list=fct_list).save()
            for i in fct_list:
                for j in i["item"]:
                    Series(brand_id=brand_id, series_id=j["id"], series_name=j["name"]).save()


if __name__ == '__main__':
    create_app()
    main()
