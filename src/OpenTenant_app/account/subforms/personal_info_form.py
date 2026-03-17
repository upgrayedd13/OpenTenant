from wtforms import Form
from wtforms import StringField, TelField, SelectField, EmailField
from wtforms.validators import DataRequired, Optional, Length


class PersonalInfoForm(Form):
    first_name = StringField(
        'First Name',
        validators=[DataRequired()],
        description='Lorem ipsum dolor sit amet.'
    )
    
    last_name = StringField(
        'Last Name',
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
        validators=[DataRequired()],
        description='Lorem ipsum dolor sit amet.'
    )

    contact_method = SelectField(
        'Preferred Contact Method',
        validators=[DataRequired(), Length(min=1, message='Must make a selection!')],
        description='Lorem ipsum dolor sit amet.',
        choices=['', 'Email', 'Phone'],
        default=''
    )

    occupation = StringField(
        'Occupation (Optional)',
        validators=[Optional()],
        description='Lorem ipsum dolor sit amet.'
    )