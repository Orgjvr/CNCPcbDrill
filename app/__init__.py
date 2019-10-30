from flask import Flask , session  #, render_template
from flask_socketio import SocketIO  #, emit
import logging
import atexit

socketio = SocketIO()


def create_app(debug=False):
    """Create an application."""
    
    app = Flask(__name__, instance_relative_config=True)
    app.debug = debug
    app.config['SECRET_KEY'] = 'gjr39dkjn344_!67#'

    # Load the default configuration from ./config/default.py
    app.config.from_object('config.default')

    #NOTE: Moved settings from default.py to configObj ==> config/default.ini

    # Load the configuration from the instance folder
    #app.config.from_object('./instance/config.ini')
    #NOTE: user specific 

    # Load the file specified by the APP_CONFIG_FILE environment variable
    # Variables defined here will override those in the default configuration
    #app.config.from_envvar('APP_CONFIG_FILE')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)


    socketio.init_app(app)


    return app


