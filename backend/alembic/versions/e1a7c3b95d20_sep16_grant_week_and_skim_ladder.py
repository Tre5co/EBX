"""sep16 — grants carry a week, not a cause; the finality ladder

Jax, 2026-09-16 (INSTRUCTIONS build-seq §1):

    "Grants do not have a cause id, only a weekly id. Perpetuate this and
    delete any cause id. A cause id doesn't make sense because the active
    week's cause is different between the 2 elections."

    benefactor_accounts.grant_cause_id   DROPPED
        The week id already exists: `last_grant_week`. A granted token may enter
        the initiative election or the organization election closing that week.

The skim ladder (10% final at the ME, another 10% at the OE, 100% on budget day)
needs no column: the skims are booked into the existing `votes_p2.donated_ct`,
and budget-day finality is derived from the mission's clock
(`wallet.final_ct_of`).

Revision ID: e1a7c3b95d20
Revises: c5d8f2a91e67
Create Date: 2026-09-16
"""
from alembic import op
import sqlalchemy as sa

revision = 'e1a7c3b95d20'
down_revision = 'c5d8f2a91e67'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('benefactor_accounts') as batch:
        batch.drop_column('grant_cause_id')


def downgrade() -> None:
    with op.batch_alter_table('benefactor_accounts') as batch:
        batch.add_column(sa.Column('grant_cause_id', sa.String(), nullable=True))
