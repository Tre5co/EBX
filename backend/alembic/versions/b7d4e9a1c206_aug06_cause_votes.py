"""aug06 cause votes (§5 — the cause election gets a backend)

NEW table:   cause_votes — one benefactor's vote, for one WEEK, on which cause
             should hold an upcoming window. Unique per (ben, slot, week).
NEW columns: causes.status ('active' | 'suggested' | 'retired'),
             causes.proposed_by_id, causes.created_at.
ALTERED:     causes.index becomes NULLABLE — a suggested cause holds no window
             until it wins one.

The contest runs SEVEN weeks but is advertised as six: week 1 aggregates the
six weeks before it opened. A challenger takes a week with >50% of that week's
votes; taking all seven replaces the incumbent for that window.

Revision ID: b7d4e9a1c206
Revises: a1b2c3d4e5f6
Create Date: 2026-08-06
"""
from alembic import op
import sqlalchemy as sa

revision = 'b7d4e9a1c206'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'cause_votes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('ben_id', sa.Integer(), nullable=False),
        sa.Column('slot', sa.Integer(), nullable=False),
        sa.Column('cause_id', sa.String(), nullable=False),
        sa.Column('week_start', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(['ben_id'], ['benefactor_accounts.id'], ),
        sa.ForeignKeyConstraint(['cause_id'], ['causes.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ben_id', 'slot', 'week_start', name='uq_cause_vote_ben_slot_week'),
    )
    op.create_index('ix_cause_votes_slot_week', 'cause_votes', ['slot', 'week_start'])

    # SQLite can't ALTER a column in place — batch_alter_table rebuilds the
    # table, which is also how `index` loses its NOT NULL.
    with op.batch_alter_table('causes') as batch:
        batch.add_column(sa.Column('status', sa.String(), server_default='active', nullable=False))
        batch.add_column(sa.Column('proposed_by_id', sa.Integer(), nullable=True))
        batch.add_column(sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=True))
        batch.alter_column('index', existing_type=sa.Integer(), nullable=True)
        batch.create_foreign_key('fk_causes_proposed_by', 'benefactor_accounts', ['proposed_by_id'], ['id'])


def downgrade() -> None:
    op.drop_index('ix_cause_votes_slot_week', table_name='cause_votes')
    op.drop_table('cause_votes')
    with op.batch_alter_table('causes') as batch:
        batch.drop_constraint('fk_causes_proposed_by', type_='foreignkey')
        batch.drop_column('created_at')
        batch.drop_column('proposed_by_id')
        batch.drop_column('status')
        batch.alter_column('index', existing_type=sa.Integer(), nullable=False)
