import requests
import os

from config.runtime import APP_DIR
from config.user_settings import get_user_setting

_http = requests.Session()


def _tmdb_get(endpoint, params=None):

    api_key = get_user_setting("tmdb_api_key")
    if not api_key:
        raise RuntimeError(
            "TMDB_API_KEY no está configurada."
        )

    request_params = {
        "api_key": api_key,
        "language": "es-ES",
    }
    if params:
        request_params.update(params)

    try:
        response = _http.get(
            f"https://api.themoviedb.org/3/{endpoint}",
            params=request_params,
            timeout=20,
        )
        response.raise_for_status()
    except requests.RequestException as error:
        status_code = (
            error.response.status_code
            if error.response is not None
            else None
        )
        detail = (
            f"TMDb respondió con HTTP {status_code}."
            if status_code
            else "No se pudo conectar con TMDb."
        )
        raise RuntimeError(detail) from error

    return response.json()


def enrich_series(title, seasons, cancel_event=None):
    if cancel_event and cancel_event.is_set():
        return None

    search_result = _tmdb_get(
        "search/tv",
        {"query": title},
    )
    if cancel_event and cancel_event.is_set():
        return None

    results = search_result.get("results", [])
    if not results:
        return None

    series_id = results[0]["id"]
    details = _tmdb_get(f"tv/{series_id}")
    if cancel_event and cancel_event.is_set():
        return None

    season_episodes = {}

    for season_number in sorted(set(seasons)):
        if cancel_event and cancel_event.is_set():
            return None
        if season_number == 0:
            continue

        season_data = _tmdb_get(
            f"tv/{series_id}/season/{season_number}"
        )
        if cancel_event and cancel_event.is_set():
            return None

        season_episodes[season_number] = {
            episode["episode_number"]: episode.get("name")
            for episode in season_data.get("episodes", [])
        }

    if cancel_event and cancel_event.is_set():
        return None

    tmdb_poster_path = _preferred_poster_path(
        "tv",
        series_id,
        details.get("poster_path"),
        cancel_event=cancel_event,
    )
    if cancel_event and cancel_event.is_set():
        return None

    poster_path = download_poster(
        tmdb_poster_path,
        f"series_{series_id}.jpg",
    )

    return {
        "tmdb_id": series_id,
        "genre": ", ".join(
            genre["name"]
            for genre in details.get("genres", [])
        ),
        "overview": details.get("overview") or "",
        "poster_path": poster_path,
        "episodes": season_episodes,
    }


def search_movie(title, year):
    return _tmdb_get(
        "search/movie",
        {"query": title, "year": year},
    )


def search_movie_candidates(title, year, include_tmdb_id=None):
    candidates = search_movie(title, year).get("results", [])
    if include_tmdb_id is None or any(
        candidate.get("id") == include_tmdb_id
        for candidate in candidates
    ):
        return candidates

    details = get_movie_details(include_tmdb_id)
    current_candidate = {
        "id": details["id"],
        "title": details.get("title"),
        "original_title": details.get("original_title"),
        "release_date": details.get("release_date"),
        "overview": details.get("overview"),
    }
    return [current_candidate, *candidates]


def get_movie_details(tmdb_id):
    return _tmdb_get(f"movie/{tmdb_id}")


def get_movie_details_with_credits(tmdb_id):
    return _tmdb_get(
        f"movie/{tmdb_id}",
        {"append_to_response": "credits"},
    )


def _preferred_poster_path(
    media_type,
    tmdb_id,
    fallback_path,
    cancel_event=None,
):
    if cancel_event and cancel_event.is_set():
        return fallback_path

    images = _tmdb_get(
        f"{media_type}/{tmdb_id}/images",
        {"include_image_language": "en,null"},
    )
    if cancel_event and cancel_event.is_set():
        return fallback_path

    return next(
        (
            poster["file_path"]
            for poster in images.get("posters", [])
            if poster.get("iso_639_1") == "en" and poster.get("file_path")
        ),
        fallback_path,
    )


def get_movie_credits(tmdb_id):
    return _tmdb_get(f"movie/{tmdb_id}/credits")

def get_director(credits):

    for person in credits["crew"]:

        if person["job"] == "Director":

            return person["name"]

    return None

def download_poster(
    poster_path,
    filename
):

    if not poster_path:
        return None

    url = (
        "https://image.tmdb.org/t/p/w500"
        + poster_path
    )

    response = _http.get(url, timeout=20)
    response.raise_for_status()

    poster_directory = APP_DIR / "cache" / "posters"
    poster_directory.mkdir(parents=True, exist_ok=True)
    save_path = poster_directory / filename

    with open(save_path, "wb") as file:

        file.write(response.content)

    return os.path.relpath(save_path, APP_DIR)

def enrich_movie(title, year, tmdb_id=None):

    if tmdb_id is None:
        search_result = search_movie(title, year)

        if not search_result.get("results"):

            print(f"No se encontró: {title}")
            return None

        tmdb_id = search_result["results"][0]["id"]

    details = get_movie_details_with_credits(
        tmdb_id
    )

    director = get_director(
        details.get("credits", {})
    )

    poster_file = f"movie_{tmdb_id}.jpg"

    tmdb_poster_path = _preferred_poster_path(
        "movie",
        tmdb_id,
        details.get("poster_path"),
    )
    poster_path = download_poster(
        tmdb_poster_path,
        poster_file
    )

    return {
        "tmdb_id": tmdb_id,
        "title": details.get("original_title") or details["title"],
        "year": (
            int((details.get("release_date") or "")[:4])
            if (details.get("release_date") or "")[:4].isdigit()
            else None
        ),
        "director": director,
        "genre": ", ".join(
            genre["name"]
            for genre in details.get("genres", [])
        ),
        "runtime": details.get("runtime"),
        "overview": details.get("overview") or "",
        "poster_path": poster_path
    }
