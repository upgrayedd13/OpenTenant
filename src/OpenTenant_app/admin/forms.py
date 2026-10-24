from wtforms import SelectField, StringField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Optional

from flask_wtf import FlaskForm


class ElevatorStatusForm(FlaskForm):
    elevator_id = HiddenField('Elevator ID')
    
    car_1_status = SelectField(
        'Car 1 Status',
        choices=[
            ('working', 'WORKING'),
            ('non-working', 'NON-WORKING'),
            ('reserved', 'RESERVED'),
        ],
        validators=[Optional()]
    )
    car_1_comment = StringField(
        'Car 1 Comment',
        validators=[Optional(), Length(max=160)]
    )
    
    car_2_status = SelectField(
        'Car 2 Status',
        choices=[
            ('working', 'WORKING'),
            ('non-working', 'NON-WORKING'),
            ('reserved', 'RESERVED'),
        ],
        validators=[Optional()]
    )
    car_2_comment = StringField(
        'Car 2 Comment',
        validators=[Optional(), Length(max=160)]
    )
    
    car_3_status = SelectField(
        'Car 3 Status',
        choices=[
            ('working', 'WORKING'),
            ('non-working', 'NON-WORKING'),
            ('reserved', 'RESERVED'),
        ],
        validators=[Optional()]
    )
    car_3_comment = StringField(
        'Car 3 Comment',
        validators=[Optional(), Length(max=160)]
    )
    
    submit = SubmitField('Update Elevator Statuses')
