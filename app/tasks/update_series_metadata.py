from app.metadata.tmdb import enrich_series
from app.services.series_service import (
    get_episodes_for_series,
    get_series_for_metadata,
    update_series_metadata,
)
from config.user_settings import get_user_setting


def run(root_path=None, force_update=False, cancel_event=None):
    root_path = (
        root_path
        if root_path is not None
        else get_user_setting("series_path")
    )
    series_items = get_series_for_metadata(
        root_path,
        force_update=force_update,
    )
    episodes_found = 0
    metadata_updated = 0
    not_found = []
    failed = []

    for series in series_items:
        if cancel_event and cancel_event.is_set():
            break

        episodes = get_episodes_for_series(series.id, root_path)
        episodes_found += len(episodes)

        try:
            metadata = enrich_series(
                series.title,
                [episode.season for episode in episodes],
                cancel_event=cancel_event,
            )
            if cancel_event and cancel_event.is_set():
                break
            if metadata is None:
                not_found.append(series.title or "Serie sin título")
                continue

            update_series_metadata(series.id, metadata)
            metadata_updated += 1
        except Exception as error:
            failed.append({
                "title": series.title or "Serie sin título",
                "error": str(error),
            })

    return {
        "series_found": len(series_items),
        "episodes_found": episodes_found,
        "metadata_updated": metadata_updated,
        "not_found": not_found,
        "failed": failed,
        "cancelled": bool(cancel_event and cancel_event.is_set()),
    }
