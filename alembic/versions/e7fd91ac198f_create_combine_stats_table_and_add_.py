"""create combine_stats table and add timestamps to Players

Revision ID: e7fd91ac198f
Revises: b4419e82a611
Create Date: 2026-05-09 11:02:59.333567

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7fd91ac198f'
down_revision: Union[str, None] = 'b4419e82a611'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "Players",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )
    op.add_column(
        "Players",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )

    op.execute("""
        CREATE OR REPLACE FUNCTION set_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = NOW();
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)
    op.execute("""
        CREATE TRIGGER players_set_updated_at
        BEFORE UPDATE ON "Players"
        FOR EACH ROW EXECUTE FUNCTION set_updated_at();
    """)

    op.create_table(
        "combine_stats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "player_id",
            sa.Integer(),
            sa.ForeignKey("Players.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("height_inches", sa.Numeric(5, 2), nullable=True),
        sa.Column("weight_lbs", sa.Numeric(6, 2), nullable=True),
        sa.Column("hand_size_inches", sa.Numeric(4, 2), nullable=True),
        sa.Column("arm_length_inches", sa.Numeric(4, 2), nullable=True),
        sa.Column("wingspan_inches", sa.Numeric(5, 2), nullable=True),
        sa.Column("forty_yard_dash", sa.Numeric(4, 2), nullable=True),
        sa.Column("ten_yard_split", sa.Numeric(4, 2), nullable=True),
        sa.Column("twenty_yard_shuttle", sa.Numeric(4, 2), nullable=True),
        sa.Column("three_cone", sa.Numeric(4, 2), nullable=True),
        sa.Column("vertical_jump_inches", sa.Numeric(4, 2), nullable=True),
        sa.Column("broad_jump_inches", sa.Numeric(5, 2), nullable=True),
        sa.Column("bench_press_reps", sa.Integer(), nullable=True),
        sa.Column(
            "recorded_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("combine_stats")
    op.execute('DROP TRIGGER IF EXISTS players_set_updated_at ON "Players"')
    op.execute("DROP FUNCTION IF EXISTS set_updated_at")
    op.drop_column("Players", "updated_at")
    op.drop_column("Players", "created_at")
