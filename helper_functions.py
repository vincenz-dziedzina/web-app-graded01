from flask import Flask, render_template, request, session, redirect, url_for, flash
from functools import wraps
from settings import app
from models import *

# Enum for python 2.7
class Status:
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

class CssClasses:
    ERROR = "w3-panel w3-red"
    SUCCESS = "w3-panel w3-pale-green"

def logged_in():
    return "auth_user_id" in session

# Provides logged_in, request_path and current_user variable for every template
@app.context_processor
def add_template_variables():
    variables = dict()
    logged_in_bool = logged_in()
    variables["logged_in"] = logged_in()
    variables["request_path"] = str(request.path)
    if logged_in_bool:
        variables["current_user"] = get_current_user()
    return variables

def check_authentification(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if logged_in():
            return f(*args, **kwargs)
        else:
            flash({"formField" : "success", "message" : "You do not have access to this page."}, CssClasses.ERROR)
            return redirect(url_for("login"))
    return decorated_function

def check_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if get_current_user().is_admin:
            return f(*args, **kwargs)
        else:
            flash({"formField" : "success", "message" : "Only the conferencechair (admin) has access to this page"}, CssClasses.ERROR)
            return redirect(url_for("login"))
    return decorated_function

def get_current_user():
    return User.query.get(session["auth_user_id"])

def flash_errors(form):
    for formField, errors in form.errors.items():
        for error in errors:
            flash({"formField" : formField, "message" : str(error)}, CssClasses.ERROR)
