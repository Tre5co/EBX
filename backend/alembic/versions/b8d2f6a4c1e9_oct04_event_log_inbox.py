"""P4 · Event log + Inbox — the event log, notifications and member messages.

ADDITIVE ONLY: five new tables, nothing existing is altered or dropped, so a
downgrade loses only notifications and messages.

  events            the one source for notifications, the weekly update and
                    (later) the admin audit trail.
  notifications     the per-benefactor fan-out of an event, read / unread.
  message_threads   a conversation between two benefactors who share a mission.
  messages          its messages.
  message_reports   the report button.

Revision ID: b8d2f6a4c1e9
Revises: a7c4e2f9b1d3
Create Date: 2026-10-04
"""
from alembic import op
import sqlalchemy as sa

revision = 'b8d2f6a4c1e9'
down_revision = 'a7c4e2f9b1d3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'events',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('kind', sa.String(), nullable=False, index=True),
        sa.Column('actor_ben_id', sa.Integer(), sa.ForeignKey('benefactor_accounts.id'), nullable=True),
        sa.Column('actor_org_id', sa.String(), sa.ForeignKey('organizations.id'), nullable=True),
        sa.Column('post_id', sa.String(), nullable=True, index=True),
        sa.Column('mission_id', sa.String(), nullable=True, index=True),
        sa.Column('tiv_id', sa.String(), nullable=True),
        sa.Column('org_id', sa.String(), nullable=True),
        sa.Column('week', sa.Integer(), nullable=True, index=True),
        sa.Column('dedupe', sa.String(), nullable=True, unique=True),
        sa.Column('data', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), index=True),
    )
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('ben_id', sa.Integer(), sa.ForeignKey('benefactor_accounts.id'), nullable=False, index=True),
        sa.Column('event_id', sa.Integer(), sa.ForeignKey('events.id'), nullable=False, index=True),
        sa.Column('detail', sa.JSON(), nullable=True),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint('ben_id', 'event_id', name='uq_notification_ben_event'),
    )
    op.create_table(
        'message_threads',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('a_id', sa.Integer(), sa.ForeignKey('benefactor_accounts.id'), nullable=False, index=True),
        sa.Column('b_id', sa.Integer(), sa.ForeignKey('benefactor_accounts.id'), nullable=False, index=True),
        sa.Column('mission_id', sa.String(), sa.ForeignKey('missions.id'), nullable=True),
        sa.Column('a_read_at', sa.DateTime(), nullable=True),
        sa.Column('b_read_at', sa.DateTime(), nullable=True),
        sa.Column('last_message_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint('a_id', 'b_id', name='uq_thread_pair'),
    )
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('thread_id', sa.Integer(), sa.ForeignKey('message_threads.id'), nullable=False, index=True),
        sa.Column('sender_id', sa.Integer(), sa.ForeignKey('benefactor_accounts.id'), nullable=False),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('hidden', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        'message_reports',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('message_id', sa.Integer(), sa.ForeignKey('messages.id'), nullable=False, index=True),
        sa.Column('reporter_id', sa.Integer(), sa.ForeignKey('benefactor_accounts.id'), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('status', sa.String(), nullable=False, server_default='open'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('message_reports')
    op.drop_table('messages')
    op.drop_table('message_threads')
    op.drop_table('notifications')
    op.drop_table('events')
