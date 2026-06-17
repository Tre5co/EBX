"""jun15 vote_events audit log + drop stale tables (build-seq 1 & 2)

Revision ID: f4a9c1d2e6b3
Revises: e8c5d2a7b491
Create Date: 2026-06-15

build-seq 1: append-only vote_events audit log feeding /admin/votes.
build-seq 2: drop the deprecated mission_metrics, reviews, initiative_ratings
tables (their models were removed). The denormalised Initiative.rating /
rating_avg / rating_count columns are intentionally KEPT — cause.html reads
them — they simply become static after the per-benefactor rating model goes.
"""
from alembic import op
import sqlalchemy as sa

revision = 'f4a9c1d2e6b3'
down_revision = 'e8c5d2a7b491'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'vote_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('election_id', sa.String(), nullable=True),
        sa.Column('cause_id', sa.String(), nullable=True),
        sa.Column('target', sa.String(), nullable=True),
        sa.Column('kind', sa.String(), nullable=False, server_default='initiative'),
        sa.Column('action', sa.String(), nullable=False),
        sa.Column('old_value', sa.String(), nullable=True),
        sa.Column('new_value', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['benefactor_accounts.id']),
        sa.ForeignKeyConstraint(['election_id'], ['initiatives.id']),
        sa.ForeignKeyConstraint(['cause_id'], ['causes.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_vote_events_created_at', 'vote_events', ['created_at'])

    # Drop deprecated tables (models removed in build-seq 2).
    for tbl in ('initiative_ratings', 'reviews', 'mission_metrics'):
        op.drop_table(tbl)


def downgrade() -> None:
    # Recreate the dropped tables (best-effort; matches their last schema).
    op.create_table(
        'mission_metrics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('mission_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('target_value', sa.Float(), nullable=False),
        sa.Column('current_value', sa.Float(), nullable=False),
        sa.Column('unit', sa.String(), nullable=True),
        sa.ForeignKeyConstraint(['mission_id'], ['missions.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('organization_id', sa.String(), nullable=False),
        sa.Column('benefactor_id', sa.Integer(), nullable=True),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('body', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id']),
        sa.ForeignKeyConstraint(['benefactor_id'], ['benefactor_accounts.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_table(
        'initiative_ratings',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('benefactor_id', sa.Integer(), nullable=False),
        sa.Column('initiative_id', sa.String(), nullable=False),
        sa.Column('stars', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['benefactor_id'], ['benefactor_accounts.id']),
        sa.ForeignKeyConstraint(['initiative_id'], ['initiatives.id']),
        sa.UniqueConstraint('benefactor_id', 'initiative_id', name='uq_initiative_rating_benefactor'),
        sa.PrimaryKeyConstraint('id'),
    )

    op.drop_index('ix_vote_events_created_at', table_name='vote_events')
    op.drop_table('vote_events')
