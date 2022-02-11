from email import message
import email_validator
from wtforms import Form, StringField, PasswordField, validators, EmailField

class RegistrationForm(Form):
    username = StringField('Username', [
        validators.Length(max=25, message="Username must be less than 25 characters"),
        validators.DataRequired()
    ])
    email = EmailField('Email', [
        validators.Email(message="Please use a valid email address"),
        validators.DataRequired()
    ])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match')
    ])
    confirm = PasswordField('Confirm password', [
        validators.DataRequired()
    ])

class LoginForm(Form):
    username = StringField('Username', [
        validators.Length(max=25, message="Username must be less than 25 characters"),
        validators.DataRequired()
    ])
    password = PasswordField('Password', [
        validators.DataRequired()
    ])