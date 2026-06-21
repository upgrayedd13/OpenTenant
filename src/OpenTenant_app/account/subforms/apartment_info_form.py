from wtforms import DateField, IntegerField, DecimalField
from wtforms.validators import DataRequired, NumberRange
from decimal import Decimal
from datetime import date

from ...utils.custom_validators import UnitNumberValidator
from ...models.lease import Lease
from ...models.user import User
from .subform import Subform


class ApartmentInfoForm(Subform):
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
        l.base_monthly_rent  = self.base_monthly_rent.data or Decimal(0)
        l.monthly_rent_total = self.monthly_rent_total.data or Decimal(0)
        l.num_occupants      = int(self.num_occupants.data or 0)
        l.unit_number        = int(self.unit_number.data or 0)
        l.start_date         = self.lease_start_date.data or date.today()
        l.end_date           = self.lease_end_date.data
        return l


    @staticmethod
    def from_user(user: User) -> 'ApartmentInfoForm':
        form = ApartmentInfoForm()
        lease = user.current_lease
        if lease:
            form.base_monthly_rent.data  = lease.base_monthly_rent
            form.monthly_rent_total.data = lease.monthly_rent_total
            form.num_occupants.data      = lease.num_occupants
            form.unit_number.data        = lease.unit_number
            form.lease_start_date.data   = lease.start_date
            form.lease_end_date.data     = lease.end_date
        return form
