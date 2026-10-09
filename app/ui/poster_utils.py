import re
import unicodedata
from functools import lru_cache
from pathlib import Path

from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter

from config.runtime import APP_DIR, resolve_app_path


def _poster_key(value):
    normalized = unicodedata.normalize("NFKD", value or "")
    without_marks = "".join(
        character
        for character in normalized
        if not unicodedata.combining(character)
    ).casefold()
    return re.sub(r"[^a-z0-9]+", "_", without_marks).strip("_")


@lru_cache(maxsize=1)
def _cached_posters():
    poster_directory = APP_DIR / "cache" / "posters"
    return {
        _poster_key(path.stem): path
        for path in sorted(poster_directory.glob("*"))
        if path.is_file()
    }


def load_poster(poster_path, title):
    candidates = []
    if poster_path:
        candidates.append(Path(resolve_app_path(poster_path)))

    if title:
        cached_poster = _cached_posters().get(_poster_key(title))
        if cached_poster:
            candidates.append(cached_poster)

    for candidate in candidates:
        pixmap = QPixmap(str(candidate))
        if not pixmap.isNull():
            return pixmap

    return QPixmap()


def clear_poster_cache():
    poster_directory = APP_DIR / "cache" / "posters"
    if poster_directory.exists():
        for path in poster_directory.iterdir():
            if path.is_file():
                path.unlink()
    invalidate_poster_cache()


def invalidate_poster_cache():
    _cached_posters.cache_clear()
    _load_scaled_poster.cache_clear()


@lru_cache(maxsize=512)
def _load_scaled_poster(path, modified_ns, width, height):
    source = QPixmap(path)
    if source.isNull():
        return QPixmap()

    scaled = source.scaled(
        width,
        height,
        Qt.KeepAspectRatio,
        Qt.SmoothTransformation,
    )
    canvas = QPixmap(width, height)
    canvas.fill(QColor("#0e1113"))
    painter = QPainter(canvas)
    painter.drawPixmap(
        (width - scaled.width()) // 2,
        (height - scaled.height()) // 2,
        scaled,
    )
    painter.end()
    return canvas


def load_scaled_poster(poster_path, title, width, height):
    candidates = []
    if poster_path:
        candidates.append(Path(resolve_app_path(poster_path)))

    if title:
        cached_poster = _cached_posters().get(_poster_key(title))
        if cached_poster:
            candidates.append(cached_poster)

    for candidate in candidates:
        try:
            modified_ns = candidate.stat().st_mtime_ns
        except OSError:
            continue
        pixmap = _load_scaled_poster(
            str(candidate),
            modified_ns,
            width,
            height,
        )
        if not pixmap.isNull():
            return pixmap

    return QPixmap()
