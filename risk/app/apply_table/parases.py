# -*- coding: utf-8 -*-
from flask_restful import reqparse, inputs
import json
import traceback


class ApplyTableFormat(object):
    apply_table_parse = {
        'id': str,
        'modules': list,
        'name': str,
        'status': inputs.int_range(0, 1)
    }
    modules_parse = {
        'immutable': inputs.int_range(0, 1),
        'index': int,
        'name': str,
    }
    modulars = {
        'name': str,
        'labels': list,
        "key": str,
    }
    labels = {
        'unchanged': int,
        'isShow': int,
        'key': str,
        'mustWrite': int,
        'name': str,
        'remarks': str,
        'type': str,
    }


def check_data(data_module, input_data):
    """ update a dict """
    for key, val in data_module.items():
        try:
            input_data[key] = val(input_data[key])
        except (IndexError, TypeError, ValueError) as ex:
            raise ValueError(str(ex))
    return input_data


class CustomParse(object):
    def __init__(self, strict=True):
        self.strict = strict

    def __call__(self, data):

        data = check_data(ApplyTableFormat.apply_table_parse, data)
        for module_index, each_b_mod  in enumerate(data['modules']):
            data_module = check_data(ApplyTableFormat.modules_parse, data['modules'][module_index])
            pages = data_module['pages']
            try:
                for index, each_page in enumerate(pages):
                    for s_mod_index, each_s_modular in enumerate(each_page['modulars']):
                        each_page['modulars'][s_mod_index] = check_data(ApplyTableFormat.modulars, each_s_modular)
                        labels_input = each_page['modulars'][s_mod_index]['labels']
                        for col, each_label in enumerate(labels_input):

                            labels_input[col] = check_data(ApplyTableFormat.labels, each_label)
                    return data
            except Exception as e:
                traceback.print_exc()