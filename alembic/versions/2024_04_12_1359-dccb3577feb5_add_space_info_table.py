"""Add space_info table

Revision ID: dccb3577feb5
Revises: 0278f7c21985
Create Date: 2024-04-12 13:59:35.003367

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dccb3577feb5'
down_revision: Union[str, None] = '0278f7c21985'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('space_info',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('space_key', sa.String(), nullable=False),
    sa.Column('space_name', sa.String(), nullable=False),
    sa.Column('last_import_date', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('space_info')
    # ### end Alembic commands ###