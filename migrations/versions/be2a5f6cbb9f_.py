"""empty message

Revision ID: be2a5f6cbb9f
Revises: 
Create Date: 2022-02-02 23:11:53.112122

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'be2a5f6cbb9f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('join_date', sa.DateTime(), nullable=False),
    sa.Column('roles', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('delivery_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('receiver_name', sa.String(length=100), nullable=True),
    sa.Column('delivery_area', sa.String(length=100), nullable=True),
    sa.Column('collectable_amount', sa.Integer(), nullable=True),
    sa.Column('receiver_number', sa.String(length=50), nullable=True),
    sa.Column('receiver_address', sa.String(length=100), nullable=True),
    sa.Column('book_date', sa.DateTime(), nullable=False),
    sa.Column('merchant_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['merchant_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('merchant',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('profile_image', sa.String(length=20), nullable=False),
    sa.Column('merchant_id', sa.Integer(), nullable=False),
    sa.Column('pickup_address', sa.String(length=100), nullable=True),
    sa.Column('balance', sa.String(length=100), nullable=True),
    sa.Column('due_chare', sa.String(length=100), nullable=True),
    sa.Column('bkash_number', sa.String(length=11), nullable=True),
    sa.Column('bank_number', sa.String(length=40), nullable=True),
    sa.ForeignKeyConstraint(['merchant_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('parcel',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('merchant_id', sa.Integer(), nullable=False),
    sa.Column('delivery_id', sa.Integer(), nullable=False),
    sa.Column('delivery_man', sa.String(length=50), nullable=True),
    sa.Column('parcel_status', sa.String(length=50), nullable=True),
    sa.Column('charge', sa.String(length=50), nullable=True),
    sa.Column('due_charge', sa.String(length=50), nullable=True),
    sa.Column('user_balance', sa.String(length=50), nullable=True),
    sa.Column('pay_status', sa.String(length=50), nullable=True),
    sa.Column('pay_method', sa.String(length=50), nullable=True),
    sa.Column('parcel_date', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['delivery_id'], ['delivery_info.id'], ),
    sa.ForeignKeyConstraint(['merchant_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('parcel')
    op.drop_table('merchant')
    op.drop_table('delivery_info')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###
