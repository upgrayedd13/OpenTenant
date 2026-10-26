"""add_password_reset_tokens_table

Revision ID: d47be2b4c0a04c2da969e69868200d98
Revises: a09d0a86e0bc4994aa7f85c39a77
Create Date: 2026-10-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd47be2b4c0a04c2da969e69868200d98'
down_revision = 'ebaa8d6633cc'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_password_reset_tokens_id'), 'password_reset_tokens', ['id'], unique=False)
    op.create_unique_constraint('uq_password_reset_tokens_token_hash', 'password_reset_tokens', ['token_hash'])
    op.create_unique_constraint('uq_password_reset_tokens_user_id', 'password_reset_tokens', ['user_id'])
    op.create_index(op.f('ix_password_reset_tokens_user_id'), 'password_reset_tokens', ['user_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_password_reset_tokens_user_id'), table_name='password_reset_tokens')
    op.drop_constraint('uq_password_reset_tokens_user_id', 'password_reset_tokens', type_='unique')
    op.drop_constraint('uq_password_reset_tokens_token_hash', 'password_reset_tokens', type_='unique')
    op.drop_index(op.f('ix_password_reset_tokens_id'), table_name='password_reset_tokens')
    op.drop_table('password_reset_tokens')
