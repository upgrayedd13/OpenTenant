from wtforms.validators import DataRequired, EqualTo, Length
from wtforms import StringField, PasswordField
from flask_wtf import FlaskForm

from ...utils.user_validation import UsernameUniqueValidator
from ...models.user import User


class RegisterForm(FlaskForm):
    class Meta:
        csrf = False

    username = StringField(
        'Username',
        validators=[DataRequired(), UsernameUniqueValidator(), Length(max=User.str_field_len('username'))],
        description='Lorem ipsum dolor sit amet.'
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=8)],
        description='Lorem ipsum dolor sit amet.'
    )

    confirmed_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match!')],
        description='Lorem ipsum dolor sit amet.'
    )