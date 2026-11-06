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

    inspector = inspect(engine)
    movie_columns = {
        column["name"]
        for column in inspector.get_columns("movies")
    }
    if "watched" not in movie_columns:
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "ALTER TABLE movies "
                "ADD COLUMN watched BOOLEAN NOT NULL DEFAULT 0"
            )

    series_columns = {
        column["name"]
        for column in inspector.get_columns("series")
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
        if "year" not in series_columns:
            connection.exec_driver_sql(
                "ALTER TABLE series ADD COLUMN year INTEGER"
            )
        if "runtime" not in series_columns:
            connection.exec_driver_sql(
                "ALTER TABLE series ADD COLUMN runtime INTEGER"
            )
        if "director" not in series_columns:
            connection.exec_driver_sql(
                "ALTER TABLE series ADD COLUMN director VARCHAR"
            )
        if "favorite" not in series_columns:
            connection.exec_driver_sql(
                "ALTER TABLE series "
                "ADD COLUMN favorite BOOLEAN NOT NULL DEFAULT 0"
            )
        if "watched" not in series_columns:
            connection.exec_driver_sql(
                "ALTER TABLE series "
                "ADD COLUMN watched BOOLEAN NOT NULL DEFAULT 0"
            )
        if "cast_members" not in series_columns:
            connection.exec_driver_sql(
                "ALTER TABLE series ADD COLUMN cast_members TEXT"
            )

    if "cast_members" not in movie_columns:
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "ALTER TABLE movies ADD COLUMN cast_members TEXT"
            )

    episode_columns = {
        column["name"]
        for column in inspector.get_columns("episodes")
    }
    if "watched" not in episode_columns:
        with engine.begin() as connection:
            connection.exec_driver_sql(
                "ALTER TABLE episodes "
                "ADD COLUMN watched BOOLEAN NOT NULL DEFAULT 0"
            )