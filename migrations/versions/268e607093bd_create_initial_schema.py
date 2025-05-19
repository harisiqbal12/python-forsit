"""create initial schema

Revision ID: 268e607093bd
Revises: 
Create Date: 2025-05-17 17:30:25.304178

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import os


# revision identifiers, used by Alembic.
revision: str = "268e607093bd"
down_revision: Union[str, None] = None
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
    op.execute(_read_sql_file("v1__create_table.sql"))
    op.execute(_read_sql_file("v2__create_tables_indexes.sql"))


def downgrade() -> None:
    """Downgrade schema."""
    pass
