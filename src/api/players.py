import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, Field

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
