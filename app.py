from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/test.db'
db = SQLAlchemy(app)

authors = db.Table('authors',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('paper_id', db.Integer, db.ForeignKey('paper.id'))
)

class Score(db.Model):
    # __tablename__ = 'score'
    paper_id = db.Column(db.Integer, db.ForeignKey('paper.id'), primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    rating = db.Column(db.Integer)
    paper = db.relationship("Paper", back_populates="reviewers")
    reviewer = db.relationship("User", back_populates="rated_papers")

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_password = db.Column(db.String(120), nullable=False)
    rated_papers = db.relationship("Score", back_populates="paper")
    papers = db.relationship("Paper", secondary="authors", back_populates="authors")

    def __repr__(self):
        return '<User %r>' % self.email

class Paper(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(120), nullable=False)
    abstract = db.Column(db.Text(500), nullable=False)
    reviewers = db.relationship("Score", back_populates="reviewer")
    authors = db.relationship("User", secondary="authors", back_populates="papers")

    def __repr__(self):
        return '<Paper %r>' % self.title

user1 = User(email="test", hashed_password="test")
paper1 = Paper(status="vergeben", title="test", abstract="cool")
paper2 = Paper(status="vergebasdasden", title="test2", abstract="cool2")
db.session.add(user1)
db.session.add(paper1)
db.session.add(paper2)
db.session.commit()
user1 = User.query.first
paper1 = Paper.query.first
paper1.authors.append(user1)
print(Paper.query.all())
