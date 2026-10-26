from wtforms import StringField, PasswordField, BooleanField, FormField, SubmitField, EmailField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from flask_wtf import FlaskForm

from .subforms.apartment_info_form import ApartmentInfoForm
from .subforms.personal_info_form import PersonalInfoForm
from .subforms.register_form import RegisterForm
from ..models.user import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')


class ForgotPasswordForm(FlaskForm):
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    submit = SubmitField('Send Reset Link')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Reset Password')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password', message='Passwords must match.')])
    submit = SubmitField('Change Password')


class SignupForm(FlaskForm):
    personal_info = FormField(PersonalInfoForm)
    register_info = FormField(RegisterForm)
    # TODO: Add apartment info back in eventually
    # apartment_info = FormField(ApartmentInfoForm)

    submit = SubmitField('Submit')


    @staticmethod
    def from_user(user: User) -> 'SignupForm':
        form = SignupForm()
        form.personal_info = PersonalInfoForm.from_user(user)
        # form.apartment_info = ApartmentInfoForm.from_user(user)
        return form


    def disable_editing(self) -> None:
        self.personal_info.disable_editing()
        self.register_info.disable_editing()
        # self.apartment_info.disable_editing()


    def enable_editing(self) -> None:
        self.personal_info.enable_editing()
        self.register_info.enable_editing()
        # self.apartment_info.enable_editing()
