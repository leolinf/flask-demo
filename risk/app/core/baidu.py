# -*- coding = utf-8 -*-
import logging

import requests
import traceback


class BaiduMap:

    def __init__(self, ak):

        self.ak = ak

    def convert_address_to_coordinate(self, addr):

        logging.info("converting address to coordinate")

        url = "http://api.map.baidu.com/geocoder/v2/"

        data = {
            "address": addr,
            "output": "json",
            "ak": self.ak,
        }

        try:
            resp = requests.get(url, params=data, timeout=5)
            res = resp.json()
        except:
            traceback.print_exc()
            return ""
        try:
            location = res["result"]["location"]
            coords = "{0},{1}".format(location["lng"], location["lat"])
        except:
            traceback.print_exc()
            coords = ""

        return coords

    def convert_gps_to_utm(self, coords):

        url = "http://api.map.baidu.com/geoconv/v1/"

        data = {
            "ak": self.ak,
            "coords": coords,
            "from": 1,
            "to": 6,
        }

        try:
            resp = requests.get(url, params=data, timeout=5)
            res = resp.json()
        except:
            traceback.print_exc()
            return {}

        result = res.get("result", []) or []

        if result:
            return result[0]

        return {}

    @staticmethod
    def calculate_distance(coord_a, coord_b):

        logging.info("calculating distance")

        if not all([coord_a, coord_b]):
            return

        return ((coord_a["x"] - coord_b["x"]) ** 2 + (coord_a["y"] - coord_b["y"]) ** 2) ** 0.5


if __name__ == '__main__':

    ak = "7dZQjFgQSPWNMySzqqMfVjtB"

    baidu_map = BaiduMap(ak)
    # a = baidu_map.convert_gps_to_utm("104.057412,30.539246")
    # b = baidu_map.convert_gps_to_utm("104.05388,30.543896")
    #
    # dist = baidu_map.calculate_distance(a, b)
    # print(dist)
    print(baidu_map.convert_address_to_coordinate("成都天府广场"))
