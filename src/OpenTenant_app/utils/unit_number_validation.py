from wtforms.fields.core import Field
from wtforms import ValidationError
from flask_wtf import FlaskForm

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