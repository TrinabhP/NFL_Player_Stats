import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel

from src.api.auth import get_api_key
from src import database as db

router = APIRouter(tags=["stats"])

VALID_EVENTS = {
    "forty_yard_dash",
    "bench_press_reps",
    "vertical_jump_inches",
    "broad_jump_inches",
    "three_cone",
    "twenty_yard_shuttle",
}

# Lower is better for timed events; higher is better for everything else.
LOWER_IS_BETTER = {"forty_yard_dash", "three_cone", "twenty_yard_shuttle"}


class PositionAverages(BaseModel):
    position: str
    averages: dict


@router.get("/stats/positions/{position}", response_model=PositionAverages)
def get_position_averages(
    position: str,
    _: str = Depends(get_api_key),
) -> PositionAverages:
    with db.engine.begin() as connection:
        row = connection.execute(
            sqlalchemy.text(
                """
                SELECT
                    AVG(c.height_inches)        AS height_inches,
                    AVG(c.weight_lbs)           AS weight_lbs,
                    AVG(c.forty_yard_dash)      AS forty_yard_dash,
                    AVG(c.vertical_jump_inches) AS vertical_jump_inches,
                    AVG(c.broad_jump_inches)    AS broad_jump_inches,
                    AVG(c.bench_press_reps)     AS bench_press_reps,
                    AVG(c.three_cone)           AS three_cone,
                    AVG(c.twenty_yard_shuttle)  AS twenty_yard_shuttle
                FROM combine_stats c
                JOIN "Players" p ON p.id = c.player_id
                WHERE LOWER(p.position) = LOWER(:position)
                """
            ),
            {"position": position},
        ).mappings().first()

    # AVG on an empty set returns NULL rather than no row, so we also check
    # if every column value is NULL meaning the position has no combine data.
    if row is None or all(v is None for v in row.values()):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No combine data found for position '{position}'",
        )

    return PositionAverages(
        position=position,
        averages={k: float(v) if v is not None else None for k, v in row.items()},
    )


@router.get("/stats/top-performers/{event_name}")
def get_top_performers(
    event_name: str,
    limit: int = Query(default=10, ge=1, le=100),
    position: str | None = Query(default=None),
    _: str = Depends(get_api_key),
):
    if event_name not in VALID_EVENTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid event. Choose from: {', '.join(sorted(VALID_EVENTS))}",
        )

    order = "ASC" if event_name in LOWER_IS_BETTER else "DESC"
    position_filter = "AND LOWER(p.position) = LOWER(:position)" if position else ""

    with db.engine.begin() as connection:
        rows = connection.execute(
            sqlalchemy.text(
                f"""
                SELECT
                    p.id            AS player_id,
                    p.name,
                    p.position,
                    p.draft_year,
                    c.{event_name}  AS value
                FROM combine_stats c
                JOIN "Players" p ON p.id = c.player_id
                WHERE c.{event_name} IS NOT NULL
                {position_filter}
                ORDER BY c.{event_name} {order}
                LIMIT :limit
                """
            ),
            {"limit": limit, "position": position},
        ).mappings().all()

    return [
        {
            "player_id": str(r["player_id"]),
            "name": r["name"],
            "position": r["position"],
            "draft_year": r["draft_year"],
            "value": float(r["value"]),
        }
        for r in rows
    ]


@router.get("/stats/top-colleges/")
def get_top_colleges_overall(limit: int = Query(default=10, ge=1, le=100)):

    with db.engine.begin() as connection:
        rows = connection.execute(
            sqlalchemy.text(
                """
                SELECT "Players".college, COUNT(*) AS total_players_drafted
                FROM "Players"
                WHERE "Players".status = 'DRAFTED'
                GROUP BY "Players".college
                ORDER BY total_players_drafted DESC
                LIMIT :limit
                """
            ), {"limit": limit}
        ).mappings().all()

    return [
        {
            "college": r["college"],
            "total_players_drafted": r["total_players_drafted"]
        }
        for r in rows
    ]

