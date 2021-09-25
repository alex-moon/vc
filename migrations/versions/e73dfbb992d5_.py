"""empty message

Revision ID: e73dfbb992d5
Revises: 1f1183df052e
Create Date: 2021-09-25 21:01:02.524043

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e73dfbb992d5'
down_revision = '1f1183df052e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('generation_result', 'url',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('generation_result', 'url',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###