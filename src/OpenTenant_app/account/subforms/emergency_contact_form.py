from wtforms.validators import DataRequired
from wtforms import StringField, TelField
from flask_wtf import FlaskForm

class EmergencyContactForm(FlaskForm):
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
