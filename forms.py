from flask_wtf import FlaskForm
from wtforms import StringField, SelectMultipleField, PasswordField, SelectField
from wtforms.validators import DataRequired

class PaperSubmission(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    abstract = StringField('Abstract', validators=[DataRequired()])
    authors = SelectMultipleField('Authors')

class Login(FlaskForm):
    email =  StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class Registration(FlaskForm):
    email =  StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class SetStatus(FlaskForm):
    status =  SelectField('Status', coerce=str)

class SetReviewer(FlaskForm):
    reviewer =  SelectMultipleField('Reviewer')
