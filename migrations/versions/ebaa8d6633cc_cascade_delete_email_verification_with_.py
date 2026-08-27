"""Cascade delete email verification with user

Revision ID: ebaa8d6633cc
Revises: bb9e0752cb18
Create Date: 2026-08-27 01:35:38.575001

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ebaa8d6633cc'
down_revision = 'bb9e0752cb18'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('email_verifications') as batch_op:
        batch_op.drop_constraint(
            'email_verifications_user_id_fkey',
            type_='foreignkey'
        )
        batch_op.create_foreign_key(
            'email_verifications_user_id_fkey',
            'users',
            ['user_id'],
            ['id'],
            ondelete='CASCADE'
        )

def downgrade():
    with op.batch_alter_table('email_verifications') as batch_op:
        batch_op.drop_constraint(
            'email_verifications_user_id_fkey',
            type_='foreignkey'
        )
        batch_op.create_foreign_key(
            'email_verifications_user_id_fkey',
            'users',
            ['user_id'],
            ['id']
        )
