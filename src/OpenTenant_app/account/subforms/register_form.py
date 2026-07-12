from wtforms.validators import DataRequired, EqualTo, Length
from wtforms import StringField, PasswordField, HiddenField

from ...utils.custom_validators import UploadTokenValidator, UsernameUniqueValidator
from ...models.user.user import User
from .subform import Subform


class RegisterForm(Subform):
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

    # this is a hidden field so no label or description is needed
    upload_token = HiddenField(
        validators=[DataRequired(), UploadTokenValidator()]
    )
