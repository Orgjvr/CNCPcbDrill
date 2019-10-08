from flask import session, redirect, url_for, render_template, request, Response
from . import main
#from .forms import LoginForm

@main.route('/hi')
def hi():
        return "Hello World!"

@main.route('/')
def index():
        return "You have reached a dead end on the internet... :("

