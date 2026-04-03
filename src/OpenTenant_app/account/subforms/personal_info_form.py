from wtforms.validators import DataRequired, Optional, Length, EqualTo
from wtforms import StringField, TelField, SelectField, EmailField
from flask_wtf import FlaskForm

from ...utils.user_validation import EmailUniqueValidator
from ...models.user import User


class PersonalInfoForm(FlaskForm):
    given_name = StringField(
        'Name',
        validators=[DataRequired(), Length(max=User.str_field_len('name'))],
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
        validators=[DataRequired(), EmailUniqueValidator(), Length(max=User.str_field_len('email'))],
        description='Lorem ipsum dolor sit amet.'
    )

    phone_number = TelField(
        'Phone Number (Optional)',
        validators=[Optional(), Length(max=User.str_field_len('phone_number'))],
        description='Lorem ipsum dolor sit amet.'
    )

    occupation = StringField(
        'Occupation (Optional)',
        validators=[Optional(), Length(max=User.str_field_len('occupation'))],
        description='Lorem ipsum dolor sit amet.'
    )
