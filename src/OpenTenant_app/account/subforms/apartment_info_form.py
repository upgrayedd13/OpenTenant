from wtforms import DateField, IntegerField, DecimalField, StringField
from wtforms.validators import DataRequired, NumberRange, Length
from flask_wtf import FlaskForm

from ...utils.unit_number_validation import UnitNumberValidator
from ...models.lease import Lease


class ApartmentInfoForm(FlaskForm):
    class Meta:
        csrf = False

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

    address = StringField(
        'Address',
        validators=[DataRequired(), Length(max=Lease.str_field_len('address'))],
        description='Lorem ipsum dolor sit amet.'
    )

    def create_lease(self) -> Lease:
        l = Lease()
        l.base_monthly_rent = self.base_monthly_rent.data
        l.monthly_rent_total = self.monthly_rent_total.data
        l.unit_number = self.unit_number.data
        l.start_date = self.lease_start_date.data
        l.end_date = self.lease_end_date.data
        l.address = self.address.data
        return l
