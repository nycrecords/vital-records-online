"""Added Spouse Type to Marriage Data

Revision ID: ee37953302ca
Revises: e09fefb2cf76
Create Date: 2022-05-26 19:26:22.007589

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ee37953302ca'
down_revision = 'e09fefb2cf76'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('marriage_data', sa.Column('spouse_type', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('marriage_data', 'spouse_type')
    # ### end Alembic commands ###