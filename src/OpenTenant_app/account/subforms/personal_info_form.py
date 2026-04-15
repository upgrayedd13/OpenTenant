from wtforms import StringField, TelField, SelectField, EmailField
from wtforms.validators import DataRequired, Optional, Length

from ...utils.custom_validators import EmailUniqueValidator
from ...models.user_role import UserRole
from ...models.user import User
from .subform import Subform


class PersonalInfoForm(Subform):
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


    def create_user(self) -> User:
        user = User()
        user.name = self.given_name.data
        user.pronouns = self.pronouns.data if self.pronouns.data else None
        user.email = self.email.data
        user.phone_number = self.phone_number.data if self.phone_number.data else None
        user.occupation = self.occupation.data if self.occupation.data else None
        user.role = UserRole.USER
        return user


    @staticmethod
    def from_user(user: User) -> 'PersonalInfoForm':
        form = PersonalInfoForm()
        form.given_name.data = user.name
        form.pronouns.data = user.pronouns
        form.email.data = user.email
        form.phone_number.data = user.phone_number
        form.occupation.data = user.occupation
        return form
