import os

from app.scanner.scanner import scan_movies
from app.services.movie_service import (
    get_all_movies,
    save_movies,
)
from config.user_settings import get_user_setting


def run(root_path=None, cancel_event=None):
    root_path = root_path if root_path is not None else get_user_setting("movies_path")

    movies = scan_movies(root_path, cancel_event=cancel_event)

    save_movies(movies)

    root_path = os.path.normcase(
        os.path.abspath(root_path)
    )
    missing_movies = []

    for movie in get_all_movies():
        if cancel_event and cancel_event.is_set():
            break
        if not movie.video_path:
            continue

        movie_path = os.path.normcase(
            os.path.abspath(movie.video_path)
        )

        try:
            is_inside_library = (
                os.path.commonpath([root_path, movie_path])
                == root_path
            )
        except ValueError:
            is_inside_library = False

        if not is_inside_library:
            continue

        try:
            os.stat(movie.video_path)
        except FileNotFoundError:
            missing_movies.append({
                "id": movie.id,
                "title": movie.title or "Sin título",
                "path": movie.video_path,
            })

    print(
        f"Biblioteca actualizada: {len(movies)} películas"
    )

    return {
        "scanned": len(movies),
        "missing": missing_movies,
        "cancelled": bool(cancel_event and cancel_event.is_set()),
    }