from wtforms.validators import Optional, Length
from wtforms import StringField, TelField

from ...models.emergency_contact import EmergencyContact
from ...models.user import User
from .subform import Subform


class EmergencyContactForm(Subform):
    emergency_contact_name = StringField(
        'Contact Name (Optional)',
        validators=[Optional(), Length(max=EmergencyContact.str_field_len('name'))],
        description='Lorem ipsum dolor sit amet.'
    )

    emergency_contact_phone = TelField(
        'Phone Number (Optional)',
        validators=[Optional(), Length(max=EmergencyContact.str_field_len('phone_number'))],
        description='Lorem ipsum dolor sit amet.'
    )


    def create_emergency_contact(self) -> EmergencyContact:
        ec = EmergencyContact()
        ec.name = self.emergency_contact_name.data if self.emergency_contact_name.data else None
        ec.phone_number = self.emergency_contact_phone.data if self.emergency_contact_phone.data else None
        return ec


    @staticmethod
    def from_user(user: User) -> 'EmergencyContactForm':
        form = EmergencyContactForm()
        form.emergency_contact_name.data  = user.emergency_contact.name
        form.emergency_contact_phone.data = user.emergency_contact.phone_number
        return form
