"""aug12 budgeting line items

Jax's budgeting spec (docs/structure.md, cause.html backlog) replaces the
free-text budgeting suggestion with a COSTED LIST. A benefactor picks one of
service / supply / support and fills a row; the post carries the list of rows,
and the three kinds render as three tables:

    service   Job    | hourly_rate | days_needed    🛠 Labor required
    supply    Item   | supplier    | cost           📦 Commodities required
    support   Item                                  🤝 Connections required

`line_items` is that list — JSON, one object per row, `kind` matching the
post's type. It is nullable and null everywhere outside budgeting.

WHY A COLUMN RATHER THAN TEXT IN THE BODY. The rows are the thing the budget
builder ranks and sums: an hourly rate that only exists inside prose cannot be
totalled, and the mission page has to add these up to build a plan. Storing
them as text would mean re-parsing the same strings in every reader.

WHAT IT DOES TO THE ESTIMATE RULE. `est_setup_days` / `est_cost_usd` (added
2026-08-08) stay, and stay required for budgeting — but they may now be
DERIVED from the rows instead of typed: setup = Σ days_needed, cost =
Σ (rate × days × 8h) for service and Σ cost for supply. crud.create_post fills
them from `line_items` when they are absent, so a costed list satisfies the
"a suggestion is costed or it is not a suggestion" rule on its own.

Revision ID: a1f6b3c92d47
Revises: c8a3d5b71f04
Create Date: 2026-08-12
"""
from alembic import op
import sqlalchemy as sa

revision = 'a1f6b3c92d47'
down_revision = 'c8a3d5b71f04'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('posts') as batch:
        batch.add_column(sa.Column('line_items', sa.JSON(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('posts') as batch:
        batch.drop_column('line_items')
