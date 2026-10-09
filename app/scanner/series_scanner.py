import os
import re

from app.scanner.scanner import VIDEO_EXTENSIONS


EPISODE_PATTERN = re.compile(
    r"(?i)(?:\bS(?P<season>\d{1,2})[\s._-]*E(?P<episode>\d{1,3})\b"
    r"|\b(?P<season_alt>\d{1,2})x(?P<episode_alt>\d{1,3})\b"
    r"|\bSeason[\s._-]*(?P<season_word>\d{1,2})"
    r"[\s._-]*Episode[\s._-]*(?P<episode_word>\d{1,3})\b)"
)
SEASON_PATTERN = re.compile(
    r"(?i)(?:season|s)[\s._-]*(\d{1,2})"
)
RELEASE_TAG_PATTERN = re.compile(
    r"(?i)(?:[\s._-]+)(?:2160p|1080p|720p|480p|web[- ]?dl|webrip|"
    r"hdtv|bluray|blu-ray|x26[45]|hevc|h\.?264|aac|ddp|dts|"
    r"proper|repack|eztv|rarbg)(?:$|[\s._-])"
)


def _episode_title(filename, match):

    title = os.path.splitext(filename[match.end():])[0]
    title = re.sub(r"^[\s._-]+", "", title)
    title = RELEASE_TAG_PATTERN.split(title, maxsplit=1)[0]
    title = title.replace(".", " ").replace("_", " ")
    title = re.sub(r"[\[\](){}]", " ", title)
    title = re.sub(r"\s+", " ", title).strip(" -")

    return title or f"Episodio {_episode_numbers(match)[1]}"


def _episode_numbers(match):
    season = (
        match.group("season")
        or match.group("season_alt")
        or match.group("season_word")
    )
    episode = (
        match.group("episode")
        or match.group("episode_alt")
        or match.group("episode_word")
    )
    return int(season), int(episode)


def _series_title(folder_name):
    title = re.sub(r"\s*\((?:19|20)\d{2}\).*$", "", folder_name)
    title = RELEASE_TAG_PATTERN.split(title, maxsplit=1)[0]
    title = title.replace(".", " ").replace("_", " ")
    title = re.sub(r"\s+", " ", title).strip(" -_.")
    return title or folder_name


def scan_series(root_path, cancel_event=None):

    if not root_path or not os.path.isdir(root_path):
        raise FileNotFoundError(
            f"La carpeta de series no existe o no está disponible: {root_path}"
        )

    series_items = []

    def raise_walk_error(error):
        raise error

    for series_folder in sorted(os.listdir(root_path)):
        if cancel_event and cancel_event.is_set():
            break

        series_path = os.path.join(root_path, series_folder)
        if not os.path.isdir(series_path):
            continue

        episodes = []
        for current_path, _, files in os.walk(
            series_path,
            onerror=raise_walk_error,
        ):
            if cancel_event and cancel_event.is_set():
                break

            season_match = SEASON_PATTERN.search(
                os.path.basename(current_path)
            )

            for filename in sorted(files):
                if cancel_event and cancel_event.is_set():
                    break

                if not filename.lower().endswith(VIDEO_EXTENSIONS):
                    continue

                episode_match = EPISODE_PATTERN.search(filename)
                if not episode_match:
                    continue

                season, episode_number = _episode_numbers(episode_match)
                if season_match:
                    season = int(season_match.group(1))

                episodes.append({
                    "season": season,
                    "episode": episode_number,
                    "title": _episode_title(filename, episode_match),
                    "video_path": os.path.join(current_path, filename),
                })

        if episodes:
            series_items.append({
                "title": _series_title(series_folder),
                "episodes": episodes,
            })

    return series_items
