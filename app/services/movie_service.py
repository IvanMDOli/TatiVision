from app.models.database import SessionLocal
from app.models.movie import Movie
from app.scanner.path_utils import is_path_within_root


def save_movie(movie_data):
    save_movies([movie_data])


def save_movies(movie_data_list):
    movie_data_list = list(movie_data_list)
    if not movie_data_list:
        return 0

    session = SessionLocal()
    try:
        paths = list({
            movie_data["full_path"]
            for movie_data in movie_data_list
        })
        existing_paths = set()
        for index in range(0, len(paths), 500):
            existing_paths.update(
                path
                for (path,) in session.query(Movie.video_path)
                .filter(Movie.video_path.in_(paths[index:index + 500]))
                .all()
            )

        new_movies = []
        for movie_data in movie_data_list:
            movie_path = movie_data["full_path"]
            if movie_path in existing_paths:
                continue
            existing_paths.add(movie_path)
            new_movies.append(Movie(
                title=movie_data["title"],
                year=movie_data["year"],
                video_path=movie_path,
            ))
        if not new_movies:
            return 0

        session.add_all(new_movies)
        session.commit()
        return len(new_movies)

    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_all_movies(root_path=None):

    session = SessionLocal()

    query = (
        session.query(Movie)
        .order_by(Movie.title)
    )
    if root_path is not None:
        query = query.filter(Movie.video_path.isnot(None))

    try:
        movies = query.all()
        if root_path is not None:
            movies = [
                movie
                for movie in movies
                if is_path_within_root(movie.video_path, root_path)
            ]
        return movies
    finally:
        session.close()


def delete_movies_by_ids(movie_ids):

    ids = list(set(movie_ids))
    if not ids:
        return 0

    session = SessionLocal()

    try:
        deleted_count = (
            session.query(Movie)
            .filter(Movie.id.in_(ids))
            .delete(synchronize_session=False)
        )
        session.commit()
        return deleted_count

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def get_movies_without_metadata(root_path=None):

    session = SessionLocal()

    query = (
        session.query(Movie)
        .filter(Movie.tmdb_id == None)
    )
    if root_path is not None:
        query = query.filter(Movie.video_path.isnot(None))

    try:
        movies = query.all()
        if root_path is not None:
            movies = [
                movie
                for movie in movies
                if is_path_within_root(movie.video_path, root_path)
            ]
        return movies
    finally:
        session.close()


def update_movie_metadata(
    movie_id,
    metadata
):

    session = SessionLocal()

    movie = (
        session.query(Movie)
        .filter_by(id=movie_id)
        .first()
    )

    if movie:

        movie.tmdb_id = metadata["tmdb_id"]
        if metadata.get("title"):
            movie.title = metadata["title"]
        if "year" in metadata:
            movie.year = metadata["year"]
        movie.director = metadata["director"]
        movie.genre = metadata["genre"]
        movie.runtime = metadata["runtime"]
        movie.overview = metadata["overview"]
        movie.poster_path = metadata.get("poster_path") or ""

        session.commit()

    session.close()


def search_movies(text):

    session = SessionLocal()

    movies = (
        session.query(Movie)
        .filter(
            Movie.title.contains(text)
        )
        .all()
    )

    session.close()

    return movies

def get_movie_by_id(movie_id):

    session = SessionLocal()

    movie = (
        session.query(Movie)
        .filter_by(id=movie_id)
        .first()
    )

    session.close()

    return movie

def get_movies_by_genre(
    genre_name
):

    session = SessionLocal()

    movies = (
        session.query(Movie)
        .all()
    )

    session.close()

    return [

        movie

        for movie in movies

        if movie.genre
        and genre_name in movie.genre

    ]

def toggle_favorite(movie_id):

    session = SessionLocal()

    try:
        movie = (
            session.query(Movie)
            .filter_by(id=movie_id)
            .first()
        )

        if movie is None:
            raise LookupError(
                f"No se encontró la película con id {movie_id}"
            )

        movie.favorite = not bool(movie.favorite)
        session.commit()

        return bool(movie.favorite)

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def toggle_watched(movie_id):

    session = SessionLocal()

    try:
        movie = (
            session.query(Movie)
            .filter_by(id=movie_id)
            .first()
        )

        if movie is None:
            raise LookupError(
                f"No se encontró la película con id {movie_id}"
            )

        movie.watched = not bool(movie.watched)
        session.commit()

        return bool(movie.watched)

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def get_favorite_movies():

    session = SessionLocal()

    movies = (
        session.query(Movie)
        .filter_by(favorite=True)
        .all()
    )

    session.close()

    return movies

def get_all_genres(root_path=None):

    session = SessionLocal()

    try:
        movies = session.query(Movie).all()
        if root_path is not None:
            movies = [
                movie
                for movie in movies
                if is_path_within_root(movie.video_path, root_path)
            ]
    finally:
        session.close()

    genres = set()

    for movie in movies:

        if movie.genre:

            for genre in movie.genre.split(","):

                genres.add(
                    genre.strip()
                )

    return sorted(genres)

def get_movies_grouped_by_genre(movies=None):

    if movies is None:
        session = SessionLocal()

        try:
            movies = session.query(Movie).all()
        finally:
            session.close()

    grouped = {}

    for movie in movies:

        genres = [
            genre.strip()
            for genre in (movie.genre or "").split(",")
            if genre.strip()
        ] or ["Sin género"]

        for genre in genres:

            if genre not in grouped:

                grouped[genre] = []

            grouped[genre].append(
                movie
            )

    return grouped
