from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms.validators import DataRequired,Length, Email,EqualTo, ValidationError
from crr.models import User
from flask_login import current_user

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                validators=[DataRequired(), Length(min=2,max=20)])
    userrole = SelectField(u'Role', choices = [('User','User'), ('Agent','Agent'), ('Admin','Admin')],
                validators=[DataRequired()])            
    email = StringField('Email',
                validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
                validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', 
                validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self,username):

        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That Username is taken. Please choose a different one.')

    def validate_email(self,email):

        email = User.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('An account already exists with that Email.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
                validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                validators=[DataRequired(), Length(min=2,max=20)])
    email = StringField('Email',
                validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

    def validate_username(self,username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That Username is taken. Please choose a different one.')
    
    def validate_email(self,email):
        if email.data != current_user.email:
            email = User.query.filter_by(email=email.data).first()
            if email:
                raise ValidationError('An account already exists with that Email.')


class TicketForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired()])
    status = StringField('Status')
    agent_id = StringField('Available Agent')
    content = TextAreaField('Content',validators=[DataRequired()])
    submit = SubmitField('Ticket')
    
class TicketUpdateForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired()] )
    status = SelectField(u'Status', coerce=str, validators=[DataRequired()] )
    agent_id = StringField('Available Agent')
    content = TextAreaField('Content',validators=[DataRequired()] )
    submit = SubmitField('Ticket')

class TicketAssignForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired()] )
    status = SelectField('Status')
    agent_id = SelectField(u'Available Agent', coerce=int, validators=[DataRequired()])
    content = TextAreaField('Content',validators=[DataRequired()] )
    submit = SubmitField('Ticket')

class RequestResetForm(FlaskForm):
    email = StringField('Email',
                validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')

    def validate_email(self,email):

        user = User.query.filter_by(email=email.data).first()
        if user is None:
            raise ValidationError('There is no account with that email. You must register first.')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', 
                validators=[DataRequired()])
    confirm_password = PasswordField('Confirm New Password', 
                validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')