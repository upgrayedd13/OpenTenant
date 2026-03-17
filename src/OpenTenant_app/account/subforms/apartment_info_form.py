from wtforms import Form
from wtforms import DateField, IntegerField, DecimalField
from wtforms.validators import DataRequired, NumberRange

from .unit_number_validation import UnitNumberValidator


class ApartmentInfoForm(Form):
    unit_number = IntegerField(
        'Unit Number', 
        validators=[DataRequired(), UnitNumberValidator()],
        description='Lorem ipsum dolor sit amet.'
    )

    lease_start_date = DateField(
        'Lease Start Date',
        validators=[DataRequired()],
        format='%Y-%m-%d',
        description='Lorem ipsum dolor sit amet.'
    )

    lease_end_date = DateField(
        'Lease End Date',
        validators=[DataRequired()],
        format='%Y-%m-%d',
        description='Lorem ipsum dolor sit amet.'
    )

    base_monthly_rent = DecimalField(
        'Monthly Rent',
        validators=[DataRequired(), NumberRange(min=0)],
        places=2,
        description='Lorem ipsum dolor sit amet.'
    )

    monthly_rent_total = DecimalField(
        'Monthly Total',
        validators=[DataRequired(), NumberRange(min=0)],
        places=2,
        description='Lorem ipsum dolor sit amet.'
    )

    num_occupants = IntegerField(
        'Number of Occupants',
        validators=[DataRequired(), NumberRange(min=0, max=10)],
        description='Lorem ipsum dolor sit amet.'
    )
