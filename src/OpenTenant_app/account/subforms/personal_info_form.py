from wtforms import StringField, TelField, SelectField, EmailField
from wtforms.validators import DataRequired, Optional, Length
from flask_wtf import FlaskForm


class PersonalInfoForm(FlaskForm):
    given_name = StringField(
        'Name',
        validators=[DataRequired()],
        description='Lorem ipsum dolor sit amet.'
    )

    pronouns = SelectField(
        'Pronouns (Optional)',
        validators=[Optional(), Length(min=1, message='Must make a selection!')],
        description='Lorem ipsum dolor sit amet.',
        choices=['', 'He/Him', 'She/Her', 'They/Them', 'Other'],
        default=''
    )

    email = EmailField(
        'Email',
        validators=[DataRequired()],
        description='Lorem ipsum dolor sit amet.'
    )

    phone_number = TelField(
        'Phone Number',
        validators=[Optional()],
        description='Lorem ipsum dolor sit amet.'
    )

    occupation = StringField(
        'Occupation (Optional)',
        validators=[Optional()],
        description='Lorem ipsum dolor sit amet.'
    )