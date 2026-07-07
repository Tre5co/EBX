"""June 2026: post comments + image attachments

Revision ID: c2e4f6a8b0d1
Revises: b7d4e9a13c5f
Create Date: 2026-06-27 00:00:00.000000

Discussion overhaul:
- Post.parent_id (nullable str, FK posts.id) — a comment points at its parent
  post; top-level posts leave it null.
- Post.image_url (nullable text) — an attached image (data URL or stored path).
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2e4f6a8b0d1'
down_revision = 'b7d4e9a13c5f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('posts') as batch_op:
        batch_op.add_column(sa.Column('parent_id', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('image_url', sa.Text(), nullable=True))
        batch_op.create_foreign_key('fk_posts_parent_id', 'posts', ['parent_id'], ['id'])


def downgrade() -> None:
    with op.batch_alter_table('posts') as batch_op:
        batch_op.drop_constraint('fk_posts_parent_id', type_='foreignkey')
        batch_op.drop_column('image_url')
        batch_op.drop_column('parent_id')
