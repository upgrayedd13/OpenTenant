"""add_ip_address_to_password_reset_tokens

Revision ID: 743d182174754f58bd352fa684031311
Revises: d47be2b4c0a04c2da969e69868200d98
Create Date: 2026-10-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '743d182174754f58bd352fa684031311'
down_revision = 'd47be2b4c0a04c2da969e69868200d98'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('password_reset_tokens', sa.Column('ip_address', sa.String(length=45), nullable=True))


def downgrade():
    op.drop_column('password_reset_tokens', 'ip_address')
