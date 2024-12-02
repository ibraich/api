"""empty message

Revision ID: 225a57721908
Revises: 7da7afe4f843
Create Date: 2024-12-02 16:41:50.829013

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '225a57721908'
down_revision = '7da7afe4f843'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('DocumentEdit', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'User', ['user_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('DocumentEdit', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###
