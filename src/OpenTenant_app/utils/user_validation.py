from wtforms.fields.core import Field
from wtforms import ValidationError
from flask_wtf import FlaskForm

from ..models.user import User



class UsernameUniqueValidator:
    def __call__(self, form: FlaskForm, field: Field) -> None:
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(f'Username "{field.data}" is already taken!')


class EmailUniqueValidator:
    def __call__(self, form: FlaskForm, field: Field) -> None:
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(f'Email "{field.data}" is already taken!')
