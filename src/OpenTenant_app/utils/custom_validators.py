from wtforms.fields.core import Field
from wtforms import ValidationError
from flask_wtf import FlaskForm
import os

from .get_config import get_config
from ..models.user.user import User


MIN_FLOOR = 7
MAX_FLOOR = 36
MIN_UNIT  = 1
MAX_UNIT  = 12
MAX_UNIT_TOP_FLOOR = 6  # top floor is special


def validate_unit_number(unit_num: int) -> None:
    floor = unit_num // 100
    unit  = unit_num  % 100

    # check the floor number
    if not (MIN_FLOOR <= floor <= MAX_FLOOR):
        raise ValidationError(f'Unit must be between floors {MIN_FLOOR} and {MAX_FLOOR}!')

    # check the unit number
    max_unit_num = MAX_UNIT_TOP_FLOOR if floor == MAX_UNIT_TOP_FLOOR else MAX_UNIT
    if not (MIN_UNIT <= unit <= max_unit_num):
        raise ValidationError(f'Unit number must be between {MIN_UNIT:02d} and {max_unit_num:02d} on floor {floor}!')


class UnitNumberValidator:
    def __call__(self, form: FlaskForm, field: Field) -> None:
        validate_unit_number(field.data)


class UsernameUniqueValidator:
    def __call__(self, form: FlaskForm, field: Field) -> None:
        if User.get_one_or_none_by(username=field.data):
            raise ValidationError(f'Username "{field.data}" is already taken!')


class EmailUniqueValidator:
    def __call__(self, form: FlaskForm, field: Field) -> None:
        if User.get_one_or_none_by(email=field.data):
            raise ValidationError(f'Email "{field.data}" is already taken!')


class UploadTokenValidator:
    def __call__(self, form: FlaskForm, field: Field) -> None:
        fullPath = os.path.join(get_config('TMP_DIR'), field.data)
        if not os.path.isfile(fullPath):
            raise ValidationError(f'Got invalid user upload token {field.data}!')
