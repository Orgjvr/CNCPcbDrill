from flask import session, redirect, url_for, render_template, request
from . import main
#from .forms import LoginForm

@main.route('/')
def index():
        return "Hello World!"

