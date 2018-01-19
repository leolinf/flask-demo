# -*- coding: utf-8 -*-

import re
import datetime

from ..models import SingleSearch


class SyncManager(object):
    """同步更新管理"""

    @staticmethod
    def credit_approve_status(search_id, status, time=None):
        """信用报告审批状态"""

        if status is None:
            return

        SingleSearch.objects(apply_number=search_id).update(
            set__approve_status=status,
            set__approve_time=time, 
        )


class ExcelManager:

    @staticmethod
    def _validate_mobile(mobile):

        l = mobile.split('.')
        if len(l) == 2:
            mobile = l[0]

        return bool(re.match('^1\d{10}$', mobile))

    @staticmethod
    def _validate_name(name):

        if not name:
            return True

        return bool(re.match('^.{0,10}$', name))

    @staticmethod
    def _validate_bankcode(bankcode):

        if not bankcode:
            return True

        return bool(re.match('^.{5,30}$', bankcode))

    @staticmethod
    def _validate_idcard(idcard):

        if not idcard:
            return True

        pattern = re.compile('^\d{17}[0-9X]$')
        if not pattern.match(idcard):
            return False

        if idcard[6:8] != '19':
            return False

        birth = idcard[6:14]
        try:
            datetime.datetime.strptime(birth, '%Y%m%d')
        except ValueError:
            return False

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

        if not _relation(idcard):
            return False

        return True

    @staticmethod
    def _validate_address(address):

        if not address:
            return True

        return bool(re.match('^.{5,30}$', address))

    @classmethod
    def validate(cls, mobile, name=None, idcard=None, bankcode=None, address=None, *args):

        opts = [cls._validate_mobile(mobile)]
        if name:
            opts.append(cls._validate_name(name))
        if idcard:
            opts.append(cls._validate_idcard(idcard))
        if bankcode:
            opts.append(cls._validate_bankcode(bankcode))
        if address:
            opts.append(cls._validate_address(address))

        return all(opts)

    @classmethod
    def validate_monitor(cls, mobile, name=None, idcard=None, *args):

        opts = [cls._validate_mobile(mobile)]

        if name:
            opts.append(cls._validate_name(name))
        if idcard:
            opts.append(cls._validate_idcard(idcard))

        return all(opts)
