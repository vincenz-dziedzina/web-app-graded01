from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField, PasswordField, SelectField, IntegerField, TextAreaField
from wtforms.validators import *
from helper_functions import Status

class PaperSubmission(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=5, max=200)])
    abstract = TextAreaField('Abstract', validators=[DataRequired(), Length(min=5, max=2000)])
    authors = SelectMultipleField('Other authors', coerce=int)

class Login(FlaskForm):
    email =  StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=30)])

class Registration(FlaskForm):
    email =  StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=5, max=30)])

class SetStatus(FlaskForm):
    status =  SelectField('Status', coerce=str, validators=[DataRequired(), AnyOf([Status.UNDER_REVIEW, Status.ACCEPTED, Status.REJECTED])])

class SetReviewer(FlaskForm):
    reviewer =  SelectMultipleField('Reviewer', validators=[DataRequired()])

class SetRating(FlaskForm):
    rating = IntegerField("Rating", validators=[NumberRange(min=-2, max=2)])
