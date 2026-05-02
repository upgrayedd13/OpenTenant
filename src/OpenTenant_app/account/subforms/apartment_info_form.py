from wtforms import DateField, IntegerField, DecimalField, StringField
from wtforms.validators import DataRequired, NumberRange, Length
from flask_wtf import FlaskForm

from ...utils.unit_number_validation import UnitNumberValidator
from ...models.lease import Lease
from ...models.user import User


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


    def create_lease(self) -> Lease:
        l = Lease()
        l.base_monthly_rent = self.base_monthly_rent.data
        l.monthly_rent_total = self.monthly_rent_total.data
        l.unit_number = self.unit_number.data
        l.start_date = self.lease_start_date.data
        l.end_date = self.lease_end_date.data
        return l

    @staticmethod
    def from_user(user: User) -> 'ApartmentInfoForm':
        form = ApartmentInfoForm()
        form.base_monthly_rent.data  = user.current_lease.base_monthly_rent
        form.monthly_rent_total.data = user.current_lease.monthly_rent_total
        form.unit_number.data        = user.current_lease.unit_number
        form.lease_start_date.data   = user.current_lease.start_date
        form.lease_end_date.data     = user.current_lease.end_date
        return form
