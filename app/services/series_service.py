import json

from sqlalchemy import Integer, cast, func

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


def get_series_for_metadata(root_path=None, force_update=False):
    series_items = get_all_series(root_path)
    if force_update:
        return series_items
    return [
        series
        for series in series_items
        if (
            series.tmdb_id is None
            or not series.cast_members
            or series.cast_members.strip() in ("[]", "null")
        )
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

        existing_episodes = {}
        if series_data["episodes"]:
            for episode in (
                session.query(Episode)
                .filter_by(series_id=series.id)
                .all()
            ):
                existing_episodes.setdefault(
                    (episode.season, episode.episode),
                    episode,
                )

        for episode_data in series_data["episodes"]:
            episode = existing_episodes.get(
                (episode_data["season"], episode_data["episode"])
            )
            if episode is None:
                episode = Episode(
                    series_id=series.id,
                    season=episode_data["season"],
                    episode=episode_data["episode"],
                    watched=False,
                )
                session.add(episode)
                episode.title = episode_data["title"]
                series.watched = False
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
        series.year = metadata.get("year")
        series.runtime = metadata.get("runtime")
        series.genre = metadata["genre"]
        series.overview = metadata["overview"]
        series.director = metadata.get("director") or ""
        series.cast_members = json.dumps(
            metadata.get("cast_members") or [],
            ensure_ascii=False,
        )
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


def set_episode_watched(episode_id, watched):
    session = SessionLocal()
    try:
        episode = session.query(Episode).filter_by(id=episode_id).first()
        if episode is None:
            raise LookupError(f"No se encontró el episodio con id {episode_id}")
        episode.watched = bool(watched)
        session.flush()
        _update_series_watched(session, episode.series_id)
        episode_watched = bool(episode.watched)
        session.commit()
        return episode_watched
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def set_season_watched(series_id, season, watched):
    session = SessionLocal()
    try:
        (
            session.query(Episode)
            .filter_by(series_id=series_id, season=season)
            .update(
                {Episode.watched: bool(watched)},
                synchronize_session=False,
            )
        )
        series_watched = _update_series_watched(session, series_id)
        session.commit()
        return series_watched
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def set_series_watched(series_id, watched):
    session = SessionLocal()
    try:
        series = session.query(Series).filter_by(id=series_id).first()
        if series is None:
            raise LookupError(f"No se encontró la serie con id {series_id}")
        (
            session.query(Episode)
            .filter_by(series_id=series_id)
            .update(
                {Episode.watched: bool(watched)},
                synchronize_session=False,
            )
        )
        series.watched = bool(watched)
        series_watched = bool(series.watched)
        session.commit()
        return series_watched
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def set_series_favorite(series_id, favorite):
    session = SessionLocal()
    try:
        series = session.query(Series).filter_by(id=series_id).first()
        if series is None:
            raise LookupError(f"No se encontró la serie con id {series_id}")
        series.favorite = bool(favorite)
        is_favorite = bool(series.favorite)
        session.commit()
        return is_favorite
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def _update_series_watched(session, series_id):
    series = session.query(Series).filter_by(id=series_id).first()
    if series is None:
        raise LookupError(f"No se encontró la serie con id {series_id}")
    episode_count, watched_count = (
        session.query(
            func.count(Episode.id),
            func.coalesce(func.sum(cast(Episode.watched, Integer)), 0),
        )
        .filter_by(series_id=series_id)
        .one()
    )
    series.watched = bool(episode_count) and watched_count == episode_count
    return bool(series.watched)
