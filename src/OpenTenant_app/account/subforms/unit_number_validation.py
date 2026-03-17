from flask_wtf import FlaskForm
from wtforms.fields.core import Field
from wtforms import ValidationError

class UnitNumberValidator:
    def __init__(self, min_floor: int=7, max_floor: int=36, min_unit: int=1, max_unit: int=12) -> None:
        self.min_floor = min_floor
        self.max_floor = max_floor
        self.min_unit = min_unit
        self.max_unit = max_unit


    def __call__(self, form: FlaskForm, field: Field) -> None:
        value = field.data
        floor = value // 100
        unit = value % 100

        if not (self.min_floor <= floor <= self.max_floor and self.min_unit <= unit <= self.max_unit):
            raise ValidationError(f"Unit must be between floors {self.min_floor} and {self.max_floor}"
                                  f"and unit {self.min_unit:02d} and {self.max_unit:02d}.")