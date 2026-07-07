"""jul06 org claims + guaranteed-to-pool rate (Build Phase 2 — the claim gate)

NEW table:   org_claims — one row per (mission, org) click-through acceptance:
             the representative attestation that grants budget/sequence authority.
NEW column:  missions.guaranteed_pool_rate — NULL until claimed (frontend/crud
             fall back to settings.pool_rate_unclaimed), set to the claimed rate
             on claim. Rates are config-driven placeholders.

Revision ID: d9b7e2c4f1a8
Revises: c2e4f6a8b0d1
Create Date: 2026-07-06
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd9b7e2c4f1a8'
down_revision = 'c2e4f6a8b0d1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'org_claims',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('mission_id', sa.String(), nullable=False),
        sa.Column('org_id', sa.String(), nullable=False),
        sa.Column('ben_id', sa.Integer(), nullable=False),
        sa.Column('kind', sa.String(), nullable=False, server_default='claim'),
        sa.Column('attestation_version', sa.String(), nullable=False),
        sa.Column('member_name', sa.String(), nullable=True),
        sa.Column('member_position', sa.String(), nullable=True),
        sa.Column('accepted_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['mission_id'], ['missions.id']),
        sa.ForeignKeyConstraint(['org_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['ben_id'], ['benefactor_accounts.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('mission_id', 'org_id', name='uq_claim_mission_org'),
    )
    with op.batch_alter_table('missions') as batch:
        batch.add_column(sa.Column('guaranteed_pool_rate', sa.Float(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('missions') as batch:
        batch.drop_column('guaranteed_pool_rate')
    op.drop_table('org_claims')
