"""aug20b one-way commitment — drop fresh_ct and returned_lots

Build-seq §1, second pass the same day. Jax, on reading the conversion model
back: *"Now that we have the 3-changes-per-token model, the slider bars have
become less appealing and I think I will remove them. Every token has a record
of where it has traveled, so moving tokens requires a specific transaction.
Users can no longer move tokens from an OE to unallocated. Unallocated is just
the tokens they have either purchased or been granted and not yet allocated."*

**Committed ct cannot come back**, so two columns added earlier today describe
states that can no longer exist:

    returned_lots   ct that had come back OUT of a race, held as lots so its
                    conversion count could not be laundered by resting in the
                    unallocated bar. Nothing can rest there any more — ct leaves
                    a race only by converting straight into another one, where
                    the count travels with it in a single transaction.

    fresh_ct        the part of the balance that was THIS WEEK'S grant, tracked
                    apart from ct that had been in a race and come back. With no
                    such ct, unallocated contains exactly two things — granted
                    and purchased — so the granted part is `free_ct −
                    purchased_ct` and storing it separately is storing one
                    number twice, with two chances to drift.

A grant that goes uncommitted is NOT demoted by this. It keeps its date
(rolled forward a week, per `token_model.roll_commit_by`) and its two doors;
it simply stops being counted in a column of its own.

Both columns were added in `f2c6a80d91b4` / `d4e7b91c3a52` earlier today and
have never held a value that matters, so this drops rather than migrates them.
`purchased_ct` and `conversions` stay: they are the two the new model needs.

Revision ID: a3b81d42c7e9
Revises: f2c6a80d91b4
Create Date: 2026-08-20
"""
from alembic import op
import sqlalchemy as sa

revision = 'a3b81d42c7e9'
down_revision = 'f2c6a80d91b4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('benefactor_accounts') as batch:
        batch.drop_column('returned_lots')
        batch.drop_column('fresh_ct')


def downgrade() -> None:
    with op.batch_alter_table('benefactor_accounts') as batch:
        batch.add_column(sa.Column('fresh_ct', sa.Integer(), nullable=False,
                                   server_default='0'))
        batch.add_column(sa.Column('returned_lots', sa.JSON(), nullable=True))
