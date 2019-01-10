# -*- coding: utf-8 -*-

from flask import Flask, render_template
from flask_socketio import SocketIO, emit, send


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['DEBUG'] = True
socketio=SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('my event', namespace='/test')
def test_message(message):
    emit('my response', {'data': message['data']})
    print('test_message my event')


@socketio.on('my broadcast event', namespace='/test')
def test_message(message):
    # 未命名事件
    emit('my response', {'data': message['data']}, broadcast=True)
    print('test_message mybraodcast')


@socketio.on('connect', namespace='/test')
def test_connect():
    emit('my response', {'data': 'Connected'})
    print("test connect")


@socketio.on('disconnect', namespace='/test')
def test_disconnect():
    print('Client disconnected')


@socketio.on('json')
def hander_json(json):
    print('receied json: %s', str(json))


@socketio.on('message')
def handler_message(message):
    # 命名事件

    send(message)
    print('recevied message:'+ str(message))

@socketio.on('client_event')
def client_msg(msg):
    emit('server_response', {'data': msg['data']})
    print('client', msg)

@socketio.on('connect_event')
def connected_msg(msg):
    emit('server_response', {'data': msg['data']})
    print('connect', msg)
    return 'success', '我爱喝水'


if __name__ == '__main__':
    socketio.run(app)
