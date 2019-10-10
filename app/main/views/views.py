from flask import session, redirect, url_for, render_template, request, Response
from .. import main
#from .forms import LoginForm
from flask import current_app as app

@main.route('/hi')
def hi():
        return "Hello World!"

@main.route('/old')
def old_index():
        #colors dict()
        colors = dict(app.config.get('COLOR_DICT'))
        print("colors=")
        print(colors)
        return "You have reached a dead end on the internet... :("

