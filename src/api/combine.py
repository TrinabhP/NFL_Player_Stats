import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.api.auth import get_api_key
from src import database as db

router = APIRouter(tags=["combine"])


class CombineStats(BaseModel):
    height_inches: float | None = None
    weight_lbs: float | None = None
    hand_size_inches: float | None = None
    arm_length_inches: float | None = None
    wingspan_inches: float | None = None
    forty_yard_dash: float | None = None
    ten_yard_split: float | None = None
    twenty_yard_shuttle: float | None = None
    three_cone: float | None = None
    vertical_jump_inches: float | None = None
    broad_jump_inches: float | None = None
    bench_press_reps: int | None = None


class CombineStatsResponse(BaseModel):
    player_id: str
    name: str
    position: str
    combine_stats: CombineStats


def _require_player(connection, player_id: int):
    row = connection.execute(
        sqlalchemy.text('SELECT id FROM "Players" WHERE id = :id'),
        {"id": player_id},
    ).first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")


@router.post("/players/{player_id}/combine")
def add_combine_stats(
    player_id: int,
    body: CombineStats,
    _: str = Depends(get_api_key),
):
    with db.engine.begin() as connection:
        _require_player(connection, player_id)
        existing = connection.execute(
            sqlalchemy.text("SELECT id FROM combine_stats WHERE player_id = :pid"),
            {"pid": player_id},
        ).first()
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Combine stats already exist for this player. Use PUT to update.",
            )
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO combine_stats (
                    player_id, height_inches, weight_lbs, hand_size_inches,
                    arm_length_inches, wingspan_inches, forty_yard_dash,
                    ten_yard_split, twenty_yard_shuttle, three_cone,
                    vertical_jump_inches, broad_jump_inches, bench_press_reps
                ) VALUES (
                    :pid, :height, :weight, :hand, :arm, :wing, :forty,
                    :ten, :shuttle, :cone, :vertical, :broad, :bench
                )
                RETURNING id
                """
            ),
            {
                "pid": player_id,
                "height": body.height_inches,
                "weight": body.weight_lbs,
                "hand": body.hand_size_inches,
                "arm": body.arm_length_inches,
                "wing": body.wingspan_inches,
                "forty": body.forty_yard_dash,
                "ten": body.ten_yard_split,
                "shuttle": body.twenty_yard_shuttle,
                "cone": body.three_cone,
                "vertical": body.vertical_jump_inches,
                "broad": body.broad_jump_inches,
                "bench": body.bench_press_reps,
            },
        ).scalar_one()
    return {"combine_id": str(result), "success": True}


@router.put("/players/{player_id}/combine")
def update_combine_stats(
    player_id: int,
    body: CombineStats,
    _: str = Depends(get_api_key),
):
    with db.engine.begin() as connection:
        _require_player(connection, player_id)
        updated = connection.execute(
            sqlalchemy.text(
                """
                UPDATE combine_stats SET
                    height_inches = :height,
                    weight_lbs = :weight,
                    hand_size_inches = :hand,
                    arm_length_inches = :arm,
                    wingspan_inches = :wing,
                    forty_yard_dash = :forty,
                    ten_yard_split = :ten,
                    twenty_yard_shuttle = :shuttle,
                    three_cone = :cone,
                    vertical_jump_inches = :vertical,
                    broad_jump_inches = :broad,
                    bench_press_reps = :bench
                WHERE player_id = :pid
                """
            ),
            {
                "pid": player_id,
                "height": body.height_inches,
                "weight": body.weight_lbs,
                "hand": body.hand_size_inches,
                "arm": body.arm_length_inches,
                "wing": body.wingspan_inches,
                "forty": body.forty_yard_dash,
                "ten": body.ten_yard_split,
                "shuttle": body.twenty_yard_shuttle,
                "cone": body.three_cone,
                "vertical": body.vertical_jump_inches,
                "broad": body.broad_jump_inches,
                "bench": body.bench_press_reps,
            },
        )
        if updated.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No combine stats found for this player. Use POST to create.",
            )
    return {"success": True}


@router.get("/players/{player_id}/combine", response_model=CombineStatsResponse)
def get_combine_stats(
    player_id: int,
    _: str = Depends(get_api_key),
) -> CombineStatsResponse:
    with db.engine.begin() as connection:
        row = connection.execute(
            sqlalchemy.text(
                """
                SELECT
                    p.id, p.name, p.position,
                    c.height_inches, c.weight_lbs, c.hand_size_inches,
                    c.arm_length_inches, c.wingspan_inches, c.forty_yard_dash,
                    c.ten_yard_split, c.twenty_yard_shuttle, c.three_cone,
                    c.vertical_jump_inches, c.broad_jump_inches, c.bench_press_reps
                FROM "Players" p
                JOIN combine_stats c ON c.player_id = p.id
                WHERE p.id = :id
                """
            ),
            {"id": player_id},
        ).mappings().first()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player or combine stats not found",
        )
    return CombineStatsResponse(
        player_id=str(row["id"]),
        name=row["name"],
        position=row["position"],
        combine_stats=CombineStats(
            height_inches=row["height_inches"],
            weight_lbs=row["weight_lbs"],
            hand_size_inches=row["hand_size_inches"],
            arm_length_inches=row["arm_length_inches"],
            wingspan_inches=row["wingspan_inches"],
            forty_yard_dash=row["forty_yard_dash"],
            ten_yard_split=row["ten_yard_split"],
            twenty_yard_shuttle=row["twenty_yard_shuttle"],
            three_cone=row["three_cone"],
            vertical_jump_inches=row["vertical_jump_inches"],
            broad_jump_inches=row["broad_jump_inches"],
            bench_press_reps=row["bench_press_reps"],
        ),
    )
