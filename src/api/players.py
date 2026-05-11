import math
import sqlalchemy
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field
from sqlalchemy.engine import Connection

from src.api.auth import get_api_key
from src import database as db

router = APIRouter(tags=["players"])

SORT_COL_MAP = {
    "name":             "p.name",
    "position":         "p.position",
    "draft_year":       "p.draft_year",
    "forty_yard_dash":  "c.forty_yard_dash",
    "bench_press_reps": "c.bench_press_reps",
}

# columns of combine_stats
COMBINE_STATS_NUMERIC_COLUMNS: tuple[str, ...] = (
    "height_inches",
    "weight_lbs",
    "hand_size_inches",
    "arm_length_inches",
    "wingspan_inches",
    "forty_yard_dash",
    "ten_yard_split",
    "twenty_yard_shuttle",
    "three_cone",
    "vertical_jump_inches",
    "broad_jump_inches",
    "bench_press_reps",
)

# build a comma separated SELECT fragment
def _combine_columns_sql(alias: str) -> str:
    """E.g. ``alias.height_inches, alias.weight_lbs, ...``."""
    return ", ".join(f"{alias}.{column}" for column in COMBINE_STATS_NUMERIC_COLUMNS)


class CreatePlayer(BaseModel):
    name: str = Field(..., min_length=1)
    position: str = Field(..., min_length=1)
    college: str = Field(..., min_length=1)
    draft_year: int
    team: str = Field(..., min_length=1)
    status: str = Field(..., min_length=1)


class CreatePlayerResponse(BaseModel):
    player_id: str
    success: bool


class PlayerResponse(BaseModel):
    player_id: str
    name: str
    position: str
    college: str
    draft_year: int
    team: str
    status: str


class PlayerSearchResult(BaseModel):
    player_id: str
    name: str
    position: str
    college: str
    draft_year: int
    team: str
    forty_yard_dash: float | None
    bench_press_reps: int | None


class SimilarPlayerEntry(BaseModel):
    player_id: str
    name: str
    position: str
    team: str
    draft_year: int
    similarity_score: int


class SimilarPlayersResponse(BaseModel):
    player_id: str
    name: str
    position: str
    similar_players: list[SimilarPlayerEntry]


def _non_null_combine_measurements(row: dict[str, Any]) -> dict[str, float]:
    """create a non null valued dict of combine stats"""
    measurements: dict[str, float] = {}
    for column in COMBINE_STATS_NUMERIC_COLUMNS:
        raw = row.get(column)
        if raw is not None:
            measurements[column] = float(raw)
    return measurements


def _similarity_score_between_profiles(
    anchor: dict[str, float],
    candidate: dict[str, float],
) -> float:
    """
    Compare two combine measurement dicts. For each metric present on both sides, accumulate squared relative error,
    take RMS (root mean square), then ``100 / (1 + RMS)``. Higher is more similar, no overlap returns 0.0.
    """
    squared_errors: list[float] = []
    for column in COMBINE_STATS_NUMERIC_COLUMNS:
        if column not in anchor or column not in candidate:
            continue
        anchor_value = anchor[column]
        candidate_value = candidate[column]
        denominator = max(abs(anchor_value), 1e-3)
        relative_difference = (anchor_value - candidate_value) / denominator
        squared_errors.append(relative_difference**2)

    if not squared_errors:
        return 0.0

    rms = math.sqrt(sum(squared_errors) / len(squared_errors))
    return 100.0 / (1.0 + rms)


def _fetch_player_with_combine(connection: Connection, player_id: int):
    """Load one player with all numeric combine columns, or None if missing player or no combine_stats row"""
    fragment = _combine_columns_sql("c")
    return (
        connection.execute(
            sqlalchemy.text(
                f"""
                SELECT
                    p.id AS id,
                    p.name AS name,
                    p.position AS position,
                    p.team AS team,
                    p.draft_year AS draft_year,
                    {fragment}
                FROM "Players" p
                INNER JOIN combine_stats c ON c.player_id = p.id
                WHERE p.id = :player_id
                """
            ),
            {"player_id": player_id},
        )
        .mappings()
        .first()
    )


def _fetch_similarity_candidates(
    connection: Connection,
    *,
    exclude_player_id: int,
    anchor_position: str,
    position_only: bool,
    draft_year_min: int | None,
    draft_year_max: int | None,
) -> list[dict[str, Any]]:
    """All other players with combine_stats, excluding the anchor, with optional position and draft year filters"""
    fragment = _combine_columns_sql("c")
    clauses = ["p.id != :exclude_player_id"]
    params: dict[str, Any] = {"exclude_player_id": exclude_player_id}

    if position_only:
        clauses.append("LOWER(p.position) = LOWER(:required_position)")
        params["required_position"] = anchor_position

    if draft_year_min is not None:
        clauses.append("p.draft_year >= :draft_year_min")
        params["draft_year_min"] = draft_year_min

    if draft_year_max is not None:
        clauses.append("p.draft_year <= :draft_year_max")
        params["draft_year_max"] = draft_year_max

    where_sql = " AND ".join(clauses)
    rows = connection.execute(
        sqlalchemy.text(
            f"""
            SELECT
                p.id AS id,
                p.name AS name,
                p.position AS position,
                p.team AS team,
                p.draft_year AS draft_year,
                {fragment}
            FROM "Players" p
            INNER JOIN combine_stats c ON c.player_id = p.id
            WHERE {where_sql}
            """
        ),
        params,
    ).mappings().all()
    return [dict(row) for row in rows]


def _rank_by_combine_similarity(
    anchor_row: dict[str, Any],
    candidate_rows: list[dict[str, Any]],
    maximum_results: int,
) -> list[SimilarPlayerEntry]:
    """Score every candidate vs the anchor, sort best first, return up to ``maximum_results`` with rounded scores"""
    anchor_m = _non_null_combine_measurements(anchor_row)
    scored: list[tuple[float, dict[str, Any]]] = []
    for cand_row in candidate_rows:
        cand_m = _non_null_combine_measurements(cand_row)
        if not cand_m:
            continue
        scored.append((_similarity_score_between_profiles(anchor_m, cand_m), cand_row))

    scored.sort(key=lambda item: item[0], reverse=True)

    ranked: list[SimilarPlayerEntry] = []
    for score, row in scored[:maximum_results]:
        ranked.append(
            SimilarPlayerEntry(
                player_id=str(row["id"]),
                name=row["name"],
                position=row["position"],
                team=row["team"],
                draft_year=row["draft_year"],
                similarity_score=int(round(score)),
            )
        )
    return ranked


@router.get("/players/search/")
def search_players(
    request: Request,
    name: str | None = Query(default=None),
    position: str | None = Query(default=None),
    college: str | None = Query(default=None),
    team: str | None = Query(default=None),
    draft_year: int | None = Query(default=None),
    min_forty: float | None = Query(default=None),
    max_forty: float | None = Query(default=None),
    min_bench: int | None = Query(default=None),
    max_bench: int | None = Query(default=None),
    search_page: int = Query(default=1, ge=1),
    sort_col: str = Query(default="name"),
    sort_order: str = Query(default="asc", pattern="^(asc|desc)$"),
    _: str = Depends(get_api_key),
):
    if sort_col not in SORT_COL_MAP:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort_col. Choose from: {', '.join(sorted(SORT_COL_MAP))}",
        )

    conditions = []
    params: dict = {}

    if name is not None:
        conditions.append("LOWER(p.name) LIKE LOWER(:name)")
        params["name"] = f"%{name}%"
    if position is not None:
        conditions.append("LOWER(p.position) = LOWER(:position)")
        params["position"] = position
    if college is not None:
        conditions.append("LOWER(p.college) LIKE LOWER(:college)")
        params["college"] = f"%{college}%"
    if team is not None:
        conditions.append("LOWER(p.team) LIKE LOWER(:team)")
        params["team"] = f"%{team}%"
    if draft_year is not None:
        conditions.append("p.draft_year = :draft_year")
        params["draft_year"] = draft_year
    if min_forty is not None:
        conditions.append("c.forty_yard_dash >= :min_forty")
        params["min_forty"] = min_forty
    if max_forty is not None:
        conditions.append("c.forty_yard_dash <= :max_forty")
        params["max_forty"] = max_forty
    if min_bench is not None:
        conditions.append("c.bench_press_reps >= :min_bench")
        params["min_bench"] = min_bench
    if max_bench is not None:
        conditions.append("c.bench_press_reps <= :max_bench")
        params["max_bench"] = max_bench

    where_clause = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    order_col = SORT_COL_MAP[sort_col]
    order_dir = "ASC" if sort_order == "asc" else "DESC"
    page_size = 10
    offset = (search_page - 1) * page_size
    params["limit"] = page_size + 1
    params["offset"] = offset

    with db.engine.begin() as connection:
        rows = connection.execute(
            sqlalchemy.text(
                f"""
                SELECT
                    p.id            AS player_id,
                    p.name,
                    p.position,
                    p.college,
                    p.draft_year,
                    p.team,
                    c.forty_yard_dash,
                    c.bench_press_reps
                FROM "Players" p
                LEFT JOIN combine_stats c ON c.player_id = p.id
                {where_clause}
                ORDER BY {order_col} {order_dir}
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        ).mappings().all()

    has_next = len(rows) == page_size + 1
    results = rows[:page_size]

    previous_url = (
        str(request.url.include_query_params(search_page=search_page - 1))
        if search_page > 1
        else None
    )
    next_url = (
        str(request.url.include_query_params(search_page=search_page + 1))
        if has_next
        else None
    )

    return {
        "previous": previous_url,
        "next": next_url,
        "results": [
            PlayerSearchResult(
                player_id=str(r["player_id"]),
                name=r["name"],
                position=r["position"],
                college=r["college"],
                draft_year=r["draft_year"],
                team=r["team"],
                forty_yard_dash=float(r["forty_yard_dash"]) if r["forty_yard_dash"] is not None else None,
                bench_press_reps=int(r["bench_press_reps"]) if r["bench_press_reps"] is not None else None,
            )
            for r in results
        ],
    }


@router.post("/players/", response_model=CreatePlayerResponse)
def create_player(
    body: CreatePlayer,
    _: str = Depends(get_api_key),
) -> CreatePlayerResponse:
    with db.engine.begin() as connection:
        new_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO "Players" (name, position, college, draft_year, team, status)
                VALUES (:name, :position, :college, :draft_year, :team, :status)
                RETURNING id
                """
            ),
            {
                "name": body.name,
                "position": body.position,
                "college": body.college,
                "draft_year": body.draft_year,
                "team": body.team,
                "status": body.status,
            },
        ).scalar_one()
    return CreatePlayerResponse(player_id=str(new_id), success=True)


@router.get("/players/{player_id}/similar", response_model=SimilarPlayersResponse)
def get_similar_players(
    player_id: int,
    limit: int = Query(default=10, ge=1, le=50),
    position_only: bool = False,
    draft_year_min: int | None = Query(default=None),
    draft_year_max: int | None = Query(default=None),
    _: str = Depends(get_api_key),
) -> SimilarPlayersResponse:
    """
    Find players with combine data most similar to ``player_id`` 
    404 if the player is missing, has no combine row, or every combine measurement is NULL.
    """
    if (
        draft_year_min is not None
        and draft_year_max is not None
        and draft_year_min > draft_year_max
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="draft_year_min cannot exceed draft_year_max",
        )

    with db.engine.begin() as connection:
        anchor_row = _fetch_player_with_combine(connection, player_id)

        if anchor_row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player not found or has no combine stats",
            )

        anchor_dict = dict(anchor_row)
        anchor_combine = _non_null_combine_measurements(anchor_dict)
        if not anchor_combine:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Insufficient combine measurements to compute similarity",
            )

        candidate_rows = _fetch_similarity_candidates(
            connection,
            exclude_player_id=player_id,
            anchor_position=str(anchor_dict["position"]),
            position_only=position_only,
            draft_year_min=draft_year_min,
            draft_year_max=draft_year_max,
        )

    similar_players = _rank_by_combine_similarity(anchor_dict, candidate_rows, limit)

    return SimilarPlayersResponse(
        player_id=str(anchor_dict["id"]),
        name=str(anchor_dict["name"]),
        position=str(anchor_dict["position"]),
        similar_players=similar_players,
    )


@router.get("/players/{player_id}", response_model=PlayerResponse)
def get_player(
    player_id: int,
    _: str = Depends(get_api_key),
) -> PlayerResponse:
    with db.engine.begin() as connection:
        row = connection.execute(
            sqlalchemy.text(
                """
                SELECT id, name, position, college, draft_year, team, status
                FROM "Players"
                WHERE id = :id
                """
            ),
            {"id": player_id},
        ).mappings().first()
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found")
    return PlayerResponse(
        player_id=str(row["id"]),
        name=row["name"],
        position=row["position"],
        college=row["college"],
        draft_year=row["draft_year"],
        team=row["team"],
        status=row["status"],
    )
