"""Add submission and grading to assignments

Revision ID: d2bd54301dd6
Revises: 
Create Date: 2025-01-30 18:14:39.519292

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd2bd54301dd6'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assignment', schema=None) as batch_op:
        batch_op.add_column(sa.Column('grade', sa.Float(), nullable=True))
        batch_op.add_column(sa.Column('submission', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('submitted_on', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('graded_on', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('assignment', schema=None) as batch_op:
        batch_op.drop_column('graded_on')
        batch_op.drop_column('submitted_on')
        batch_op.drop_column('submission')
        batch_op.drop_column('grade')

    # ### end Alembic commands ###
