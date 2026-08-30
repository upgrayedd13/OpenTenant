from wtforms.validators import DataRequired, EqualTo, Length, Optional
from wtforms import StringField, PasswordField, HiddenField, SelectField

from ...utils.custom_validators import UploadTokenValidator, UsernameUniqueValidator, EmailUniqueValidator
from ...models.user import User
from ...models.user_role import UserRole
from flask_wtf import FlaskForm


class BotAccountForm(FlaskForm):
    name = StringField(
        'Name',
        validators=[DataRequired(), Length(max=User.str_field_len('name'))],
        description='Bot account display name'
    )

    email = StringField(
        'Email',
        validators=[DataRequired(), EmailUniqueValidator(), Length(max=User.str_field_len('email'))],
        description='Bot account email address'
    )

    username = StringField(
        'Username',
        validators=[DataRequired(), UsernameUniqueValidator(), Length(max=User.str_field_len('username'))],
        description='Bot account username'
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=8)],
        description='Bot account password'
    )

    confirmed_password = PasswordField(
        'Confirm Password',
        validators=[DataRequired(), EqualTo('password', message='Passwords must match!')],
        description='Confirm the bot account password'
    )

    role = SelectField(
        'User Role',
        validators=[DataRequired()],
        description='Select the role for this bot account',
        choices=[
            (10, 'User'),
            (11, 'Super User'),
            (20, 'Admin'),
            (30, 'Super Admin')
        ],
        default=10
    )

    def create_user(self):
        user = User()
        user.name = self.name.data
        user.email = self.email.data
        user.username = self.username.data
        user.set_password(self.password.data)
        user.role = UserRole(int(self.role.data))
        user.email_verified = True
        return user
