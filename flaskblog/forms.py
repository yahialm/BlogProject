from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SubmitField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User, Post
from flask_login import current_user

# By creating a new instance of RegistrationForm we create new fields for users

class RegistrationForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    # Users can register themselves with emails that maybe are already used by another users so to solve this problem we create this two functions below , one to check if the username entered is already in our database and the other to check if this email is already existant

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            # show error message
            raise ValidationError('That username is taken. Use a new one instead')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            #show error message
            raise ValidationError('That email is taken. Use a new one instead')


# Same for LoginForm

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


# This form is dedicated for the account page where the user can update his personal informations 

class AccountUpdateForm(FlaskForm):
    username = StringField('Username',validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',validators=[DataRequired(), Email()])
    submit = SubmitField('Save & Update')

    # Suppose the user enter the same credentiels , wwe dont need to update his personal informations since they are the same . So before trying to update we need to check if the inpuuts are the same as the infos stored in the database. This is why the first line is added for each of the functions below

    def validate_username(self, username):
        if current_user.username != username.data:
            user = User.query.filter_by(username=username.data).first()
            if user :
                # show error message
                raise ValidationError('That username is taken. Use a new one instead')

    def validate_email(self, email):
        if current_user.email != email.data:
            user = User.query.filter_by(email=email.data).first()
            if user:
                #show error message
                raise ValidationError('That email is taken. Use a new one instead')
            

# Create the new post form 

class PostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')