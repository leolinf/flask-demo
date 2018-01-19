# -*- coding = utf-8 -*-

import re


def vin(value):

    message = "vin码不合法"

    pattern = re.compile('^[A-Z0-9]{17}$')
    if not pattern.match(value):
        raise ValueError(message)

    return value


def keywords_validate(keywords):

    if not re.match("^[\u4ed00-\u9fa5a-zA-Z0-9]+$", keywords):
        return True
    return False


def vin_validate(value):

    pattern = re.compile('^[A-Z0-9]{17}$')
    if not pattern.match(value):
        return True
    return False


if __name__ == "__main__":
    print(vin_validate("12345678901234567s"))
