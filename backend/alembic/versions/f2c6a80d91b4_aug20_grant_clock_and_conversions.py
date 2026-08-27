"""aug20 grant clock, purchased tokens, conversion budget

Build-seq §1, rewritten 2026-08-20 ("I've resolved my confusion"). Three
sentences in that rewrite need a column each; the rest of the change is
arithmetic and lives in `token_model.py`.

**"These granted tokens are marked with the date that they must be committed
by (or expire). If they are not committed … by that date, the date changes 1
week forward."** The date is a property of the GRANT, not of the account's whole
balance, so it cannot be derived from `last_grant_week` alone once a benefactor
has spent part of one grant and kept part of another:

    grant_commit_by_week   cycle week by which `fresh_ct` must be committed

Missing it is not a forfeiture — `token_model.roll_commit_by` simply hands out
next week's date. What caps a hoard is the top-up formula (`grant = 10 − free`),
which was always the mechanism; the date is there so a benefactor can see that
this week's ten are meant to be spent this week.

**"Purchased tokens are the same as granted tokens except they do not have a
deadline to commit."** They also carry no two-door restriction, which makes them
behave exactly like returned balance — but the unallocated strip has to be able
to say which uncommitted tokens are on a clock:

    purchased_ct           the part of `free_ct` that was bought, not granted

**"There is a limit to the amount of times it can be converted (3)."** This
replaces the 15-week fuse (`TOKEN_CLOCK_WEEKS`) that used to bound a stake's
life. A count is the better bound: a deadline punishes a benefactor for
deliberating, while a conversion budget prices the thing that actually needed
pricing — hopping to the newest organization election every week to stay
permanently committed and never donate.

    conversions            moves to a race other than `origin_mission_id`
    returned_lots          ct sitting in the unallocated bar, as lots that
                           remember their origin and their spent conversions

A conversion is SPENT when a philanthropy is voted for in the new race, not when
the slider moves: "in order for the user to convert their token to a different
OE, they need to vote on a phl for it. If they don't, the token defaults to the
OE from the tiv it was created within."

`returned_lots` is what makes the count survive the trip through the wallet. Ct
that leaves a race lands in one balance with everything else, and a scalar
cannot remember that 3 of those tokens have already moved twice — so a
benefactor could reset a stake's history by parking it for a week. Lots are
FIFO, they keep their origin, and merging two into one row takes the HIGHER
conversion count: mixing a spent lot with a fresh one must not buy back moves.

Nobody's money moves here. Existing stakes start with zero conversions spent,
which is the correct reading of history — no stake in the pilot database has
ever been converted, because until today it could not be.

Revision ID: f2c6a80d91b4
Revises: d4e7b91c3a52
Create Date: 2026-08-20
"""
from alembic import op
import sqlalchemy as sa

revision = 'f2c6a80d91b4'
down_revision = 'd4e7b91c3a52'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('benefactor_accounts') as batch:
        batch.add_column(sa.Column('purchased_ct', sa.Integer(), nullable=False,
                                   server_default='0'))
        batch.add_column(sa.Column('grant_commit_by_week', sa.Integer(), nullable=True))
        batch.add_column(sa.Column('returned_lots', sa.JSON(), nullable=True))

    with op.batch_alter_table('votes_p2') as batch:
        batch.add_column(sa.Column('conversions', sa.Integer(), nullable=False,
                                   server_default='0'))


def downgrade() -> None:
    with op.batch_alter_table('votes_p2') as batch:
        batch.drop_column('conversions')

    with op.batch_alter_table('benefactor_accounts') as batch:
        batch.drop_column('returned_lots')
        batch.drop_column('grant_commit_by_week')
        batch.drop_column('purchased_ct')
