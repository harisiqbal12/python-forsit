"""sales table

Revision ID: 9eced4ec6e0a
Revises: 268e607093bd
Create Date: 2025-05-18 21:19:09.058870

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import os


# revision identifiers, used by Alembic.
revision: str = "9eced4ec6e0a"
down_revision: Union[str, None] = "268e607093bd"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _read_sql_file(filename: str):
    """Read SQL from a file"""
    directory = os.path.dirname(os.path.abspath(__file__))
    sql_dir = os.path.join(directory, "../sql")
    with open(os.path.join(sql_dir, filename), "r") as f:
        return f.read()


def upgrade() -> None:
    # exectute sql
    op.execute(_read_sql_file("V3__sales_table.sql"))


def downgrade() -> None:
    """Downgrade schema."""
    pass
