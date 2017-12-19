from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash
from settings import db

authors = db.Table('authors',
   db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
   db.Column('paper_id', db.Integer, db.ForeignKey('paper.id'), primary_key=True)
)

class Score(db.Model):
    __tablename__ = "score"
    left_id = db.Column(db.Integer, db.ForeignKey('paper.id'), primary_key=True)
    right_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    rating = db.Column(db.Integer, default=0)
    # relationships
    reviewer = relationship("User", back_populates="scored_papers")
    paper = relationship("Paper", back_populates="reviewers")

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_password = db.Column(db.String(500), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)
    is_reviewer = db.Column(db.Boolean, nullable=False, default=False)
    # relationships
    scored_papers = db.relationship("Score", back_populates="reviewer")

    def __repr__(self):
        return '<User %r>' % self.email

class Paper(db.Model):
    __tablename__ = 'paper'
    id = db.Column(db.Integer, primary_key=True)

    status = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    abstract = db.Column(db.Text(500), nullable=False)
    # relationships
    authors = db.relationship('User', secondary=authors, lazy='subquery', backref=db.backref('papers', lazy=True))
    reviewers = db.relationship("Score", back_populates="paper")
    scores = db.relationship("Score", back_populates="paper")

    def has_reviewer(self, user):
        for reviewer in self.reviewers:
            if reviewer.reviewer.id == user.id:
                return True
        return False

    def __repr__(self):
        return '<Paper %r>' % self.title

def seed_database():
    db.drop_all()
    db.create_all()
    hashed_password = generate_password_hash("password")
    user1 = User(email="testmail1@web.de", hashed_password=hashed_password)
    user2 = User(email="testmail3@web.de", hashed_password=hashed_password)
    admin1 = User(email="conferencechair@web.de", hashed_password=hashed_password, is_admin=True)
    paper1 = Paper(status="vergeben", title="testtitle", abstract="cool")
    paper2 = Paper(status="vergebasdasden", title="testtitle2", abstract="cool2")

    db.session.add(user1)
    db.session.add(user2)
    db.session.add(admin1)
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
    score.paper = foundPaper

    #
    # score = Score(rating=10)
    # score.reviewer=User.query.all()[1]
    # score.paper = foundPaper
    #
    # db.session.add(score)
    # db.session.commit()
    #
    # foundUser = User.query.first()
    # foundPaper = Paper.query.first()
    print(score.reviewer)
    print(score.paper)
    print(score.reviewer.scored_papers[0])
    print(score.paper.reviewers[0].reviewer)
    # print("reviewers: ", foundPaper.scores)
    # print(foundPaper.scores[0].reviewer.id == foundUser.id)
    # print(foundPaper.scores[0].paper.id == foundPaper.id)

# seed_database()
