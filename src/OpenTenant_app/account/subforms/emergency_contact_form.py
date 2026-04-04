from wtforms.validators import Optional, Length
from wtforms import StringField, TelField
from flask_wtf import FlaskForm

from ...models.emergency_contact import EmergencyContact


class EmergencyContactForm(FlaskForm):
    class Meta:
        csrf = False

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
