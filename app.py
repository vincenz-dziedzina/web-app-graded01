from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from models import *
# from enum import Enum

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/test.db'
app.secret_key = "mysecretkey"
db = SQLAlchemy(app)

# Terminal instructions:
# . web-tech/bin/activate
# export FLASK_APP=app.py
# export FLASK_DEBUG=1
# flask run

class Status:
    UNDER_REVIEW = "under review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

def logged_in():
    return "auth_user_id" in session

@app.context_processor
def add_template_variables():
    variables = dict()
    logged_in_bool = logged_in()
    variables["logged_in"] = logged_in
    if logged_in_bool:
        variables["current_user"] = get_current_user()
    return variables

def check_authentification(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if logged_in():
            print("in here")
            return f(*args, **kwargs)
        else:
            return redirect(url_for("login"))
    return decorated_function

def get_current_user():
    return User.query.get(session["auth_user_id"])

@app.route('/')
@check_authentification
def index():
    current_user = get_current_user()
    papers = Paper.query.filter(Paper.authors.any(id=current_user.id)).all()
    return render_template('index.html', papers=papers)


@app.route('/login', methods=["POST", "GET"])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    elif request.method == 'POST':
        form_data = request.form
        user = User.query.filter_by(email=form_data.get('email')).first()
        if check_password_hash(user.hashed_password, form_data.get("password")):
            session["auth_user_id"] = user.id
            return redirect(url_for("index"))
        else:
            return render_template('login.html', message="Login failed")

@app.route('/logout')
@check_authentification
def logout():
    del session["auth_user_id"]
    return redirect(url_for("login"))

@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'GET':
        return render_template('registration.html')
    elif request.method == 'POST':
        form_data = request.form

        hashed_password = generate_password_hash(form_data.get("password"))
        new_user = User(email=form_data.get("email"), hashed_password = hashed_password)

        db.session.add(new_user)
        db.session.commit()

        session["auth_user_id"] = new_user.id
        return redirect(url_for("index"))

@app.route('/paper_submission', methods=['POST', 'GET'])
@check_authentification
def paper_submission():
    if request.method == "GET":
        return render_template('paper_submission.html')
    elif request.method == "POST":
        result = request.form

        new_paper = Paper(status=Status.UNDER_REVIEW, title=result.get('title'), abstract=result.get('abstract'))
        new_paper.authors.append(app.current_user)

        db.session.commit()
        papers = Paper.query.filter(Paper.authors.any(id=app.current_user.id)).all()
        # TODO Add other authors too
        return render_template('index.html', current_user=current_user, papers=papers)

@app.route('/roles')
@check_authentification
def roles():
    users = User.query.all()
    return render_template('set_roles.html', users=users)

if __name__ == '__main__':
    app.run()
