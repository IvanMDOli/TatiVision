from app.models.database import (
    Base,
    engine
)
from sqlalchemy import inspect

import app.models.movie
import app.models.series
import app.models.episode


def initialize_database():

    Base.metadata.create_all(engine)

    movie_columns = {
        column["name"]
        for column in inspect(engine).get_columns("movies")
    }
    if "watched" not in movie_columns:
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "ALTER TABLE movies "
                "ADD COLUMN watched BOOLEAN NOT NULL DEFAULT 0"
            )

    series_columns = {
        column["name"]
        for column in inspect(engine).get_columns("series")
    }
    with engine.begin() as connection:
        if "genre" not in series_columns:
            connection.exec_driver_sql(
                "ALTER TABLE series ADD COLUMN genre VARCHAR"
            )
        if "tmdb_id" not in series_columns:
            connection.exec_driver_sql(
                "ALTER TABLE series ADD COLUMN tmdb_id INTEGER"
            )