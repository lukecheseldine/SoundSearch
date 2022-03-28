from email import message
import email_validator
from wtforms import Form, StringField, PasswordField, validators

class RegistrationForm(Form):
    email = StringField('Email', [
        validators.Email(message='Invalid email address'),
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
    email = StringField('Email', [
        validators.Email(message='Invalid email address'),
        validators.DataRequired()
    ])
    password = PasswordField('Password', [
        validators.DataRequired()
    ])