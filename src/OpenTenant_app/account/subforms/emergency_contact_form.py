from wtforms import Form
from wtforms import StringField, TelField
from wtforms.validators import DataRequired

class EmergencyContactForm(Form):
    emergency_contact_name = StringField(
        'Contact Name',
        validators=[DataRequired()],
        description='Lorem ipsum dolor sit amet.'
    )

    emergency_contact_phone = TelField(
        'Phone Number',
        validators=[DataRequired()],
        description='Lorem ipsum dolor sit amet.'
    )
