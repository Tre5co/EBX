"""P2b · Organization experience — organization accounts and applications.

ADDITIVE ONLY: two new tables, nothing existing is altered or dropped, so a
downgrade loses only organization logins and applications.

  org_accounts      the second account kind (D28): its own login, one
                    organization, admin | member (D29), no wallet.
  org_applications  the claim: answers to org_config.APPLICATION_SECTIONS.

The `memberships` reshape (rep/executive → organization accounts) and
`mission_candidacies.tiv_id` stay PROPOSED — see INSTRUCTIONS › P2b.

Revision ID: a7c4e2f9b1d3
Revises: e3b9c7a1d4f2
Create Date: 2026-10-02
"""
from alembic import op
import sqlalchemy as sa

revision = 'a7c4e2f9b1d3'
down_revision = 'e3b9c7a1d4f2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'org_accounts',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('org_id', sa.String(), sa.ForeignKey('organizations.id'), nullable=False, index=True),
        sa.Column('email', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('handle', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('pass_hash', sa.String(), nullable=False),
        sa.Column('display_name', sa.String(), nullable=True),
        sa.Column('position', sa.String(), nullable=True),
        sa.Column('role', sa.String(), nullable=False, server_default='member'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('is_test', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_by_id', sa.Integer(), sa.ForeignKey('org_accounts.id'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        'org_applications',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('org_id', sa.String(), sa.ForeignKey('organizations.id'), nullable=False, index=True),
        sa.Column('account_id', sa.Integer(), sa.ForeignKey('org_accounts.id'), nullable=True),
        sa.Column('answers', sa.JSON(), nullable=True),
        sa.Column('attestation_version', sa.String(), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='pending'),
        sa.Column('created_org', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('review_note', sa.Text(), nullable=True),
        sa.Column('reviewed_by_id', sa.Integer(), sa.ForeignKey('benefactor_accounts.id'), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('org_applications')
    op.drop_table('org_accounts')
