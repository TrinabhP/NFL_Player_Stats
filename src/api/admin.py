from fastapi import APIRouter, Depends, status
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset():
    """
    Reset all the data in the schema. A reason could be the start
    of a new draft. All Players are reset.
    """

    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                TRUNCATE "Players"
                """
            )
        )
        connection.execute(
            sqlalchemy.text(
                """
                TRUNCATE combine_stats
                """
            )
        )


        
