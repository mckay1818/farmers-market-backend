"""added cart model, refactored relationships between products, orders, customers, and carts

Revision ID: 30aebabcbd0c
Revises: 23f0b1a38f76
Create Date: 2023-02-09 11:40:25.885092

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '30aebabcbd0c'
down_revision = '23f0b1a38f76'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('cart',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('customer_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['customer_id'], ['customer.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('cart_product',
    sa.Column('cart_id', sa.Integer(), nullable=False),
    sa.Column('product_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['cart_id'], ['cart.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], ),
    sa.PrimaryKeyConstraint('cart_id', 'product_id')
    )
    op.drop_table('order_product')
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cart_id', sa.Integer(), nullable=False))
        batch_op.create_foreign_key(None, 'cart', ['cart_id'], ['id'])
        batch_op.drop_column('is_shipped')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('order', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_shipped', sa.BOOLEAN(), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('cart_id')

    op.create_table('order_product',
    sa.Column('order_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('product_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('quantity', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['order_id'], ['order.id'], name='order_product_order_id_fkey'),
    sa.ForeignKeyConstraint(['product_id'], ['product.id'], name='order_product_product_id_fkey'),
    sa.PrimaryKeyConstraint('order_id', 'product_id', name='order_product_pkey')
    )
    op.drop_table('cart_product')
    op.drop_table('cart')
    # ### end Alembic commands ###
