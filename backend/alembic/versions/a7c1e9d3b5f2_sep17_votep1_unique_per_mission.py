"""sep17 — votes_p1 unique per (ben, mission, tiv)

INSTRUCTIONS build-seq §2 (Elections). The old UNIQUE(ben_id, tiv_id) spanned
missions. `_relist_losers` moves a losing initiative into its cause's next
election, so a benefactor who backed it once could never back it again: the
insert collided and the slate PUT failed. The key is per mission now.

Revision ID: a7c1e9d3b5f2
Revises: f7b2d9e41c63
Create Date: 2026-09-17
"""
from alembic import op

revision = 'a7c1e9d3b5f2'
down_revision = 'f7b2d9e41c63'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('votes_p1', recreate='always') as batch:
        batch.drop_constraint('uq_votep1_ben_tiv', type_='unique')
        batch.create_unique_constraint('uq_votep1_ben_mission_tiv',
                                       ['ben_id', 'mission_id', 'tiv_id'])


def downgrade() -> None:
    with op.batch_alter_table('votes_p1', recreate='always') as batch:
        batch.drop_constraint('uq_votep1_ben_mission_tiv', type_='unique')
        batch.create_unique_constraint('uq_votep1_ben_tiv', ['ben_id', 'tiv_id'])
