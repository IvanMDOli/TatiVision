from app.models.database import SessionLocal
from app.models.episode import Episode
from app.models.series import Series
from app.scanner.path_utils import is_path_within_root


def get_all_series(root_path=None):

    session = SessionLocal()
    try:
        series_items = session.query(Series).order_by(Series.title).all()
        if root_path is None:
            return series_items

        episode_paths = session.query(
            Episode.series_id,
            Episode.video_path,
        ).all()
        visible_series_ids = {
            series_id
            for series_id, video_path in episode_paths
            if is_path_within_root(video_path, root_path)
        }
        return [
            series
            for series in series_items
            if series.id in visible_series_ids
        ]
    finally:
        session.close()


def get_all_series_genres(root_path=None):

    genres = set()
    for series in get_all_series(root_path):
        if series.genre:
            genres.update(
                genre.strip()
                for genre in series.genre.split(",")
                if genre.strip()
            )

    return sorted(genres)


def get_series_for_metadata(root_path=None, force_update=False):
    series_items = get_all_series(root_path)
    if force_update:
        return series_items
    return [
        series
        for series in series_items
        if series.tmdb_id is None
    ]


def get_series_by_id(series_id, root_path=None):

    session = SessionLocal()
    try:
        series = (
            session.query(Series)
            .filter_by(id=series_id)
            .first()
        )
        if series is None or root_path is None:
            return series

        episodes = (
            session.query(Episode)
            .filter_by(series_id=series_id)
            .all()
        )
        return (
            series
            if any(
                is_path_within_root(episode.video_path, root_path)
                for episode in episodes
            )
            else None
        )
    finally:
        session.close()


def get_episodes_for_series(series_id, root_path=None):
    session = SessionLocal()
    try:
        episodes = (
            session.query(Episode)
            .filter_by(series_id=series_id)
            .order_by(Episode.season, Episode.episode)
            .all()
        )
        if root_path is not None:
            episodes = [
                episode
                for episode in episodes
                if is_path_within_root(episode.video_path, root_path)
            ]
        return episodes
    finally:
        session.close()


def sync_series(series_data):

    session = SessionLocal()
    try:
        series = (
            session.query(Series)
            .filter_by(title=series_data["title"])
            .first()
        )
        series_has_metadata = bool(series and series.tmdb_id)
        if series is None:
            series = Series(
                title=series_data["title"],
                overview="",
                poster_path="",
            )
            session.add(series)
            session.flush()

        for episode_data in series_data["episodes"]:
            episode = (
                session.query(Episode)
                .filter_by(
                    series_id=series.id,
                    season=episode_data["season"],
                    episode=episode_data["episode"],
                )
                .first()
            )
            if episode is None:
                episode = Episode(
                    series_id=series.id,
                    season=episode_data["season"],
                    episode=episode_data["episode"],
                )
                session.add(episode)
                episode.title = episode_data["title"]
            elif not series_has_metadata:
                episode.title = episode_data["title"]
            episode.video_path = episode_data["video_path"]

        series_id = series.id
        session.commit()
        return series_id

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()


def update_series_metadata(series_id, metadata):

    session = SessionLocal()
    try:
        series = (
            session.query(Series)
            .filter_by(id=series_id)
            .first()
        )
        if series is None:
            raise LookupError(
                f"No se encontró la serie con id {series_id}"
            )

        series.tmdb_id = metadata["tmdb_id"]
        series.genre = metadata["genre"]
        series.overview = metadata["overview"]
        if metadata["poster_path"]:
            series.poster_path = metadata["poster_path"]

        for episode in (
            session.query(Episode)
            .filter_by(series_id=series_id)
            .all()
        ):
            season_episodes = metadata["episodes"].get(
                episode.season,
                {},
            )
            tmdb_title = season_episodes.get(episode.episode)
            if tmdb_title:
                episode.title = tmdb_title

        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
