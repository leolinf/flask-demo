# -*- coding: utf-8 -*-

import re
import datetime

from flask_restful import inputs


phone = inputs.regex('^1\d{10}$')
name = inputs.regex('^.{0,10}$')
banknum = inputs.regex('^.{5,30}$')
address = inputs.regex('^.{5,30}$')


def idnum(value):

    message = 'The input field idnum is illegal.'

    pattern = re.compile('^\d{17}[0-9X]$')
    if not pattern.match(value):
        raise ValueError(message)

    if value[6:8] != '19':
        raise ValueError(message)

    birth = value[6:14]
    try:
        datetime.datetime.strptime(birth, '%Y%m%d')
    except ValueError:
        raise ValueError(message)

    def _relation(value):
        factor = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        last = {
            0: '1',
            1: '0',
            2: 'X',
            3: '9',
            4: '8',
            5: '7',
            6: '6',
            7: '5',
            8: '4',
            9: '3',
            10: '2',
        }
        summary = sum([int(value[i]) * factor[i] for i in range(17)])
        return last[summary % 11] == value[-1]

    if not _relation(value):
        raise ValueError(message)

    return value

