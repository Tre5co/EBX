"""aug27c the finalized ME/OE model — the cause tag, the split, and four states

The model is `docs/_to_delete/ME_OE_FINALIZATION.md`, answered by Jax on 2026-08-27. Three
of its rules need a column that does not exist yet, and one column stops being
read.

    benefactor_accounts.grant_cause_id
        "Tokens aren't granted until election week when it's too late to
        transfer or withdraw." A granted token appears against the week's CAUSE
        and, if unspent, waits for that cause's next window. It cannot be moved
        anywhere else, so the cause is not a tag on mobile money — it is the
        only place that token was ever able to go. This is what replaces the
        rolling commit-by date on the face of the token.

    votes_p1.stake_ct
        "The vote commit be the total amount committed to that election, and the
        weight be the percentage given to each tiv within it." The slate was
        already normalized to shares; what was missing is the amount. It is
        stored PER ROW as `commit x share` (largest-remainder, so the rows sum
        to the commit exactly) rather than in a new per-election table, because
        the sum over a mission's rows IS the election-level commit and one
        number stored twice is one number that can drift.

    votes_p2.committed_week
        The week an allocation was made, which is the whole of the week-change
        rule: inside its own week it is a draft, at the roll it hardens.

    votes_p2.minted_ct / votes_p2.donated_ct
        The two states after `committed`. `minted` is EBX — mission-tied,
        immovable. `donated` is what has crossed over in tranches, deductible at
        the date of each. They are BOOKED rather than derived because a history
        cannot be recomputed from a balance: the OE half of settlement was the
        one half still being recomputed on every read, and this is the column
        that ends that.

    votes_p2.marked_tiv_id
        A backer of a LOSING initiative keeps tokens, marked with the initiative
        they voted for, and may move them to a different organization election
        by voting for a philanthropy there. The mark is what says these ct are
        still tokens; a row without one, in a decided ME, is early EBX.

Nothing is dropped. `benefactor_accounts.grant_commit_by_week` and
`votes_p2.conversions` are left in place, unread, holding the last values the
retired rules wrote — the pilot database is the record of races settled under
those rules, and a column deleted is a race that can no longer be explained.
They come out when no open mission predates 2026-08-27.

Revision ID: c5d8f2a91e67
Revises: a3b81d42c7e9
Create Date: 2026-08-27
"""
from alembic import op
import sqlalchemy as sa

revision = 'c5d8f2a91e67'
down_revision = 'a3b81d42c7e9'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('benefactor_accounts') as batch:
        batch.add_column(sa.Column('grant_cause_id', sa.String(), nullable=True))
    with op.batch_alter_table('votes_p1') as batch:
        batch.add_column(sa.Column('stake_ct', sa.Integer(), nullable=False,
                                   server_default='0'))
    with op.batch_alter_table('votes_p2') as batch:
        batch.add_column(sa.Column('committed_week', sa.Integer(), nullable=True))
        batch.add_column(sa.Column('minted_ct', sa.Integer(), nullable=False,
                                   server_default='0'))
        batch.add_column(sa.Column('donated_ct', sa.Integer(), nullable=False,
                                   server_default='0'))
        batch.add_column(sa.Column('marked_tiv_id', sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('votes_p2') as batch:
        batch.drop_column('marked_tiv_id')
        batch.drop_column('donated_ct')
        batch.drop_column('minted_ct')
        batch.drop_column('committed_week')
    with op.batch_alter_table('votes_p1') as batch:
        batch.drop_column('stake_ct')
    with op.batch_alter_table('benefactor_accounts') as batch:
        batch.drop_column('grant_cause_id')
