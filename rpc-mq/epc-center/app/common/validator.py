# -*- coding = utf-8 -*-
import json
import re


def vin(value):

    message = "vin码不合法"

    pattern = re.compile('^[A-Z0-9]{17}$')
    if not pattern.match(value):
        raise ValueError(message)

    return value


def json_type(value):

    message = "不是json串"

    try:
        res = json.loads(value)
    except:
        raise ValueError(message)

    return res
