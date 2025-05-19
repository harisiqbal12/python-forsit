"""enable rls

Revision ID: 9c2ce1b8e442
Revises: 9eced4ec6e0a
Create Date: 2025-05-19 04:30:33.074795

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import os


# revision identifiers, used by Alembic.
revision: str = '9c2ce1b8e442'
down_revision: Union[str, None] = '9eced4ec6e0a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _read_sql_file(filename: str):
    """Read SQL from a file"""
    directory = os.path.dirname(os.path.abspath(__file__))
    sql_dir = os.path.join(directory, "../sql")
    with open(os.path.join(sql_dir, filename), "r") as f:
        return f.read()


def upgrade() -> None:
    # execute sql
    op.execute(_read_sql_file("V4__enable_rls.sql"))


def downgrade() -> None:
    """Downgrade schema."""
    pass
