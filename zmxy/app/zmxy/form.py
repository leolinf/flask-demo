# -*- coding: utf-8 -*-

from wtforms import Form, StringField, IntegerField, SelectField
from wtforms import validators


class AuthForm(Form):

    phone = StringField("mobile", [validators.length(min=11, max=11), validators.Regexp(r'^1\d{10}$')])
    name = StringField("name", [validators.required()])
    idCard = StringField("idcard", [validators.required()])


class DataForm(Form):

    params = StringField("params", [validators.required()])
    sign = StringField("sign", [validators.required()])
