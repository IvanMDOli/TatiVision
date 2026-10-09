import json
import os
from copy import deepcopy
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import uuid4

from config.runtime import APP_DIR
from config.settings import DEFAULT_SETTINGS


SETTINGS_PATH = APP_DIR / "settings.json"
_settings = None


def has_completed_initial_setup():
    if not SETTINGS_PATH.is_file():
        return False

    try:
        with SETTINGS_PATH.open(encoding="utf-8") as settings_file:
            stored_settings = json.load(settings_file)
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(
            f"No se pudo leer la configuración {SETTINGS_PATH}: {error}"
        ) from error

    if not isinstance(stored_settings, dict):
        return False

    if not isinstance(stored_settings.get("player_mode"), str):
        return False

    if stored_settings["player_mode"] == "custom":
        return bool(
            isinstance(stored_settings.get("custom_player_path"), str)
            and stored_settings["custom_player_path"].strip()
        )

    return stored_settings["player_mode"] in (
        "vlc",
        "system",
        "open_with",
    )


def _read_settings():
    settings = DEFAULT_SETTINGS.copy()
    if SETTINGS_PATH.exists():
        try:
            with SETTINGS_PATH.open(encoding="utf-8") as settings_file:
                stored_settings = json.load(settings_file)
        except (OSError, json.JSONDecodeError) as error:
            raise RuntimeError(
                f"No se pudo leer la configuración {SETTINGS_PATH}: {error}"
            ) from error

        if not isinstance(stored_settings, dict):
            raise RuntimeError(
                f"El formato de configuración es inválido: {SETTINGS_PATH}"
            )
        settings.update(stored_settings)

    if "libraries" not in settings:
        legacy_movie_path = settings.get("movies_path", "")
        legacy_series_path = settings.get("series_path", "")
        libraries = []
        if legacy_movie_path or legacy_series_path:
            libraries.append({
                "id": "legacy-default",
                "name": "Mi biblioteca",
                "description": "Principal",
                "movies_path": legacy_movie_path,
                "series_path": legacy_series_path,
            })
        settings["libraries"] = libraries

    if not isinstance(settings.get("libraries"), list):
        raise RuntimeError(
            f"La lista de bibliotecas es inválida en {SETTINGS_PATH}."
        )
    if not isinstance(settings.get("active_library_id"), str):
        settings["active_library_id"] = ""
    if settings["active_library_id"] not in {
        library.get("id")
        for library in settings["libraries"]
        if isinstance(library, dict)
    }:
        settings["active_library_id"] = (
            settings["libraries"][0].get("id", "")
            if settings["libraries"]
            and isinstance(settings["libraries"][0], dict)
            else ""
        )
    active_library = get_active_library(settings)
    settings["movies_path"] = (
        active_library.get("movies_path", "") if active_library else ""
    )
    settings["series_path"] = (
        active_library.get("series_path", "") if active_library else ""
    )

    if settings["player_mode"] in ("vlc", "open_with"):
        settings["player_mode"] = "system"
        settings["custom_player_path"] = ""

    _validate_settings(settings)
    return settings


def _validate_settings(settings):
    string_settings = (
        "movies_path",
        "series_path",
        "tmdb_api_key",
        "player_mode",
        "custom_player_path",
    )
    if any(not isinstance(settings.get(name), str) for name in string_settings):
        raise RuntimeError(
            f"Hay valores inválidos en la configuración {SETTINGS_PATH}."
        )
    if settings["player_mode"] not in ("system", "custom"):
        raise RuntimeError(
            f"El reproductor configurado no es válido en {SETTINGS_PATH}."
        )
    if settings["player_mode"] == "custom" and not settings[
        "custom_player_path"
    ].strip():
        raise RuntimeError(
            f"La ruta del reproductor personalizado falta en {SETTINGS_PATH}."
        )
    if settings["player_mode"] == "custom":
        player_path = Path(settings["custom_player_path"])
        if not player_path.is_absolute() or player_path.suffix.casefold() != ".exe":
            raise RuntimeError(
                f"La ruta del reproductor personalizado debe ser absoluta y "
                f"apuntar a un archivo .exe en {SETTINGS_PATH}."
            )
    libraries = settings.get("libraries", [])
    if not isinstance(libraries, list):
        raise RuntimeError(
            f"La lista de bibliotecas es inválida en {SETTINGS_PATH}."
        )
    for library in libraries:
        if not isinstance(library, dict) or any(
            not isinstance(library.get(key), str)
            for key in (
                "id",
                "name",
                "description",
                "movies_path",
                "series_path",
            )
        ):
            raise RuntimeError(
                f"Hay una biblioteca con valores inválidos en "
                f"{SETTINGS_PATH}."
            )
        if not library["name"].strip() or len(library["description"]) > 20:
            raise RuntimeError(
                f"El nombre o la descripción de una biblioteca no son "
                f"válidos en {SETTINGS_PATH}."
            )


def get_user_setting(name):
    global _settings
    if _settings is None:
        _settings = _read_settings()
    if name in ("movies_path", "series_path"):
        library = get_active_library(_settings)
        return library.get(name, "") if library else ""
    return _settings[name]


def get_user_settings():
    global _settings
    if _settings is None:
        _settings = _read_settings()
    return deepcopy(_settings)


def get_libraries():
    return get_user_settings()["libraries"]


def get_active_library(settings=None):
    settings = settings or get_user_settings()
    active_id = settings.get("active_library_id", "")
    return next(
        (
            library
            for library in settings.get("libraries", [])
            if isinstance(library, dict) and library.get("id") == active_id
        ),
        None,
    )


def save_library(name, description, movies_path, series_path):
    settings = get_user_settings()
    library = {
        "id": uuid4().hex,
        "name": name.strip(),
        "description": description.strip(),
        "movies_path": str(Path(movies_path).resolve()) if movies_path else "",
        "series_path": str(Path(series_path).resolve()) if series_path else "",
    }
    settings["libraries"].append(library)
    settings["active_library_id"] = library["id"]
    settings["movies_path"] = library["movies_path"]
    settings["series_path"] = library["series_path"]
    save_user_settings(settings)
    return deepcopy(library)


def select_library(library_id):
    settings = get_user_settings()
    library = next(
        (
            item for item in settings["libraries"]
            if item.get("id") == library_id
        ),
        None,
    )
    if library is None:
        raise LookupError(f"No se encontró la biblioteca {library_id}.")
    settings.update({
        "active_library_id": library["id"],
        "movies_path": library.get("movies_path", ""),
        "series_path": library.get("series_path", ""),
    })
    save_user_settings(settings)
    return deepcopy(library)


def delete_library(library_id):
    settings = get_user_settings()
    matching_library = next(
        (
            library for library in settings["libraries"]
            if library["id"] == library_id
        ),
        None,
    )
    if matching_library is None:
        raise LookupError(f"No se encontró la biblioteca {library_id}.")

    settings["libraries"] = [
        library
        for library in settings["libraries"]
        if library["id"] != library_id
    ]
    if settings["active_library_id"] == library_id:
        active_library = (
            settings["libraries"][0]
            if settings["libraries"]
            else None
        )
        settings["active_library_id"] = (
            active_library["id"] if active_library else ""
        )
        settings["movies_path"] = (
            active_library["movies_path"] if active_library else ""
        )
        settings["series_path"] = (
            active_library["series_path"] if active_library else ""
        )
    save_user_settings(settings)
    return deepcopy(matching_library)


def clear_libraries():
    settings = get_user_settings()
    settings.update({
        "libraries": [],
        "active_library_id": "",
        "movies_path": "",
        "series_path": "",
    })
    save_user_settings(settings)


def save_user_settings(updates):
    global _settings
    settings = get_user_settings()
    settings.update(updates)
    _validate_settings(settings)
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)

    temporary_path = None
    try:
        with NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=SETTINGS_PATH.parent,
            delete=False,
        ) as settings_file:
            json.dump(settings, settings_file, indent=2, ensure_ascii=False)
            settings_file.write("\n")
            temporary_path = Path(settings_file.name)
        os.replace(temporary_path, SETTINGS_PATH)
    except OSError as error:
        if temporary_path and temporary_path.exists():
            temporary_path.unlink()
        raise RuntimeError(
            f"No se pudo guardar la configuración {SETTINGS_PATH}: {error}"
        ) from error

    _settings = settings
    return deepcopy(settings)
