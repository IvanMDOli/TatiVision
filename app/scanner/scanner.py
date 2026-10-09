import os
import re


VIDEO_EXTENSIONS = (
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".m4v",
    ".webm",
    ".wmv",
)

YEAR_PATTERN = re.compile(r"(?<!\d)((?:19|20)\d{2})(?!\d)")
RELEASE_TAG_PATTERN = re.compile(
    r"(?i)(?:[\s._-]+)(?:2160p|1080p|720p|480p|"
    r"web[- ]?dl|webrip|hdtv|bluray|blu-ray|"
    r"x26[45]|hevc|h\.?264|aac|ddp|dts|proper|repack|"
    r"yify|rarbg|eztv)(?:$|[\s._-])"
)
GENERIC_FOLDER_PATTERN = re.compile(
    r"(?i)^(?:extras?|featurettes?|samples?|trailers?|"
    r"cd[\s._-]*\d+|disc[\s._-]*\d+|dvd[\s._-]*\d+|"
    r"1080p|720p|2160p|480p)$"
)


def extract_title_year(folder_name):

    title_source = os.path.splitext(folder_name)[0]
    year_matches = list(YEAR_PATTERN.finditer(title_source))
    year_match = year_matches[-1] if year_matches else None
    if year_match and not title_source[:year_match.start()].strip():
        year_match = None
    year = int(year_match.group(1)) if year_match else None
    if year_match:
        title_source = title_source[:year_match.start()]

    title_source = RELEASE_TAG_PATTERN.split(title_source, maxsplit=1)[0]
    title = re.sub(r"[\[\](){}]", " ", title_source)
    title = title.replace(".", " ").replace("_", " ")
    title = re.sub(r"\s+", " ", title).strip(" -_.")

    return title, year


def extract_movie_title_year(video_path, root_path):
    filename = os.path.basename(video_path)
    current_path = os.path.dirname(video_path)
    title_folder = os.path.basename(current_path)
    parent_path = os.path.dirname(current_path)
    normalized_root = os.path.normcase(os.path.abspath(root_path))

    if GENERIC_FOLDER_PATTERN.fullmatch(title_folder):
        title_folder = (
            filename
            if os.path.normcase(os.path.abspath(parent_path)) == normalized_root
            else os.path.basename(parent_path)
        )
    if os.path.normcase(os.path.abspath(current_path)) == normalized_root:
        title_folder = filename

    title, year = extract_title_year(title_folder)
    if not title:
        title, year = extract_title_year(filename)
    return title, year


def scan_movies(root_path, cancel_event=None):

    if not root_path or not os.path.isdir(root_path):
        raise FileNotFoundError(
            f"La carpeta de películas no existe o no está disponible: {root_path}"
        )

    movies = []

    def raise_walk_error(error):
        raise error

    normalized_root = os.path.normcase(os.path.abspath(root_path))
    for current_path, _, files in os.walk(
        root_path,
        onerror=raise_walk_error,
    ):
        if cancel_event and cancel_event.is_set():
            break

        for file in sorted(files, key=str.casefold):
            if cancel_event and cancel_event.is_set():
                break

            if file.lower().endswith(VIDEO_EXTENSIONS):

                full_path = os.path.join(current_path, file)
                title, year = extract_movie_title_year(
                    full_path,
                    normalized_root,
                )

                movies.append({
                    "title": title,
                    "year": year,
                    "video_file": file,
                    "full_path": full_path,
                })

    return movies