"""sep29 — P3 · Posting: targets, tags, versions, per-mission votes, references

INSTRUCTIONS › P3 · Posting (D8, D19–D21, answered 2026-09-28):

* `posts.target_kind` / `target_id` — what a post is ABOUT, stated once
  (cause · initiative · organization · mission · post · budget · none).
* `posts.tags` — a general post's subtype and its entity tags; citations are
  tags too. `posts.version` / `updated_at` — the newest version (D21).
* `post_versions` — every edit is a new version; old ones never change.
* `post_missions` — the missions a post belongs to and the version each keeps
  once its election closes (origin · roll · pull · cite).
* `post_refs` — what a post cites, at the version it cited (the Analysis's
  12 + 12, the two leading ones `auto`).
* `mission_leads` — the leading Background (fixed at T) and Investigation
  (fixed at T+8) of each mission (D20).
* `post_votes.mission_scope` — votes count per mission (D21); the unique key
  becomes (post, benefactor, mission).

Data: every existing post gets its version 1 and its target; every post with a
mission gets its `origin` row; every vote is scoped to its post's mission; and
the retired Review lane (case · evaluation, D8) becomes general posts carrying
the tag. No money moves.

Revision ID: e3b9c7a1d4f2
Revises: d2f8b6c1a9e4
Create Date: 2026-09-29
"""
import json

from alembic import op
import sqlalchemy as sa

revision = 'e3b9c7a1d4f2'
down_revision = 'd2f8b6c1a9e4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('posts') as b:
        b.add_column(sa.Column('target_kind', sa.String(), nullable=True))
        b.add_column(sa.Column('target_id', sa.String(), nullable=True))
        b.add_column(sa.Column('tags', sa.JSON(), nullable=True))
        b.add_column(sa.Column('version', sa.Integer(), nullable=False, server_default='1'))
        b.add_column(sa.Column('updated_at', sa.DateTime(), nullable=True))

    with op.batch_alter_table('post_votes', recreate='always') as b:
        b.add_column(sa.Column('mission_scope', sa.String(), nullable=False, server_default=''))
        b.drop_constraint('uq_post_vote_ben', type_='unique')
        b.create_unique_constraint('uq_post_vote_ben_mission', ['post_id', 'ben_id', 'mission_scope'])

    op.create_table(
        'post_versions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('post_id', sa.String(), sa.ForeignKey('posts.id'), nullable=False, index=True),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('body', sa.Text(), nullable=False),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('line_items', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint('post_id', 'version', name='uq_post_version'),
    )
    op.create_table(
        'post_missions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('post_id', sa.String(), sa.ForeignKey('posts.id'), nullable=False, index=True),
        sa.Column('mission_id', sa.String(), sa.ForeignKey('missions.id'), nullable=False, index=True),
        sa.Column('via', sa.String(), nullable=False, server_default='origin'),
        sa.Column('pinned_version', sa.Integer(), nullable=True),
        sa.Column('pinned_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.UniqueConstraint('post_id', 'mission_id', name='uq_post_mission'),
    )
    op.create_table(
        'post_refs',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('post_id', sa.String(), sa.ForeignKey('posts.id'), nullable=False, index=True),
        sa.Column('kind', sa.String(), nullable=False),
        sa.Column('ref_post_id', sa.String(), sa.ForeignKey('posts.id'), nullable=True, index=True),
        sa.Column('ref_version', sa.Integer(), nullable=True),
        sa.Column('ref_mission_id', sa.String(), sa.ForeignKey('missions.id'), nullable=True),
        sa.Column('url', sa.Text(), nullable=True),
        sa.Column('label', sa.String(), nullable=True),
        sa.Column('auto', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('position', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )
    op.create_table(
        'mission_leads',
        sa.Column('mission_id', sa.String(), sa.ForeignKey('missions.id'), primary_key=True),
        sa.Column('background_id', sa.String(), sa.ForeignKey('posts.id'), nullable=True),
        sa.Column('background_version', sa.Integer(), nullable=True),
        sa.Column('background_fixed_at', sa.DateTime(), nullable=True),
        sa.Column('investigation_id', sa.String(), sa.ForeignKey('posts.id'), nullable=True),
        sa.Column('investigation_version', sa.Integer(), nullable=True),
        sa.Column('investigation_fixed_at', sa.DateTime(), nullable=True),
    )

    _backfill(op.get_bind())


def _backfill(conn) -> None:
    t = sa.text
    missions = {r[0]: {'cause_id': r[1], 'winning_tiv_id': r[2]}
                for r in conn.execute(t("SELECT id, cause_id, winning_tiv_id FROM missions"))}
    rows = conn.execute(t(
        "SELECT id, category, type, title, body, line_items, mission_id, tiv_id, cause_id, "
        "org_id, parent_id, created_at FROM posts")).mappings().all()
    for p in rows:
        cat, typ = p['category'], p['type']
        tags = []
        new_cat, new_type = cat, typ
        # D8: the Review lane is gone — case and evaluation are tags now.
        if cat in ('review', 'case') or typ in ('case', 'evaluation'):
            new_cat, new_type = 'general', 'general'
            tag = typ if typ in ('case', 'evaluation') else ('case' if cat == 'case' else None)
            if tag:
                tags.append(tag)
        m = missions.get(p['mission_id']) if p['mission_id'] else None
        cause_id = p['cause_id'] or (m['cause_id'] if m else None)
        tiv_id = p['tiv_id']
        kind, tid = None, None
        if p['parent_id']:
            kind, tid = 'post', p['parent_id']
        elif new_type == 'context':
            kind, tid = ('cause', cause_id) if cause_id else ('none', None)
        elif new_type == 'investigation':
            kind, tid = ('organization', p['org_id']) if p['org_id'] else ('mission', p['mission_id'])
        elif new_type == 'analysis':
            kind, tid = 'mission', p['mission_id']
        elif new_cat in ('budgeting', 'resolution'):
            tiv_id = tiv_id or (m['winning_tiv_id'] if m else None)
            kind, tid = ('initiative', tiv_id) if tiv_id else ('mission', p['mission_id'])
        elif p['org_id']:
            kind, tid = 'organization', p['org_id']
        elif tiv_id:
            kind, tid = 'initiative', tiv_id
        elif p['mission_id']:
            kind, tid = 'mission', p['mission_id']
        elif cause_id:
            kind, tid = 'cause', cause_id
        else:
            kind, tid = 'none', None
        conn.execute(t(
            "UPDATE posts SET category=:c, type=:ty, tags=:tags, target_kind=:k, target_id=:tid, "
            "cause_id=:cause, tiv_id=:tiv, version=1 WHERE id=:id"),
            dict(c=new_cat, ty=new_type, tags=json.dumps(tags) if tags else None, k=kind, tid=tid,
                 cause=cause_id, tiv=tiv_id, id=p['id']))
        conn.execute(t(
            "INSERT INTO post_versions (post_id, version, title, body, tags, line_items, created_at) "
            "VALUES (:id, 1, :title, :body, :tags, :li, :at)"),
            dict(id=p['id'], title=p['title'], body=p['body'] or '',
                 tags=json.dumps(tags) if tags else None,
                 li=p['line_items'] if isinstance(p['line_items'], (str, type(None))) else json.dumps(p['line_items']),
                 at=p['created_at']))
        if p['mission_id'] and not p['parent_id']:
            conn.execute(t(
                "INSERT INTO post_missions (post_id, mission_id, via, created_at) "
                "VALUES (:id, :m, 'origin', :at)"), dict(id=p['id'], m=p['mission_id'], at=p['created_at']))
    conn.execute(t(
        "UPDATE post_votes SET mission_scope = COALESCE("
        "(SELECT mission_id FROM posts WHERE posts.id = post_votes.post_id), '')"))


def downgrade() -> None:
    op.drop_table('mission_leads')
    op.drop_table('post_refs')
    op.drop_table('post_missions')
    op.drop_table('post_versions')
    with op.batch_alter_table('post_votes', recreate='always') as b:
        b.drop_constraint('uq_post_vote_ben_mission', type_='unique')
        b.drop_column('mission_scope')
        b.create_unique_constraint('uq_post_vote_ben', ['post_id', 'ben_id'])
    with op.batch_alter_table('posts') as b:
        for c in ('updated_at', 'version', 'tags', 'target_id', 'target_kind'):
            b.drop_column(c)
