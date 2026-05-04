import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.api.auth import get_api_key
from src import database as db

router = APIRouter(tags=["players"])


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
