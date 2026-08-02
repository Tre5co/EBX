"""jul19 post two-tier type (category=super, type=sub)

Adds `posts.type` (the SUBcategory) and repurposes `posts.category` as the
SUPERcategory. Backfills existing rows onto the settled taxonomy:

    context     -> mission_support / context
    analysis    -> mission_support / analysis
    case        -> review          / case
    evaluation  -> review          / evaluation

Org/staff categories (org_update, mission_update, testimonial, editorial,
headline, resolution) are left as-is with a null `type`. New benefactor types
(investigation; budgeting's service/supply/support) have no historical rows, so
no backfill is needed for them. `posts.stance` is left in place but is no longer
used (case for/against, evaluation positive/negative, and S/S/S-on-context are
retired) — dropping it is deferred to avoid a destructive change.

Source of truth for the taxonomy: backend/app/post_config.py.

Revision ID: a1b2c3d4e5f6
Revises: e5c8a1d3f7b2
Create Date: 2026-07-19
"""
from alembic import op
import sqlalchemy as sa

revision = 'a1b2c3d4e5f6'
down_revision = 'e5c8a1d3f7b2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('posts', sa.Column('type', sa.String(), nullable=True))
    # Backfill category -> (category, type). Order doesn't matter (disjoint).
    op.execute("UPDATE posts SET category='mission_support', type='context'    WHERE category='context'")
    op.execute("UPDATE posts SET category='mission_support', type='analysis'   WHERE category='analysis'")
    op.execute("UPDATE posts SET category='review',          type='case'       WHERE category='case'")
    op.execute("UPDATE posts SET category='review',          type='evaluation' WHERE category='evaluation'")


def downgrade() -> None:
    op.execute("UPDATE posts SET category='context'    WHERE category='mission_support' AND type='context'")
    op.execute("UPDATE posts SET category='analysis'   WHERE category='mission_support' AND type='analysis'")
    op.execute("UPDATE posts SET category='case'       WHERE category='review'          AND type='case'")
    op.execute("UPDATE posts SET category='evaluation' WHERE category='review'          AND type='evaluation'")
    op.drop_column('posts', 'type')
