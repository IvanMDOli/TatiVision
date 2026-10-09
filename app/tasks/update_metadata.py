from app.metadata.tmdb import (
    enrich_movie,
    search_movie,
    search_movie_candidates,
)
from app.scanner.scanner import extract_movie_title_year

from app.services.movie_service import (
    get_movies_without_metadata,
    update_movie_metadata,
    get_all_movies,
)


def run(
    force_update=False,
    candidate_selector=None,
    root_path=None,
    movie_id=None,
    cancel_event=None,
    progress_callback=None,
):
    if force_update or movie_id is not None:
        movies = get_all_movies(root_path)
    else:
        movies = get_movies_without_metadata(root_path)
    if movie_id is not None:
        movies = [movie for movie in movies if movie.id == movie_id]

    print(
        f"Películas pendientes: {len(movies)}"
    )

    updated = 0
    not_found = 0
    failed = []
    skipped = 0
    cancelled = False
    processed = 0

    for movie in movies:
        if cancel_event and cancel_event.is_set():
            cancelled = True
            break

        try:
            if candidate_selector:
                search_title, search_year = extract_movie_title_year(
                    movie.video_path or "",
                    root_path or "",
                )
                search_title = search_title or movie.title
                search_year = search_year or movie.year
                candidates = search_movie_candidates(
                    search_title,
                    search_year,
                    include_tmdb_id=movie.tmdb_id,
                )
            else:
                candidates = search_movie(movie.title, movie.year).get(
                    "results",
                    [],
                )
            if not candidates:
                not_found += 1
                continue

            selected_tmdb_id = (
                candidate_selector(movie, candidates)
                if candidate_selector
                else candidates[0]["id"]
            )
            if selected_tmdb_id is None:
                skipped += 1
                continue

            metadata = enrich_movie(
                movie.title,
                movie.year,
                tmdb_id=selected_tmdb_id,
            )

            if metadata:

                update_movie_metadata(
                    movie.id,
                    metadata
                )
                updated += 1

                print(
                    f"OK {movie.title}"
                )
            else:
                not_found += 1

        except Exception as error:
            failed.append({
                "title": movie.title or "Sin título",
                "error": str(error),
            })

            print(
                f"ERROR {movie.title}"
            )

            print(error)
        finally:
            processed += 1
            if progress_callback:
                progress_callback(
                    processed,
                    len(movies),
                    updated,
                    movie.title or "Sin título",
                )

    result = {
        "processed": processed,
        "updated": updated,
        "not_found": not_found,
        "failed": failed,
        "skipped": skipped,
        "cancelled": cancelled or bool(
            cancel_event and cancel_event.is_set()
        ),
    }
    if movie_id is not None:
        result["movie_id"] = movie_id
    return result