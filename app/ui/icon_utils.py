from collections import deque
from functools import lru_cache

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QImage, QPainter, QPixmap

from config.runtime import resource_path


def _fill_icon_interior(source):
    image = source.toImage().convertToFormat(QImage.Format_ARGB32)
    width = image.width()
    height = image.height()
    start_x = width // 2
    start_y = height // 2
    start = start_y * width + start_x

    if (image.pixel(start_x, start_y) >> 24) > 16:
        return source

    visited = bytearray(width * height)
    visited[start] = 1
    pending = deque([start])
    region = []
    touches_edge = False

    while pending:
        index = pending.popleft()
        x = index % width
        y = index // width
        region.append(index)
        if x == 0 or y == 0 or x == width - 1 or y == height - 1:
            touches_edge = True

        neighbors = []
        if x > 0:
            neighbors.append(index - 1)
        if x + 1 < width:
            neighbors.append(index + 1)
        if y > 0:
            neighbors.append(index - width)
        if y + 1 < height:
            neighbors.append(index + width)

        for neighbor in neighbors:
            if visited[neighbor]:
                continue
            pixel_x = neighbor % width
            pixel_y = neighbor // width
            if (image.pixel(pixel_x, pixel_y) >> 24) <= 16:
                visited[neighbor] = 1
                pending.append(neighbor)

    if touches_edge:
        return source

    white = QColor(Qt.white).rgba()
    for index in region:
        image.setPixel(index % width, index // width, white)
    return QPixmap.fromImage(image)


@lru_cache(maxsize=64)
def load_ui_icon(name, color=None, filled=False):
    if not name or any(character in name for character in ("/", "\\", ".")):
        raise ValueError("El nombre del ícono debe ser un nombre simple.")

    for extension in ("svg", "png", "ico"):
        icon_path = resource_path(
            f"assets/icons/ui/{name}.{extension}"
        )
        if icon_path.is_file():
            if color is None:
                return QIcon(str(icon_path))

            source = QPixmap(str(icon_path))
            if source.isNull():
                return QIcon()
            if filled:
                source = source.scaled(
                    96,
                    96,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
                source = _fill_icon_interior(source)
            tinted = QPixmap(source.size())
            tinted.fill(Qt.transparent)
            painter = QPainter(tinted)
            painter.drawPixmap(0, 0, source)
            painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
            painter.fillRect(tinted.rect(), QColor(color))
            painter.end()
            return QIcon(tinted)

    return QIcon()
