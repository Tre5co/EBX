"""Jun 2026 — benefactor post categories + post helpful/neutral/wrong voting

Revision ID: d3a1f7c2e5b8
Revises: c7f2a4e8d0b1
Create Date: 2026-06-06 00:00:00.000000

Changes:
- Post: drop 'likes'; add helpful_count, neutral_count, wrong_count (int, default 0)
  Post.type gains four new valid values for benefactor election commentary:
    'context'    — shared across tiv + org elections (background / history / who it helps)
    'analysis'   — shared across tiv + org elections (scientific / financial / expert take)
    'case'       — tiv-vote only ("why I voted for this initiative")
    'evaluation' — org-vote only ("why I voted for this organization")
  Existing type values (editorial, org_update, headline) are unchanged.
- post_votes table — one row per (post, benefactor); value in ('helpful','neutral','wrong').
  Upsert logic in the endpoint keeps the denormalised counts on posts in sync.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd3a1f7c2e5b8'
down_revision = 'c7f2a4e8d0b1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Post: swap likes for helpful/neutral/wrong counts.
    with op.batch_alter_table('posts') as batch_op:
        batch_op.drop_column('likes')
        batch_op.add_column(sa.Column('helpful_count', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('neutral_count', sa.Integer(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('wrong_count', sa.Integer(), nullable=False, server_default='0'))

    # post_votes — per-benefactor vote on a post.
    op.create_table(
        'post_votes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('post_id', sa.String(), nullable=False),
        sa.Column('benefactor_id', sa.Integer(), nullable=False),
        sa.Column('value', sa.String(), nullable=False),  # 'helpful' | 'neutral' | 'wrong'
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id']),
        sa.ForeignKeyConstraint(['benefactor_id'], ['benefactor_accounts.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('post_id', 'benefactor_id', name='uq_post_vote_benefactor'),
    )


def downgrade() -> None:
    op.drop_table('post_votes')

    with op.batch_alter_table('posts') as batch_op:
        batch_op.drop_column('wrong_count')
        batch_op.drop_column('neutral_count')
        batch_op.drop_column('helpful_count')
        batch_op.add_column(sa.Column('likes', sa.Integer(), nullable=False, server_default='0'))
