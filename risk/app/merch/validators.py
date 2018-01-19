# -*- coding: utf-8 -*-


def baseinfo_validator(data):

    if not isinstance(data, dict):
        raise TypeError('baseinfo_invalid')

    if 'address' not in data or not isinstance(data['address'], str):
        raise ValueError('address invalid')
    if 'contactPhone' not in data or not isinstance(data['contactPhone'], str):
        raise ValueError('contactPhone invalid')
    if 'contacts' not in data or not isinstance(data['contacts'], str):
        raise ValueError('contacts invalid')

    if 'contractStatus' not in data:
        raise ValueError('contractStatus invalid')

    if 'contractUrl' not in data:
        raise ValueError('contractId invalid')
    if 'contractName' not in data:
        raise ValueError('contractName invalid')

    if 'licenseStatus' not in data:
        raise ValueError('licenseStatus invalid')

    if 'licenseUrl' not in data:
        raise ValueError('license invalid')
    if 'licenseName' not in data:
        raise ValueError('licenseName invalid')
    if 'cooperationStatus' not in data or not isinstance(data['cooperationStatus'], int):
        raise ValueError('cooperationStatus invalid')
    if 'level' not in data or not isinstance(data['level'], str):
        raise ValueError('level invalid')
    if 'merchantPhone' not in data or not isinstance(data['merchantPhone'], str):
        raise ValueError('merchantPhone invalid')
    if 'name' not in data or not isinstance(data['name'], str):
        raise ValueError('name invalid')
    if 'organizeNum' not in data or not isinstance(data['organizeNum'], str):
        raise ValueError('organizeNum invalid')
    if 'propagandaChannel' in data and not isinstance(data['propagandaChannel'], str):
        raise ValueError('propagandaChannel invalid')
    if 'remarks' in data and not isinstance(data['remarks'], str):
        raise ValueError('remarks invalid')
    if 'signTime' not in data or not isinstance(data['signTime'], int):
        raise ValueError('signTime invalid')

    return data


def applytable_validator(data):

    if not isinstance(data, list):
        raise TypeError('trial invalid')

    for i in data:
        if 'applicationId' not in i:
            raise ValueError('applicationId invalid')
        if not isinstance(i.get("trial"), list):
            raise TypeError('trial elementary invalid')
        for j in  i.get("trial"):
            if 'stage' not in j:
                raise ValueError('stage invalid')
    return data
