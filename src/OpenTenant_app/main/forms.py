from wtforms.validators import DataRequired, Optional, Email
from wtforms import StringField, EmailField, TextAreaField
from flask_wtf import FlaskForm


class BugReportForm(FlaskForm):
    name = StringField(
        'Name',
        validators=[],
        description='How should we address you if we need to reach out?'
    )

    email = EmailField(
        'Email',
        validators=[Optional(), Email()],
        description='If you\'d like a reply, let us know how to contact you.'
    )

    description = TextAreaField(
        'Describe the Issue',
        validators=[DataRequired()],
        description='Describe the bug or problem.',
        render_kw={'rows': 5}
    )
