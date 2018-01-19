# -*- coding: utf-8 -*-


def get_cat_map():
    """子品类的名称"""
    cat_map = {}
    with open("dat/dim_dev.format", "r") as f:
        for line in f:
            ls = line.strip().split("\001")
            cat_map[ls[0]] = ls[1].decode("utf-8")
    return cat_map

cat_map = get_cat_map()
