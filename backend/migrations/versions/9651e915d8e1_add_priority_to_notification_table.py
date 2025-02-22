"""Add priority to Notification Table

Revision ID: 9651e915d8e1
Revises: 4334de7ff72f
Create Date: 2024-12-01 09:27:22.625595

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9651e915d8e1'
down_revision: Union[str, None] = '4334de7ff72f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.add_column(sa.Column('priority', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notification', schema=None) as batch_op:
        batch_op.drop_column('priority')

    # ### end Alembic commands ###
