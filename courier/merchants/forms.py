#users/froms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, EqualTo, Email, ValidationError, Length


from courier.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Log In')


class RegisterFrom(FlaskForm):
    email = StringField('Email', validators=[DataRequired(),Email()])
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    mobile_number = StringField('Mobile Number', validators=[DataRequired()])
    address = StringField('Pickup Address', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('pass_confirm', "Password doesn't match!")])
    pass_confirm = PasswordField('Confirm Password', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, email):
        user =  User.query.filter_by(email = email.data).first()
        if user:
            raise ValidationError('This email already registered! Try another')

    def validate_username(self, username):
        user =  User.query.filter_by(username = username.data).first()

        if user:    
            raise ValidationError('This username already taken! Try another')


class PickupRequest(FlaskForm):
    receipient_name = StringField('Receipient Name', validators=[DataRequired()])
    receipient_number = StringField('Receipient Number', validators=[DataRequired()])
    select_zone = SelectField('Select Zone', choices=[])
    select_weight = SelectField('Select Weight (KG)', choices=[])
    receipient_address = TextAreaField('Receipient Address', validators=[DataRequired()])
    collectable_amount = StringField('Collectable Amount', validators=[DataRequired()])
    submit = SubmitField('Pick-up Request')