# -*-coding:utf-8 -*-


def gen_cat_map():
    """子品类的名称"""
    cat_map = {}
    with open("dat/dim_dev.format", "r") as f:
        for line in f:
            ls = line.strip().split("\x01")
            cat_map[ls[0]] = ls[1]
    return cat_map
