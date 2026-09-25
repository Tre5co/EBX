"""sep24 — initiative_slugs: every address an initiative has had (D13)

build-seq P1 review (2026-09-24), D13: "Old titles of the initiative should
also link to the new title." Mission pages live at /m/<initiative-title-slug>;
a stored slug per title, kept after a rename, is what lets an old link forward
to the new one. The rows themselves are written by `crud.ensure_slugs` at
startup (deterministic from the titles), not here, so this migration is only
the table.

Revision ID: c9e4a7d2b6f1
Revises: a7c1e9d3b5f2
Create Date: 2026-09-24
"""
from alembic import op
import sqlalchemy as sa

revision = 'c9e4a7d2b6f1'
down_revision = 'a7c1e9d3b5f2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'initiative_slugs',
        sa.Column('slug', sa.String(), primary_key=True),
        sa.Column('tiv_id', sa.String(), sa.ForeignKey('initiatives.id'), nullable=False),
        sa.Column('is_current', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_index('ix_initiative_slugs_tiv_id', 'initiative_slugs', ['tiv_id'])


def downgrade() -> None:
    op.drop_index('ix_initiative_slugs_tiv_id', table_name='initiative_slugs')
    op.drop_table('initiative_slugs')
