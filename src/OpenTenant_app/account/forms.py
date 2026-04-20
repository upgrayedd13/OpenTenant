from wtforms import StringField, PasswordField, BooleanField, FormField, SubmitField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

from .subforms.apartment_info_form import ApartmentInfoForm
from .subforms.personal_info_form import PersonalInfoForm
from .subforms.register_form import RegisterForm


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')


class SignupForm(FlaskForm):
    personal_info = FormField(PersonalInfoForm)
    register_info = FormField(RegisterForm)
    apartment_info = FormField(ApartmentInfoForm)

    submit = SubmitField('Submit')