from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError

from src.api import players as players_routes
from src.api import admin as admin
from src.api import info as info

description = """
NFL combine prospect records: create and query players persisted in Postgres.
Protected routes expect header `access_token` matching configured `API_KEY`.
"""

tags_metadata = [
    {"name": "players", "description": "Create and retrieve player profiles."},
]

app = FastAPI(
    title="NFL Player Stats",
    description=description,
    version="0.1.0",
    openapi_tags=tags_metadata,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(_request: Request, exc: SQLAlchemyError):
    """Surface DB errors in JSON so /docs does not show a blank 500."""
    detail = str(exc.orig) if getattr(exc, "orig", None) else str(exc)
    return JSONResponse(status_code=500, content={"detail": detail})


app.include_router(players_routes.router)
app.include_router(admin.router)
app.include_router(info.router)


@app.get("/")
async def root():
    return {"message": "NFL Player Stats API"}
