"""add Customer username field

Revision ID: 5f82b379fab4
Revises: 5457881f426e
Create Date: 2023-02-03 15:08:01.284949

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f82b379fab4'
down_revision = '5457881f426e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('customer', schema=None) as batch_op:
        batch_op.add_column(sa.Column('username', sa.String(length=20), nullable=False))
        batch_op.create_unique_constraint(None, ['username'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('customer', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='unique')
        batch_op.drop_column('username')

    # ### end Alembic commands ###
