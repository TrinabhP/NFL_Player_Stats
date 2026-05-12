from fastapi import APIRouter, Depends, status
import sqlalchemy

from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)

# Baseline prospect profile post-reset for similarity / tooling (approximate blended NFL combine means).
IDEAL_PLAYER_ID = 1
IDEAL_COMBINE_ROW = {
    "height_inches": 74.25,
    "weight_lbs": 241.0,
    "hand_size_inches": 9.75,
    "arm_length_inches": 32.75,
    "wingspan_inches": 78.5,
    "forty_yard_dash": 4.68,
    "ten_yard_split": 1.59,
    "twenty_yard_shuttle": 4.28,
    "three_cone": 7.08,
    "vertical_jump_inches": 32.5,
    "broad_jump_inches": 118.0,
    "bench_press_reps": 21,
}


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset():
    """
    Clear players and combine_stats, then insert a single baseline row (id=1) with typical
    league-wide combine averages for comparison.
    """

    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                TRUNCATE TABLE combine_stats, "Players" RESTART IDENTITY CASCADE
                """
            )
        )

        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO "Players" (id, name, position, college, draft_year, team, status)
                VALUES (
                    :id,
                    'NFL Combine Average',
                    'ALL',
                    'N/A',
                    2000,
                    'N/A',
                    'BASELINE'
                )
                """
            ),
            {"id": IDEAL_PLAYER_ID},
        )

        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO combine_stats (
                    player_id,
                    height_inches, weight_lbs, hand_size_inches,
                    arm_length_inches, wingspan_inches, forty_yard_dash,
                    ten_yard_split, twenty_yard_shuttle, three_cone,
                    vertical_jump_inches, broad_jump_inches, bench_press_reps
                ) VALUES (
                    :player_id,
                    :height_inches, :weight_lbs, :hand_size_inches,
                    :arm_length_inches, :wingspan_inches, :forty_yard_dash,
                    :ten_yard_split, :twenty_yard_shuttle, :three_cone,
                    :vertical_jump_inches, :broad_jump_inches, :bench_press_reps
                )
                """
            ),
            {"player_id": IDEAL_PLAYER_ID, **IDEAL_COMBINE_ROW},
        )

        connection.execute(
            sqlalchemy.text(
                """
                SELECT setval(
                    pg_get_serial_sequence('"Players"', 'id'),
                    (SELECT COALESCE(MAX(id), 1) FROM "Players")
                )
                """
            )
        )
        connection.execute(
            sqlalchemy.text(
                """
                SELECT setval(
                    pg_get_serial_sequence('combine_stats', 'id'),
                    (SELECT COALESCE(MAX(id), 1) FROM combine_stats)
                )
                """
            )
        )
