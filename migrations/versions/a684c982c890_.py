"""empty message

Revision ID: a684c982c890
Revises: 93a7808e92a0
Create Date: 2021-10-16 18:12:03.996294

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a684c982c890'
down_revision = '93a7808e92a0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('generation_request', sa.Column('published', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('generation_request', 'published')
    # ### end Alembic commands ###
