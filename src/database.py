from src import config
from sqlalchemy import create_engine

connection_url = config.get_settings().POSTGRES_URI
engine = create_engine(
    connection_url,
    pool_pre_ping=True,
    # Fail quickly if Postgres isn't running (Swagger would otherwise hang on first request).
    connect_args={"connect_timeout": 5},
)
