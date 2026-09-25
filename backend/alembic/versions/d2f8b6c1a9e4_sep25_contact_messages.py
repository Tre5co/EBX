"""sep25 — contact_messages: the footer's "Contact us"

2026-09-25: "'Contact us' should open a dialogue for them to send a message,
which messages jax@earthbux.net." There is no mail transport yet (P6/c1), so
every message is stored here first; `app/mailer.py` also emails it when SMTP is
configured, and `emailed` records whether it did. Staff read them at
GET /admin/contact.

Revision ID: d2f8b6c1a9e4
Revises: c9e4a7d2b6f1
Create Date: 2026-09-25
"""
from alembic import op
import sqlalchemy as sa

revision = 'd2f8b6c1a9e4'
down_revision = 'c9e4a7d2b6f1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'contact_messages',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('topic', sa.String(), nullable=False, server_default='general'),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('page', sa.String(), nullable=True),
        sa.Column('ben_id', sa.Integer(), sa.ForeignKey('benefactor_accounts.id'), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='new'),
        sa.Column('emailed', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('contact_messages')
