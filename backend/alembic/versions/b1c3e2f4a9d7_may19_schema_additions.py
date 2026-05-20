"""May 2026 schema additions: logo_url, vvv, Vote.share, Vote.org_id nullable

Revision ID: b1c3e2f4a9d7
Revises: af0d14f1a4e8
Create Date: 2026-05-19 00:00:00.000000

Changes:
- Organization.logo_url (nullable str)
- Initiative.logo_url (nullable str)
- BenefactorAccount.vvv (bool, default False) — vote-verified visual flag
- Vote.org_id → nullable (initiative-only soft votes don't require an org pick)
- Vote.share (float, default 1.0, min 0.1) — fractional vote support
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b1c3e2f4a9d7'
down_revision = 'af0d14f1a4e8'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Organization.logo_url
    with op.batch_alter_table('organizations') as batch_op:
        batch_op.add_column(sa.Column('logo_url', sa.String(), nullable=True))

    # Initiative.logo_url
    with op.batch_alter_table('initiatives') as batch_op:
        batch_op.add_column(sa.Column('logo_url', sa.String(), nullable=True))

    # BenefactorAccount.vvv
    with op.batch_alter_table('benefactor_accounts') as batch_op:
        batch_op.add_column(sa.Column('vvv', sa.Boolean(), nullable=False, server_default='0'))

    # Vote: add share, make org_id nullable
    with op.batch_alter_table('votes') as batch_op:
        batch_op.add_column(sa.Column('share', sa.Float(), nullable=False, server_default='1.0'))
        batch_op.alter_column('org_id', existing_type=sa.String(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table('votes') as batch_op:
        batch_op.alter_column('org_id', existing_type=sa.String(), nullable=False)
        batch_op.drop_column('share')

    with op.batch_alter_table('benefactor_accounts') as batch_op:
        batch_op.drop_column('vvv')

    with op.batch_alter_table('initiatives') as batch_op:
        batch_op.drop_column('logo_url')

    with op.batch_alter_table('organizations') as batch_op:
        batch_op.drop_column('logo_url')
