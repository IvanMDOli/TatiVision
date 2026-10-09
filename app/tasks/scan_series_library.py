from app.metadata.tmdb import enrich_series
from app.scanner.series_scanner import scan_series
from app.services.series_service import (
    sync_series,
    update_series_metadata,
)
from config.user_settings import get_user_setting


def run(root_path=None, update_metadata=True, cancel_event=None):

    root_path = root_path if root_path is not None else get_user_setting("series_path")
    series_items = scan_series(root_path, cancel_event=cancel_event)
    cancelled_during_scan = bool(
        cancel_event and cancel_event.is_set()
    )
    episode_count = 0
    metadata_updated = 0
    not_found = []
    failed = []

    for series_data in series_items:
        if (
            cancel_event
            and cancel_event.is_set()
            and not cancelled_during_scan
        ):
            break

        series_id = sync_series(series_data)
        episode_count += len(series_data["episodes"])

        if update_metadata and not (cancel_event and cancel_event.is_set()):
            try:
                metadata = enrich_series(
                    series_data["title"],
                    [
                        episode["season"]
                        for episode in series_data["episodes"]
                    ],
                    cancel_event=cancel_event,
                )
                if cancel_event and cancel_event.is_set():
                    break
                if metadata is None:
                    not_found.append(series_data["title"])
                    continue

                update_series_metadata(series_id, metadata)
                metadata_updated += 1

            except Exception as error:
                failed.append({
                    "title": series_data["title"],
                    "error": str(error),
                })
                print(
                    f"Error al actualizar {series_data['title']}: {error}"
                )

    return {
        "series_found": len(series_items),
        "episodes_found": episode_count,
        "metadata_updated": metadata_updated,
        "not_found": not_found,
        "failed": failed,
        "cancelled": bool(cancel_event and cancel_event.is_set()),
    }
