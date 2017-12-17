
from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from models import *
from forms import *
from settings import app, db

# Terminal instructions:
# . web-tech/bin/activate
# export FLASK_APP=app.py
# export FLASK_DEBUG=1
# flask run

# TODO put GET und Post Logic for one route in different functions
# TODO Mark the current tab

# Enum for python 2.7
class Status:
    UNDER_REVIEW = "under_review"
    ACCEPTED = "accepted"
    REJECTED = "rejected"

def logged_in():
    return "auth_user_id" in session

# Provides logged_in and current_user variable for every template
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
            return f(*args, **kwargs)
        else:
            # TODO output some message with flash
            # TODO implement automatic flash display if given in layout template
            return redirect(url_for("login"))
    return decorated_function

def check_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if get_current_user().is_admin:
            return f(*args, **kwargs)
        else:
            # TODO do something appropriate
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
    form = Login()
    if request.method == 'GET':
        return render_template('login.html', form=form)
    elif request.method == 'POST':
        form_data = request.form
        user = User.query.filter_by(email=form_data.get('email')).first()
        if(user != None):
            if check_password_hash(user.hashed_password, form_data.get("password")):
                session["auth_user_id"] = user.id
                return redirect(url_for("index"))
            else:
                return render_template('login.html', message="Login failed")
        else:
            return render_template('login.html', message="No user with this email in database.", form=form)

@app.route('/logout')
@check_authentification
def logout():
    del session["auth_user_id"]
    return redirect(url_for("login"))

# TODO regular expression for email
@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'GET':
        form = Registration()
        return render_template('registration.html', form=form)
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
    # TODO make this RESTfull, add a paper page where the author can delete the paper: paper/id
    current_user = get_current_user()
    if request.method == "GET":
        form = PaperSubmission()
        choices = []
        users = User.query.filter(User.email != current_user.email).all()
        for user in users:
            tuple = (user.id, user.email)
            choices.append(tuple)
        form.authors.choices = choices
        return render_template('paper_submission.html', form=form)
    elif request.method == "POST":
        result = request.form

        new_paper = Paper(status=Status.UNDER_REVIEW, title=result.get('title'), abstract=result.get('abstract'))
        authors = request.form.getlist("authors")
        users = User.query.filter(User.id in authors).all()

        for user in users:
            new_paper.authors.append(user)

        new_paper.authors.append(current_user)
        db.session.add(new_paper)
        db.session.commit()

        # TODO redirect to Paper page RESTfull with delete button
        papers = Paper.query.filter(Paper.authors.any(id=current_user.id)).all()
        return render_template('index.html', current_user=current_user, papers=papers)

@app.route('/roles', methods=['POST', 'GET'])
@check_authentification
@check_admin
def roles():
    current_user = get_current_user()
    # writing to db with this method did not work
    users = User.query.all()
    # users = db.session.query(User).all()
    if request.method == "GET":
        return render_template('set_roles.html', users=users)
    elif request.method == 'POST':
        reviewers = request.form.getlist("user")
        for user in users:
            if user.email in reviewers:
                user.is_reviewer = True
            else:
                user.is_reviewer = False
        db.session.commit()
        return redirect(url_for("index"))

# TODO test admin access
# TODO add error codes, maybe??
@app.route('/accept_papers', methods=['GET'])
@check_authentification
@check_admin
def accept_papers():
    papers = Paper.query.all()
    if request.method == "GET":
        return render_template('accept_papers.html', papers=papers)

@app.route('/accept_papers/<int:paperID>', methods=['POST', 'GET'])
@check_authentification
def set_status(paperID):
    paper = Paper.query.filter_by(id=paperID).first()
    form = SetStatus()
    # I really am sorry for this but nothing else worked
    choices = [('under_review', Status.UNDER_REVIEW), ('accepted', Status.ACCEPTED), ('rejected', Status.REJECTED)]
    form.status.choices = choices

    if request.method == "GET":
        return render_template('set_status.html', paper=paper, form=form)
    elif request.method == 'POST':
        result = request.form
        paper.status = result.get('status')
        db.session.commit()
        return redirect(url_for("accept_papers"))

@app.route('/set_reviewer/<int:paperID>', methods=['POST', 'GET'])
@check_authentification
def set_reviewer(paperID):
    paper = Paper.query.get(paperID)

    # TODO Duplicates
    # TODO check if author is not available
    forbidden_ids = []
    for author in paper.authors:
        forbidden_ids.append(author.id)

    for reviewer in paper.reviewers:
        forbidden_ids.append(reviewer.reviewer.id)

    potential_reviewers = []
    # users = User.query.filter(User.id not in forbidden_ids).all()
    users = db.session.query(User).filter(User.is_reviewer == True).filter(~User.id.in_(forbidden_ids)).all()
    for user in users:
        potential_reviewers.append((user.id, user.email))

#   from forms.py
    form = SetReviewer()
    form.reviewer.choices = potential_reviewers

    if request.method == "GET":
        return render_template('set_reviewer.html', paper=paper, form=form)
    elif request.method == 'POST':
        scores = []
        reviewer_IDs = request.form.getlist("reviewer")
        for reviewer_id in reviewer_IDs:
            reviewer = User.query.get(reviewer_id)
            score = Score(paper = paper, reviewer = reviewer)
            db.session.add(score)

        db.session.commit()
        return redirect(url_for("accept_papers"))


if __name__ == '__main__':
    app.run()
