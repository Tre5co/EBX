"""aug19 token wallet + explicit OE stakes

The money model settled 2026-08-19 (`backend/app/token_model.py`,
`docs/token_model.md`) needs two things the schema could not express.

**A wallet.** A benefactor's uncommitted balance was never stored — main.html
computed a per-cause budget as `10 + localStorage.ebx_purchased_ebx`, which is
a number living in one browser. The grant rule ("your uncommitted balance is
topped up to 10 every week") is arithmetic ON that balance, so it has to be on
the account:

    free_ct          uncommitted tokens, in CENTITOKENS (1 token = 100 ct = 10¢)
    fresh_ct         the part of free that is THIS WEEK'S GRANT and still
                     unspent. New tokens have two doors — this week's initiative
                     slate, or the one active-cause organization election ("2
                     options, not 9") — while ct that has come back out of a
                     race may be re-staked on any of the eight rows. The two
                     are the same tokens with different permissions, so the
                     wallet has to be able to tell them apart, and the OE table
                     draws them as two colours in one unallocated bar.
    cash_ct          refunded money; not a donation, never re-enters as tokens
    last_grant_week  cycle week index of the last top-up — idempotent grants

**An explicit OE stake.** Phase-2 weight was DERIVED: `p2_ebx_by_ben` summed a
benefactor's surviving `VoteP1.ebx_committed` rows for the mission. That works
only while phase-2 money can arrive by exactly one route (the carryover slider)
and never moves again. The new OE table is eight rows with a slider each, and a
stake can move between them, so the stake has to be a stored quantity:

    stake_ct           what this benefactor has staked on this mission's OE
    origin_mission_id  where those ct entered the system — provenance, and the
                       mission whose clock they carry
    born_week          the lot's own clock. A stake resolves 15 weeks after it
                       was first committed, wherever it currently sits. Without
                       this a benefactor can hop to the newest OE every week
                       forever: always committed, never donating, collecting the
                       full grant the whole time.
    provenance         JSON list of registered votes these ct have supported —
                       "every token maintains a record of its transactions".
                       Only committed votes are recorded; dragging a slider up
                       and down before committing leaves nothing behind.

**org_id becomes nullable.** When an initiative election closes, each backer's
non-claimed remainder moves into the winning initiative's OE automatically —
and arrives with no philanthropy named, because nobody chose one. Those stakes
fund the mission, carry no vote weight, and default to the winner of the race
they landed in unless the benefactor picks. A NOT NULL column cannot hold that
state, and the alternative (inventing an org id) is how the orphaned-initiative
500 happened in August.

`ebx_spent` and the float `VoteP1.ebx_committed` are left alone. This migration
adds capacity; it does not move anybody's money.

Revision ID: d4e7b91c3a52
Revises: a1f6b3c92d47
Create Date: 2026-08-19
"""
from alembic import op
import sqlalchemy as sa

revision = 'd4e7b91c3a52'
down_revision = 'a1f6b3c92d47'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('benefactor_accounts') as batch:
        batch.add_column(sa.Column('free_ct', sa.Integer(), nullable=False,
                                   server_default='0'))
        batch.add_column(sa.Column('fresh_ct', sa.Integer(), nullable=False,
                                   server_default='0'))
        batch.add_column(sa.Column('cash_ct', sa.Integer(), nullable=False,
                                   server_default='0'))
        batch.add_column(sa.Column('last_grant_week', sa.Integer(), nullable=True))

    with op.batch_alter_table('votes_p2') as batch:
        batch.add_column(sa.Column('stake_ct', sa.Integer(), nullable=False,
                                   server_default='0'))
        batch.add_column(sa.Column('origin_mission_id', sa.String(), nullable=True))
        batch.add_column(sa.Column('born_week', sa.Integer(), nullable=True))
        batch.add_column(sa.Column('provenance', sa.JSON(), nullable=True))
        # An unassigned stake has no organization yet — see the note above.
        batch.alter_column('org_id', existing_type=sa.String(), nullable=True)


def downgrade() -> None:
    with op.batch_alter_table('votes_p2') as batch:
        batch.alter_column('org_id', existing_type=sa.String(), nullable=False)
        batch.drop_column('provenance')
        batch.drop_column('born_week')
        batch.drop_column('origin_mission_id')
        batch.drop_column('stake_ct')

    with op.batch_alter_table('benefactor_accounts') as batch:
        batch.drop_column('last_grant_week')
        batch.drop_column('cash_ct')
        batch.drop_column('fresh_ct')
        batch.drop_column('free_ct')
