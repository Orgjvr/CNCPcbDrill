#!/bin/env python
from pcbdrill import create_app, socketio

app = create_app(debug=True)

if __name__ == '__main__':
    socketio.run(app)


from flask import Flask, render_template
from flask_socketio import SocketIO, emit


app = Flask(__name__, instance_relative_config=True)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Load the default configuration
app.config.from_object('config.default')

# Load the configuration from the instance folder
app.config.from_pyfile('config.py')

# Load the file specified by the APP_CONFIG_FILE environment variable
# Variables defined here will override those in the default configuration
app.config.from_envvar('APP_CONFIG_FILE')


if __name__ == '__main__':
    socketio.run(app)

from yourapplication import app

#from setuptools import setup

#setup(
#    name='pcbdrill',
#    packages=['pcbdrill'],
#    include_package_data=True,
#    install_requires=[
#        'flask',
#    ],
#)

