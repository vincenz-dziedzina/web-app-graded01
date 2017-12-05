from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/test.db'
db = SQLAlchemy(app)

authors = db.Table('authors',
   db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
   db.Column('paper_id', db.Integer, db.ForeignKey('paper.id'), primary_key=True)
)

class Score(db.Model):
    __tablename__ = "score"
    paper_id = db.Column(db.Integer, db.ForeignKey('paper.id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    rating = db.Column(db.Integer)

    reviewer = relationship("User" ,backref="paper_assocs")
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return '<User %r>' % self.email

class Paper(db.Model):
    __tablename__ = 'paper'
    id = db.Column(db.Integer, primary_key=True)

    status = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    abstract = db.Column(db.Text(500), nullable=False)

    scores = db.relationship("Score", backref="paper")
    authors = db.relationship('User', secondary=authors, lazy='subquery',
        backref=db.backref('papers', lazy=True))

    def __repr__(self):
        return '<Paper %r>' % self.title

db.drop_all()
db.create_all()

user1 = User(email="testmail@web.de", hashed_password="test")
paper1 = Paper(status="vergeben", title="testtitle", abstract="cool")
paper2 = Paper(status="vergebasdasden", title="testtitle2", abstract="cool2")

db.session.add(user1)
db.session.add(paper1)
db.session.add(paper2)
db.session.commit()

foundUser = User.query.first()
foundPaper = Paper.query.first()

foundPaper.authors.append(foundUser)
db.session.add(foundPaper)
db.session.commit()

foundUser = User.query.first()
foundPaper = Paper.query.first()

score = Score(rating=5)
score.reviewer = foundUser
score.user_id = foundUser.id
score.paper_id = foundPaper.id
foundPaper.scores.append(score)

db.session.add(score)
db.session.commit()

foundUser = User.query.first()
foundPaper = Paper.query.first()
print(foundPaper.scores[0].user_id == foundUser.id)
print(foundPaper.scores[0].paper_id == foundPaper.id)
