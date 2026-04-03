from wtforms.validators import DataRequired, EqualTo, Length
from wtforms import StringField
from flask_wtf import FlaskForm

from ...utils.user_validation import UsernameUniqueValidator
from ...models.user import User


class RegisterForm(FlaskForm):
    username = StringField(
        'Username',
        validators=[DataRequired(), UsernameUniqueValidator(), Length(max=User.str_field_len('username'))],
        description='Lorem ipsum dolor sit amet.'
    )

    password = StringField(
        'Password',
        validators=[DataRequired(), Length(8)],
        description='Lorem ipsum dolor sit amet.'
    )

    confirmed_password = StringField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match!')],
        description='Lorem ipsum dolor sit amet.'
    )