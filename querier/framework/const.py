# -*- coding=utf-8 -*-


class _const:
    class ConstError(TypeError):
        pass

    def __setattr__(self, name, value):

        if not name.isupper():
            raise TypeError("Need to bind uppercase")

        self.__dict__[name] = value

import sys
sys.modules['const'] = _const()

import const

const.SUCCESS = 1200
const.VERIFYDENIED = 1301
const.MISSPARAM = 1302


const.MSG = {
    const.SUCCESS: u'成功',
    const.MISSPARAM: u'没有传递必填参数或参数类型不对',
    const.VERIFYDENIED: u'没有权限',
}
