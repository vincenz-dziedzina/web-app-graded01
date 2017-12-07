from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from models import *

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/test.db'
db = SQLAlchemy(app)

dummy = Dummy()
# app.current_user = None
app.current_user = User.query.first()


@app.route('/')
def index():
    if app.current_user == None:
        return render_template('login.html')
    else:
        papers = Paper.query.filter(Paper.authors.any(id=app.current_user.id)).all()
        print(papers)
        return render_template('index.html', current_user=app.current_user, papers=papers)


@app.route('/login')
def login():
    if app.current_user == None:
        return render_template('login.html')
    else:
        return render_template('index.html', current_user=app.current_user)

@app.route('/logout')
def logout():
    app.current_user = None
    return render_template('login.html')

@app.route('/logging_in', methods=['POST', 'GET'])
def logging_in():
    if request.method == 'POST':
        result = request.form
        print(result)
        user = User.query.filter_by(email=result.get('email')).first()
        if user and user.hashed_password == result.get('password'):
            app.current_user = user
            return render_template('index.html', current_user=app.current_user)
        else:
            return render_template('login.html', message="Login failed")

@app.route('/registration')
def registration():
    return render_template('register.html')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        result = request.form
        print(result)
        new_user = User(email=result.get('email'), hashed_password=result.get('password'))
        print(new_user)
        db.session.commit()
        app.current_user = new_user
        return render_template('index.html', current_user=app.current_user)

@app.route('/paper_submission')
def paper_submission():
    return render_template('paper_submission.html')


@app.route('/submit_paper', methods=['POST', 'GET'])
def submit_paper():
    if request.method == 'POST':
        result = request.form
        print(result)
        new_paper = Paper(status="under review", title=result.get('title'), abstract=result.get('abstract'))
        new_paper.authors.append(app.current_user)
        print(new_paper)
        db.session.commit()
        papers = Paper.query.filter(Paper.authors.any(id=app.current_user.id)).all()
        # TODO Add other authors too
        return render_template('index.html', current_user=app.current_user, papers=papers)

@app.route('/set_roles')
def set_roles():
    return render_template('set_roles.html')



if __name__ == '__main__':
    app.run()
