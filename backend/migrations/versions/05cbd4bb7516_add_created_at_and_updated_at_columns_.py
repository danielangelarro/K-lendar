"""Add created_at and updated_at columns to tables

Revision ID: 05cbd4bb7516
Revises: 
Create Date: 2024-11-19 07:20:31.969346

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '05cbd4bb7516'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
