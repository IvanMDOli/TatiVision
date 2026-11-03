from PySide6.QtCore import Qt, QTimer, Signal

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea,
    QFrame,
)

from app.ui.widgets.movie_card import (
    MovieCard
)
from app.ui.widgets.series_card import SeriesCard
from app.ui.theme import apply_theme, get_current_theme


def group_catalog_items(items, sort_order="title_asc", selected_genre=None):
    field, _, direction = sort_order.partition("_")
    groups = {}
    if field == "director":
        for item in items:
            names = [
                name.strip()
                for name in (item.director or "").replace("&", ",").split(",")
                if name.strip()
            ] or ["Desconocido"]
            for name in names:
                groups.setdefault(name, []).append(item)
        missing_group = groups.pop("Desconocido", None)
        ordered_groups = sorted(
            groups.items(),
            key=lambda entry: entry[0].casefold(),
            reverse=direction == "desc",
        )
        if missing_group is not None:
            ordered_groups.append(("Desconocido", missing_group))
        return ordered_groups

    if selected_genre:
        return [(selected_genre, list(items))]

    for item in items:
        genres = [
            genre.strip()
            for genre in (item.genre or "").split(",")
            if genre.strip()
        ] or ["Sin género"]
        for genre in genres:
            groups.setdefault(genre, []).append(item)
    return sorted(groups.items(), key=lambda entry: entry[0].casefold())


def catalog_separator():
    separator = QFrame()
    separator.setFrameShape(QFrame.HLine)
    separator.setObjectName("genreSeparator")
    separator.setFixedHeight(1)
    return separator


CAROUSEL_ARROW_STYLESHEET = """
    QPushButton {
        border: 1px solid rgba(255, 255, 255, 55);
        border-radius: 18px;
        background-color: rgba(20, 24, 28, 225);
        color: white;
        font-size: 18px;
    }
    QPushButton:hover {
        background-color: rgba(0, 168, 71, 235);
        border-color: rgba(255, 255, 255, 150);
    }
    QPushButton:pressed {
        background-color: rgba(0, 115, 49, 245);
    }
"""


class MovieRow(QWidget):

    favoriteChanged = Signal(int, bool)
    watchedChanged = Signal(int, bool)
    cardAdded = Signal(object)
    renderFinished = Signal()

    def __init__(
        self,
        title,
        movies,
        click_handler,
        catalog="movies",
    ):

        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        self.catalog = catalog

        self.click_handler = click_handler

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("genreTitle")
        self.title_label.setStyleSheet(
            "color: #e8edef; font-size: 17px; font-weight: 700; "
            "letter-spacing: 0.2px; padding: 2px 0;"
        )

        layout.addWidget(
            self.title_label
        )

        self.card_step = MovieCard.CARD_WIDTH + 13

        self.scroll = QScrollArea()
        self.scroll.setStyleSheet(
            "QScrollArea { background: transparent; }"
            "QScrollArea > QWidget > QWidget { background: transparent; }"
        )

        self.scroll.setWidgetResizable(
            False
        )

        self.scroll.setFrameShape(
            QScrollArea.NoFrame
        )

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll.setFixedHeight(405)

        self.container = QWidget()
        self.container.setObjectName("catalogRowCards")
        self.container.setAttribute(Qt.WA_TranslucentBackground)
        self.container.setStyleSheet("background: transparent;")

        self.row_layout = QHBoxLayout(self.container)
        self.row_layout.setContentsMargins(13, 8, 13, 8)

        self.row_layout.setSpacing(13)

        self.row_layout.setAlignment(
            Qt.AlignLeft
        )

        self.cards = []

        self._card_type = SeriesCard if catalog == "series" else MovieCard
        self._pending_items = iter(movies)
        self._click_handler = click_handler
        self._render_timer = QTimer(self)
        self._render_timer.setInterval(8)
        self._render_timer.timeout.connect(self._render_next_batch)

        self.scroll.setWidget(self.container)
        self.scroll.horizontalScrollBar().rangeChanged.connect(
            lambda *_: self.update_arrows()
        )

        layout.addWidget(
            self.scroll
        )

        self.left_button = QPushButton(
            "❮"
        )

        self.right_button = QPushButton(
            "❯"
        )
        self.left_button.setCursor(Qt.PointingHandCursor)
        self.right_button.setCursor(Qt.PointingHandCursor)

        self.left_button.setFocusPolicy(
            Qt.NoFocus
        )

        self.right_button.setFocusPolicy(
            Qt.NoFocus
        )

        self.left_button.setParent(
            self
        )

        self.right_button.setParent(
            self
        )

        self.left_button.setFixedSize(36, 36)

        self.right_button.setFixedSize(36, 36)

        self.left_button.setStyleSheet(CAROUSEL_ARROW_STYLESHEET)
        self.right_button.setStyleSheet(CAROUSEL_ARROW_STYLESHEET)

        self.left_button.clicked.connect(
            self.scroll_left
        )

        self.right_button.clicked.connect(
            self.scroll_right
        )

        self.scroll.horizontalScrollBar().valueChanged.connect(
            lambda *_: self.update_arrows()
        )

        self.update_arrows()
        apply_theme(self, get_current_theme(), source_theme="dark")

    def start_render(self):
        self._render_next_batch()

    def apply_color_theme(self, theme):
        title_color = "#303b35" if theme == "light" else "#e8edef"
        self.title_label.setStyleSheet(
            f"color: {title_color}; font-size: 17px; font-weight: 700; "
            "letter-spacing: 0.2px; padding: 2px 0;"
        )
        arrow_style = CAROUSEL_ARROW_STYLESHEET
        if theme == "light":
            arrow_style = arrow_style.replace(
                "rgba(20, 24, 28, 225)",
                "rgba(248, 249, 248, 235)",
            ).replace("color: white;", "color: #303b35;")
        self.left_button.setStyleSheet(arrow_style)
        self.right_button.setStyleSheet(arrow_style)
        surface = "#f4f6f5" if theme == "light" else "#101417"
        self.scroll.setStyleSheet(
            "QScrollArea { background: transparent; }"
            "QScrollArea > QWidget > QWidget { "
            f"background-color: {surface}; }}"
        )
        self.container.setStyleSheet("background: transparent;")

    def _render_next_batch(self):
        batch_size = 8
        for _ in range(batch_size):
            try:
                item = next(self._pending_items)
            except StopIteration:
                self._render_timer.stop()
                self.container.adjustSize()
                self._update_container_size()
                self.update_arrows()
                self.renderFinished.emit()
                return

            card = self._card_type(item)
            card.clicked.connect(self._click_handler)
            card.favoriteChanged.connect(self.favoriteChanged.emit)
            card.watchedChanged.connect(self.watchedChanged.emit)
            self.cards.append(card)
            self.row_layout.addWidget(card)
            self.cardAdded.emit(card)

        self.container.adjustSize()
        self._update_container_size()
        self.update_arrows()
        self._render_timer.start()

    def _update_container_size(self):
        margins = self.row_layout.contentsMargins()
        card_count = self.row_layout.count()
        width = (
            margins.left()
            + margins.right()
            + sum(card.width() for card in self.cards)
            + max(0, card_count - 1) * self.row_layout.spacing()
        )
        height = (
            margins.top()
            + margins.bottom()
            + max((card.height() for card in self.cards), default=0)
        )
        width = max(width, self.scroll.viewport().width())
        height = max(height, self.scroll.viewport().height())
        self.container.setMinimumSize(width, height)
        self.container.resize(width, height)

    def cancel_render(self):
        self._render_timer.stop()
        self._pending_items = iter(())

    def resizeEvent(self, event):

        super().resizeEvent(event)
        self._update_container_size()

        center_y = (
            self.scroll.geometry().y()
            + (self.scroll.height() - self.left_button.height()) // 2
        )

        self.left_button.move(
            5,
            center_y
        )

        self.right_button.move(
            self.width() - 41,
            center_y
        )

        self.update_arrows()

    def update_movie_favorite(self, movie_id, is_favorite):

        for card in self.cards:
            if card.movie_id == movie_id:
                card.update_favorite(is_favorite)
                return

    def update_movie_watched(self, movie_id, is_watched):

        for card in self.cards:
            if card.movie_id == movie_id:
                card.update_watched(is_watched)
                return

    def update_arrows(self):

        bar = self.scroll.horizontalScrollBar()

        has_overflow = (
            bar.maximum() > 0
        )

        if not has_overflow:

            self.left_button.hide()

            self.right_button.hide()

            return

        self.left_button.setVisible(
            bar.value() > 0
        )

        self.right_button.setVisible(
            bar.value() < bar.maximum()
        )

    def scroll_right(self):

        bar = self.scroll.horizontalScrollBar()

        bar.setValue(
            bar.value() + self.card_step
        )

    def scroll_left(self):

        bar = self.scroll.horizontalScrollBar()

        bar.setValue(
            bar.value() - self.card_step
        )