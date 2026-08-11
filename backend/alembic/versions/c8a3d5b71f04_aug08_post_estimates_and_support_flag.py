"""aug08 post estimates + the post-support flag

Two additions to `posts`, both from the 2026-08-08 pass:

§2a  est_setup_days / est_cost_usd — a BUDGETING post (service · supply ·
     support) is a suggestion the mission may adopt, so it is not a suggestion
     until it is costed. Both estimates are required at creation for the
     budgeting category (enforced in crud.create_post) and null everywhere
     else, which is why the columns are nullable.

MISSION PHASE  flag / flag_reason — the first layer of the mission annulus.
     Every org-tagged thread (case · investigation · evaluation) is rated
     green (useful) / orange (critical but helpful) / red (spam, scams or
     unsupported slander), because philanthropies receive a weekly digest of
     what was written about them and are owed an honest label on it. The
     classifier is a stub that rates everything **green**, so the column lands
     with server_default='green' and every existing row is green on upgrade.

Revision ID: c8a3d5b71f04
Revises: b7d4e9a1c206
Create Date: 2026-08-08
"""
from alembic import op
import sqlalchemy as sa

revision = 'c8a3d5b71f04'
down_revision = 'b7d4e9a1c206'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('posts') as batch:
        batch.add_column(sa.Column('est_setup_days', sa.Float(), nullable=True))
        batch.add_column(sa.Column('est_cost_usd', sa.Float(), nullable=True))
        batch.add_column(sa.Column('flag', sa.String(), server_default='green', nullable=False))
        batch.add_column(sa.Column('flag_reason', sa.String(), nullable=True))
    # Belt and braces: server_default covers the rows that exist at upgrade
    # time, this covers any row written by an older process mid-deploy.
    op.execute("UPDATE posts SET flag = 'green' WHERE flag IS NULL OR flag = ''")


def downgrade() -> None:
    with op.batch_alter_table('posts') as batch:
        batch.drop_column('flag_reason')
        batch.drop_column('flag')
        batch.drop_column('est_cost_usd')
        batch.drop_column('est_setup_days')
