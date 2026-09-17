"""sep16b — the bot signature: benefactor_accounts.is_test

INSTRUCTIONS build-seq §2, "Is_test signature on bots". Accounts driven by
`scripts/bots/ebx_bots.py` carry `is_test = true`. It is set at signup only when
the request carries the server's `EBX_BOT_KEY`, or by staff through
`POST /admin/accounts/{id}/test`.

Revision ID: f7b2d9e41c63
Revises: e1a7c3b95d20
Create Date: 2026-09-16
"""
from alembic import op
import sqlalchemy as sa

revision = 'f7b2d9e41c63'
down_revision = 'e1a7c3b95d20'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('benefactor_accounts') as batch:
        batch.add_column(sa.Column('is_test', sa.Boolean(), nullable=False,
                                   server_default=sa.false()))


def downgrade() -> None:
    with op.batch_alter_table('benefactor_accounts') as batch:
        batch.drop_column('is_test')
