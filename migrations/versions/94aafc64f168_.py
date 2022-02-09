"""empty message

Revision ID: 94aafc64f168
Revises: d92206a21e48
Create Date: 2022-02-06 16:12:13.372692

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '94aafc64f168'
down_revision = 'd92206a21e48'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('parcel', 'parcel_status',
               existing_type=mysql.VARCHAR(length=50),
               nullable=False)
    op.alter_column('parcel', 'pay_status',
               existing_type=mysql.VARCHAR(length=50),
               nullable=False)
    op.alter_column('parcel', 'pay_method',
               existing_type=mysql.VARCHAR(length=50),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('parcel', 'pay_method',
               existing_type=mysql.VARCHAR(length=50),
               nullable=True)
    op.alter_column('parcel', 'pay_status',
               existing_type=mysql.VARCHAR(length=50),
               nullable=True)
    op.alter_column('parcel', 'parcel_status',
               existing_type=mysql.VARCHAR(length=50),
               nullable=True)
    # ### end Alembic commands ###