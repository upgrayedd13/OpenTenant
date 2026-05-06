"""merge heads 576ac5ec9538 and 967cc9b2f129

Revision ID: 5cac3ec24771
Revises: 576ac5ec9538, 967cc9b2f129
Create Date: 2026-05-06 11:56:39.615693

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5cac3ec24771'
down_revision = ('576ac5ec9538', '967cc9b2f129')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
