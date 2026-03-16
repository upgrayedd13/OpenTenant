from flask_wtf import FlaskForm
from wtforms import DateField, IntegerField, DecimalField
from wtforms.validators import DataRequired, NumberRange

from .unit_number_validation import UnitNumberValidator


class ApartmentInfoForm(FlaskForm):
    unit_number = IntegerField("Unit Number", validators=[DataRequired(), UnitNumberValidator()])
    lease_start_date = DateField('Lease Start Date', validators=[DataRequired()], format='%Y-%m-%d')
    lease_end_date = DateField('Lease End Date', validators=[DataRequired()], format='%Y-%m-%d')
    base_monthly_rent = DecimalField('Monthly Rent', validators=[DataRequired(), NumberRange(min=0)], places=2)
    monthly_rent_total = DecimalField('Monthly Total', validators=[DataRequired(), NumberRange(min=0)], places=2)
    num_occupants = IntegerField('Number of Occupants', validators=[DataRequired(), NumberRange(min=0, max=10)])