"""June 2026 schema additions: cause-scoped voting, initiative ratings, watchlist

Revision ID: c7f2a4e8d0b1
Revises: b1c3e2f4a9d7
Create Date: 2026-06-01 00:00:00.000000

build-seq 3 & 4 (Pass 16):
- Vote.cause_id (nullable str, FK causes.id) — lets /causes/{id}/votes aggregate
  without joining through initiatives. Existing rows backfill from the related
  initiative.
- Vote.committed (bool default False) — distinguishes pre-commit "soft" shares
  from the locked-in commitment used by /votes/commit.
- Initiative.rating_avg (float default 0.0) + Initiative.rating_count (int)
  — denormalised rollup of the per-benefactor initiative_ratings table so
  list_initiatives doesn't have to recompute on every read.
- BenefactorAccount.watched_initiative_ids (text, JSON-encoded list) —
  per-benefactor watchlist. JSON array on SQLite; can become a join table when
  Postgres lands (Q7).
- initiative_ratings table — one row per (benefactor, initiative); upserted by
  POST /initiatives/{id}/rate. Side-effect of rating: auto-add to the
  benefactor's watchlist if not already present.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c7f2a4e8d0b1'
down_revision = 'b1c3e2f4a9d7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Vote: cause_id (nullable; backfilled in a follow-up data migration) and
    # committed flag (server-default '0' so existing rows count as soft votes).
    with op.batch_alter_table('votes') as batch_op:
        batch_op.add_column(sa.Column('cause_id', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('committed', sa.Boolean(), nullable=False, server_default='0'))
        batch_op.create_foreign_key('fk_votes_cause_id', 'causes', ['cause_id'], ['id'])

    # Backfill cause_id from the related initiative so existing votes can be
    # queried via /causes/{id}/votes immediately after the migration.
    op.execute(
        "UPDATE votes SET cause_id = (SELECT initiatives.cause_id "
        "FROM initiatives WHERE initiatives.id = votes.initiative_id) "
        "WHERE cause_id IS NULL"
    )

    # Initiative ratings rollup columns.
    with op.batch_alter_table('initiatives') as batch_op:
        batch_op.add_column(sa.Column('rating_avg', sa.Float(), nullable=False, server_default='0.0'))
        batch_op.add_column(sa.Column('rating_count', sa.Integer(), nullable=False, server_default='0'))

    # BenefactorAccount watchlist (JSON-encoded list of initiative ids).
    with op.batch_alter_table('benefactor_accounts') as batch_op:
        batch_op.add_column(sa.Column('watched_initiative_ids', sa.Text(), nullable=True))

    # initiative_ratings table — per-benefactor 0..5 stars.
    op.create_table(
        'initiative_ratings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('benefactor_id', sa.Integer(), nullable=False),
        sa.Column('initiative_id', sa.String(), nullable=False),
        sa.Column('stars', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['benefactor_id'], ['benefactor_accounts.id']),
        sa.ForeignKeyConstraint(['initiative_id'], ['initiatives.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('benefactor_id', 'initiative_id', name='uq_initiative_rating_benefactor'),
    )


def downgrade() -> None:
    op.drop_table('initiative_ratings')

    with op.batch_alter_table('benefactor_accounts') as batch_op:
        batch_op.drop_column('watched_initiative_ids')

    with op.batch_alter_table('initiatives') as batch_op:
        batch_op.drop_column('rating_count')
        batch_op.drop_column('rating_avg')

    with op.batch_alter_table('votes') as batch_op:
        batch_op.drop_constraint('fk_votes_cause_id', type_='foreignkey')
        batch_op.drop_column('committed')
        batch_op.drop_column('cause_id')
