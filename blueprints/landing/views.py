from flask import render_template, redirect, url_for
from flask.views import View, MethodView

from lib.flask_augment import check_args, ensure_args, ensure_presence
from lib.utils import simple_form

from .forms import LoginForm

def landing():
    return render_template('landing/landing.slim')

login = simple_form(LoginForm, 'landing/login.slim', lambda: 'Logged in')

