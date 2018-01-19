# -*- coding=utf-8 -*-

from flask import Flask


app = Flask(__name__)


from apps.usertags import usertags
from apps.electric import electric
from apps.weibo import weibo

app.register_blueprint(usertags)
app.register_blueprint(electric)
app.register_blueprint(weibo)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=9013, debug=True)
