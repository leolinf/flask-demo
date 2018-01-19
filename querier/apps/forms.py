from wtforms import Form, StringField, IntegerField
from wtforms.validators import required


class AuthForm(Form):
    '''check user form'''

    username = StringField('app_key', [required()])
    password = StringField('app_secret', [required()])


class TelnoForm(Form):
    '''check phone form'''

    telno = StringField('telno', [required()])
    mon_ago = IntegerField('months_ago')
    end_time = IntegerField("end_time")
