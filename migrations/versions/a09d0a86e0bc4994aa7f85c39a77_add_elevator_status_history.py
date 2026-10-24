"""Add elevator_status_history table

Revision ID: 09d0a86a-e0bc-4994-aa7f-85c39a77
Revises: bb9e0752cb18
Create Date: 2026-10-23 23:08:06.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '09d0a86a-e0bc-4994-aa7f-85c39a77'
down_revision = 'bb9e0752cb18'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'elevator_status_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('elevator_id', sa.Integer(), nullable=False),
        sa.Column('car_number', sa.Integer(), nullable=False),
        sa.Column('old_status', sa.String(length=20), nullable=True),
        sa.Column('new_status', sa.String(length=20), nullable=False),
        sa.Column('changed_by_user_id', sa.Integer(), nullable=True),
        sa.Column('comment', sa.String(length=160), nullable=True),
        sa.ForeignKeyConstraint(['elevator_id'], ['elevators.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['changed_by_user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_elevator_status_history_elevator_id'), 'elevator_status_history', ['elevator_id'], unique=False)
    op.create_index(op.f('ix_elevator_status_history_car_number'), 'elevator_status_history', ['car_number'], unique=False)
    op.create_index(op.f('ix_elevator_status_history_changed_by_user_id'), 'elevator_status_history', ['changed_by_user_id'], unique=False)
    op.create_unique_constraint('uq_elevator_status_history_elevator_created_at', 'elevator_status_history', ['elevator_id', 'created_at'])


def downgrade():
    op.drop_constraint('uq_elevator_status_history_elevator_created_at', 'elevator_status_history', type_='unique')
    op.drop_index(op.f('ix_elevator_status_history_changed_by_user_id'), table_name='elevator_status_history')
    op.drop_index(op.f('ix_elevator_status_history_car_number'), table_name='elevator_status_history')
    op.drop_index(op.f('ix_elevator_status_history_elevator_id'), table_name='elevator_status_history')
    op.drop_table('elevator_status_history')
