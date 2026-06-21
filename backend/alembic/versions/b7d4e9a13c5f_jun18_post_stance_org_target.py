"""June 2026: post stance + org target

Revision ID: b7d4e9a13c5f
Revises: a9f2c1b4d7e3
Create Date: 2026-06-18 00:00:00.000000

Comments wiring:
- Post.org_id (nullable str, FK organizations.id) — the TARGET org for
  evaluation posts and org-scoped context/analysis (distinct from
  org_author_id, which is the authoring org).
- Post.stance (nullable str) — case posts carry for|against; evaluation posts
  carry positive|negative; context/analysis leave it null.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b7d4e9a13c5f'
down_revision = 'a9f2c1b4d7e3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('posts') as batch_op:
        batch_op.add_column(sa.Column('org_id', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('stance', sa.String(), nullable=True))
        batch_op.create_foreign_key('fk_posts_org_id', 'organizations', ['org_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('posts') as batch_op:
        batch_op.drop_constraint('fk_posts_org_id', type_='foreignkey')
        batch_op.drop_column('stance')
        batch_op.drop_column('org_id')
