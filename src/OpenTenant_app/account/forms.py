from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, FormField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo

from .subforms.apartment_info_form import ApartmentInfoForm
from .subforms.emergency_contact_form import EmergencyContactForm
from .subforms.personal_info_form import PersonalInfoForm

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password_confirm = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])


class LeaseForm(FlaskForm):
    personal_info = FormField(PersonalInfoForm)
    emergency_contact = FormField(EmergencyContactForm)
    apartment_info = FormField(ApartmentInfoForm)
    
    submit = SubmitField('Submit')