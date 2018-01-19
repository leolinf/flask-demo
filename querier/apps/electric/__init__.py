from flask import Blueprint


electric= Blueprint('exectric', __name__)


from . import urls
