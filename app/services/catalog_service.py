import os
import shutil
from uuid import uuid4

from sqlalchemy import inspect

from app.models.database import engine
from app.ui.poster_utils import invalidate_poster_cache
from config.runtime import APP_DIR
from config.user_settings import (
    clear_libraries,
    get_user_settings,
    save_user_settings,
)


def reset_catalog(database_engine=None, poster_directory=None):
    database_engine = database_engine or engine
    poster_directory = poster_directory or APP_DIR / "cache" / "posters"
    settings_before = get_user_settings()
    poster_backup = poster_directory.with_name(
        f"{poster_directory.name}.reset-{uuid4().hex}"
    )
    moved_posters = False

    if poster_directory.exists():
        os.replace(poster_directory, poster_backup)
        moved_posters = True

    try:
        with database_engine.begin() as connection:
            tables = set(inspect(connection).get_table_names())
            for table in ("episodes", "series", "movies"):
                if table in tables:
                    connection.exec_driver_sql(f"DELETE FROM {table}")
            if "sqlite_sequence" in tables:
                connection.exec_driver_sql(
                    "DELETE FROM sqlite_sequence "
                    "WHERE name IN ('episodes', 'series', 'movies')"
                )

            clear_libraries()
    except Exception as error:
        recovery_errors = []
        try:
            if get_user_settings() != settings_before:
                save_user_settings(settings_before)
        except Exception as recovery_error:
            recovery_errors.append(
                f"No se pudo restaurar la configuración: {recovery_error}"
            )

        try:
            if moved_posters:
                if poster_directory.exists():
                    raise FileExistsError(
                        f"La carpeta de pósteres reapareció durante el reset: "
                        f"{poster_directory}"
                    )
                os.replace(poster_backup, poster_directory)
        except OSError as recovery_error:
            recovery_errors.append(
                f"No se pudieron restaurar los pósteres: {recovery_error}"
            )

        invalidate_poster_cache()
        if recovery_errors:
            raise RuntimeError(
                f"Falló el borrado del catálogo: {error}. "
                + " ".join(recovery_errors)
            ) from error
        raise

    invalidate_poster_cache()
    if moved_posters:
        try:
            shutil.rmtree(poster_backup)
        except OSError as error:
            raise RuntimeError(
                "El catálogo y las bibliotecas se borraron, pero no se pudo "
                f"eliminar el respaldo temporal de pósteres "
                f"{poster_backup}: {error}"
            ) from error
