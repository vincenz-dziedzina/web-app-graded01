from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField, PasswordField, SelectField, IntegerField
from wtforms.validators import *

class PaperSubmission(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=200)])
    abstract = StringField('Abstract', validators=[DataRequired(), Length(min=5, max=500)])
    authors = SelectMultipleField('Other authors', coerce=int)

class Login(FlaskForm):
    email =  StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=30)])

class Registration(FlaskForm):
    email =  StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=30)])

class SetStatus(FlaskForm):
    status =  SelectField('Status', coerce=str)

class SetReviewer(FlaskForm):
    reviewer =  SelectMultipleField('Reviewer')

class SetRating(FlaskForm):
    rating = IntegerField("Rating", validators=[NumberRange(min=-2, max=2)])
