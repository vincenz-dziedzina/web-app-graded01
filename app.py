
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from sqlalchemy import and_
from werkzeug.security import generate_password_hash, check_password_hash
from models import *
from forms import *
from settings import app, db
from helper_functions import *

# Terminal instructions:
# . web-tech/bin/activate
# export FLASK_APP=app.py
# export FLASK_DEBUG=1
# flask run

@app.route('/')
@check_authentification # preprocessor in the helper_functions file
def index():
    # get_current_user function is in the helper_functions file
    current_user = get_current_user()
    submitted_papers = Paper.query.filter(Paper.authors.any(id=current_user.id)).all()
    review_papers = Score.query.filter(Score.reviewer.has(id=current_user.id)).filter_by(is_rated=False).all()
    return render_template('index.html', submitted_papers=submitted_papers, review_papers=review_papers)

@app.route('/login', methods=["POST", "GET"])
def login():
    # form classes are in the forms file
    if request.method == 'GET':
        form = Login()
        return render_template('login.html', form=form)
    elif request.method == 'POST':
        form = Login(request.form)
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user != None :
                if check_password_hash(user.hashed_password, form.password.data):
                    # CSS classes enum is specified in the helper functions file
                    flash({"formField" : "success", "message" : "Login successful"} , CssClasses.SUCCESS)
                    session["auth_user_id"] = user.id
                    return redirect(url_for("index"))
                else:
                    flash({"formField" : "password", "message" : "Login failed: Wrong password"} , CssClasses.ERROR)
                    return render_template('login.html', form=form)
            else:
                flash({"formField" : "email", "message" : "Login failed: User with this email does not exist"} , CssClasses.ERROR)
                return render_template('login.html', form=form)
        else:
            # flash_errors function is in the helper_functions file
            flash_errors(form)
            return render_template('login.html', form=form)

@app.route('/logout')
@check_authentification
def logout():
    del session["auth_user_id"]
    flash({"formField" : "success", "message" : "Logout successful"}, CssClasses.SUCCESS)
    return redirect(url_for("login"))

@app.route('/registration', methods=['POST', 'GET'])
def registration():
    if request.method == 'GET':
        form = Registration()
        return render_template('registration.html', form=form)
    elif request.method == 'POST':
        form = Registration(request.form)
        if form.validate_on_submit():
            hashed_password = generate_password_hash(form.password.data)
            new_user = User(email=form.email.data, hashed_password = hashed_password)
            db.session.add(new_user)
            try:
                db.session.commit()
                flash({"formField" : "success", "message" : "Registration successful"} , CssClasses.SUCCESS)
                session["auth_user_id"] = new_user.id
                return redirect(url_for("index"))
            except IntegrityError:
                flash({"formField" : "email", "message" : "Email already exists, choose a different email address"} , CssClasses.ERROR)
                return render_template('registration.html', form=form)
        else:
            flash_errors(form)
            return render_template('registration.html', form=form)

@app.route('/paper_submission', methods=['POST', 'GET'])
@check_authentification
def paper_submission():
    current_user = get_current_user()

    # every user except for the admin or the submitting user are allowed to be coauthor
    users = User.query.filter(User.email != current_user.email).filter(User.is_admin == False).all()

    # preprocessing for the form select field
    potential_authors = []
    for user in users:
        tuple = (user.id, user.email)
        potential_authors.append(tuple)

    if request.method == "GET":
        form = PaperSubmission()
        form.authors.choices = potential_authors
        return render_template('paper_submission.html', form=form)

    elif request.method == "POST":
        form = PaperSubmission(request.form)
        form.authors.choices = potential_authors

        if current_user.is_admin:
            flash({"formField" : "error", "message" : "The admin is not allowed to submit papers"}, CssClasses.ERROR)
            return render_template('paper_submission.html', form=form)
        elif form.validate_on_submit():
            # Status enum in helper_functions file
            new_paper = Paper(status=Status.UNDER_REVIEW, title=form.title.data, abstract=form.abstract.data)
            authors = form.authors.data
            users = User.query.filter(User.id.in_(authors)).all()

            for user in users:
                # checks if adding the user as coauthor is allowed
                if user in users:
                    new_paper.authors.append(user)

            new_paper.authors.append(current_user)
            db.session.add(new_paper)
            db.session.commit()

            # TODO check if message get displayed
            flash({"formField" : "success", "message" : "Paper submission successful"}, CssClasses.SUCCESS)
            return redirect(url_for("getPapersUserOverview"))
        else:
            flash_errors(form)
            return render_template('paper_submission.html', form=form)

@app.route('/roles', methods=['POST', 'GET'])
@check_authentification
@check_admin # preprocesser in helper_functions file
def roles():
    current_user = get_current_user()
    # conferencechair should not be a reviewer
    users = User.query.filter(User.is_admin == False).all()

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
        flash({"formField" : "", "message" : "Roles updated"}, CssClasses.SUCCESS)
        return render_template('set_roles.html', users=users)

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
    if paper == None:
        flash({"formField" : "", "message" : "This paper does not exist"}, CssClasses.ERROR)
        return redirect(url_for("accept_papers"))

    # TODO change this in the other actions
    form = SetStatus(request.form)
    choices = [(Status.UNDER_REVIEW, Status.UNDER_REVIEW), (Status.ACCEPTED, Status.ACCEPTED), (Status.REJECTED, Status.REJECTED)]
    form.status.choices = choices

    if request.method == "GET":
        return render_template('set_status.html', paper=paper, form=form)
    elif request.method == 'POST':
        if form.validate_on_submit():
            paper.status = form.status.data
            db.session.commit()
            return redirect(url_for("accept_papers"))
        else:
            flash_errors(form)
            return render_template('set_status.html', paper=paper, form=form)


@app.route('/set_reviewer/<int:paperID>', methods=['POST', 'GET'])
@check_authentification
@check_admin
def set_reviewer(paperID):
    paper = Paper.query.get(paperID)

    forbidden_ids = []
    for author in paper.authors:
        forbidden_ids.append(author.id)

    for reviewer in paper.reviewers:
        forbidden_ids.append(reviewer.reviewer.id)

    potential_reviewers = []
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
            if reviewer_id not in forbidden_ids:
                reviewer = User.query.get(reviewer_id)
                score = Score(paper = paper, reviewer = reviewer)
                db.session.add(score)

        db.session.commit()
        flash({"formField" : "", "message" : "Added reviewer"}, CssClasses.SUCCESS)
        return redirect(url_for("accept_papers"))

@app.route("/papers", methods=["GET"])
@check_authentification
def getPapersUserOverview():
    user = get_current_user()
    submitted_papers = Paper.query.filter(Paper.authors.any(id=user.id)).all()
    scores = user.scored_papers

    return render_template("papers.html", scores=scores, submitted_papers=submitted_papers)

@app.route("/papers/<int:paperID>", methods=["GET"])
@check_authentification
def getPaperReviewRating(paperID):
    user = get_current_user()
    paper = Paper.query.get(paperID)
    score = Score.query.filter(Score.reviewer == user).filter(Score.paper == paper).first()

    if(paper != None):
        #
        if paper.has_reviewer(user):
            form = SetRating()
            form.rating.data = score.rating
            return render_template("rate_paper.html", paper=paper, form=form)

        else:
            flash({"formField" : "error", "message" : "You do not have access to this paper"} , CssClasses.ERROR)
            return redirect(url_for("getPapersUserOverview"))
    else:
        flash({"formField" : "error", "message" : "This paper does not exist"} , CssClasses.ERROR)
        return redirect(url_for("getPapersUserOverview"))

@app.route("/papers/<int:paperID>", methods=["POST"])
@check_authentification
def postPaperReviewRating(paperID):
    user = get_current_user()
    paper = Paper.query.get(paperID)

    if(paper != None):
        form = SetRating(request.form)
        if paper.has_reviewer(user):
            if form.validate_on_submit():
                rating = form.rating.data
                score = Score.query.filter(Score.reviewer == user).filter(Score.paper == paper).first()
                score.rating = rating
                score.is_rated = True
                db.session.commit()

                flash({"formField" : "success", "message" : "Rating successful"} , CssClasses.SUCCESS)
                return render_template("rate_paper.html", paper=paper, form=form)
            else:
                flash_errors(form)
                return render_template("rate_paper.html", paper=paper, form=form)
        else:
            flash({"formField" : "", "message" : "You are not allowed to rate this paper"} , CssClasses.ERROR)
    else:
        flash({"formField" : "", "message" : "This paper does not exist"} , CssClasses.ERROR)
        return redirect(url_for("getPaperReviewRating",  paper.id))

if __name__ == '__main__':
    app.run()
