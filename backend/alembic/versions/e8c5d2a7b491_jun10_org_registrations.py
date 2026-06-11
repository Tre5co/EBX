"""jun10 org registrations/nominations (pass 34, build-seq 2)

Revision ID: e8c5d2a7b491
Revises: d3a1f7c2e5b8
Create Date: 2026-06-10
"""
from alembic import op
import sqlalchemy as sa

revision = 'e8c5d2a7b491'
down_revision = 'd3a1f7c2e5b8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'org_registrations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('kind', sa.String(), nullable=False, server_default='nomination'),
        sa.Column('org_name', sa.String(), nullable=False),
        sa.Column('website', sa.String(), nullable=False),
        sa.Column('justification', sa.Text(), nullable=False),
        sa.Column('member_name', sa.String(), nullable=True),
        sa.Column('member_position', sa.String(), nullable=True),
        sa.Column('initiative_ids', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('submitted_by_id', sa.Integer(), nullable=True),
        sa.Column('organization_id', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['submitted_by_id'], ['benefactor_accounts.id']),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('org_registrations')
