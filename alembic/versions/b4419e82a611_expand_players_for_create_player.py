"""expand Players table for create player endpoint

Revision ID: b4419e82a611
Revises: 4d0611273919
Create Date: 2026-05-03

Adds columns matching POST /players/
Uses integer PK id from prior revision
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b4419e82a611"
down_revision: Union[str, None] = "4d0611273919"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "Players",
        sa.Column("position", sa.String(length=64), nullable=True),
    )
    op.add_column(
        "Players",
        sa.Column("college", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "Players",
        sa.Column("draft_year", sa.Integer(), nullable=True),
    )
    op.add_column(
        "Players",
        sa.Column("team", sa.String(length=128), nullable=True),
    )
    op.add_column(
        "Players",
        sa.Column("status", sa.String(length=64), nullable=True),
    )

    # Backfill so NOT NULL succeeds on existing rows (fresh DB has none).
    op.execute(
        sa.text("""
            UPDATE "Players"
            SET
              position = COALESCE(position, ''),
              college = COALESCE(college, ''),
              draft_year = COALESCE(draft_year, 0),
              team = COALESCE(team, ''),
              status = COALESCE(status, '')
        """)
    )

    op.alter_column(
        "Players",
        "position",
        existing_type=sa.String(length=64),
        nullable=False,
    )
    op.alter_column(
        "Players",
        "college",
        existing_type=sa.String(length=255),
        nullable=False,
    )
    op.alter_column(
        "Players",
        "draft_year",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column(
        "Players",
        "team",
        existing_type=sa.String(length=128),
        nullable=False,
    )
    op.alter_column(
        "Players",
        "status",
        existing_type=sa.String(length=64),
        nullable=False,
    )


def downgrade() -> None:
    op.drop_column("Players", "status")
    op.drop_column("Players", "team")
    op.drop_column("Players", "draft_year")
    op.drop_column("Players", "college")
    op.drop_column("Players", "position")
