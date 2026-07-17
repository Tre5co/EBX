"""jul09 mission steps + projected end (§1 release-phase structure)

NEW table:   mission_steps — the release phase's STEPs. Each step carries a
             guaranteed and a potential pool (no maximums), finalized by the
             end of the budgeting phase. Resolving a step is a RESOLUTION:
             it moves the mission's credit-coin value.
NEW column:  missions.projected_end_at — the projected MISSION LENGTH end date.

Revision ID: e5c8a1d3f7b2
Revises: d9b7e2c4f1a8
Create Date: 2026-07-09
"""
from alembic import op
import sqlalchemy as sa

revision = 'e5c8a1d3f7b2'
down_revision = 'd9b7e2c4f1a8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'mission_steps',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('mission_id', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('order_num', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('guaranteed_ebx', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('potential_ebx', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('starts_at', sa.DateTime(), nullable=True),
        sa.Column('due_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='planned'),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['mission_id'], ['missions.id']),
        sa.ForeignKeyConstraint(['created_by_id'], ['benefactor_accounts.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    with op.batch_alter_table('missions') as batch:
        batch.add_column(sa.Column('projected_end_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('missions') as batch:
        batch.drop_column('projected_end_at')
    op.drop_table('mission_steps')
