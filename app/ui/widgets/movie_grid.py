from PySide6.QtWidgets import (
    QLabel,
    QWidget,
    QScrollArea,
    QGridLayout,
    QVBoxLayout,
)
from PySide6.QtCore import Qt, QTimer, Signal

from app.ui.widgets.movie_card import (
    MovieCard
)
from app.ui.widgets.responsive_grid import layout_fixed_cards


class MovieGrid(QWidget):

    favoriteChanged = Signal(int, bool)
    watchedChanged = Signal(int, bool)
    renderFinished = Signal()

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout()

        self.setLayout(layout)

        self.scroll_area = QScrollArea()

        self.scroll_area.setWidgetResizable(
            True
        )
        self.scroll_area.setFrameShape(
            QScrollArea.NoFrame
        )
        self.scroll_area.setStyleSheet(
            "QScrollArea { background-color: #101417; }"
            "QScrollArea > QWidget > QWidget { background-color: #101417; }"
        )
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.grid_container = QWidget()
        self.grid_container.setObjectName("catalogContent")
        self.grid_container.setStyleSheet(
            "QWidget#catalogContent { background-color: #101417; }"
        )
        content_layout = QVBoxLayout(self.grid_container)
        content_layout.setContentsMargins(18, 14, 18, 20)
        content_layout.setSpacing(0)

        self.context_label = QLabel()
        self.context_label.setObjectName("filteredContext")
        self.context_label.setStyleSheet(
            "color: #c7d0d4; font-size: 16px; font-weight: 700; "
            "padding: 0 0 10px;"
        )
        self.context_label.hide()
        content_layout.addWidget(self.context_label)

        self.grid_content = QWidget()
        self.grid_content.setStyleSheet(
            "QWidget { background: transparent; }"
        )

        self.grid_layout = QGridLayout(self.grid_content)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setHorizontalSpacing(16)
        self.grid_layout.setVerticalSpacing(16)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        content_layout.addWidget(self.grid_content, 1)

        self.scroll_area.setWidget(
            self.grid_container
        )

        layout.addWidget(
            self.scroll_area
        )

        self.cards = []
        self._cards_by_id = {}
        self._card_signatures = {}
        self._column_count = 0
        self._pending_movies = []
        self._render_click_handler = None
        self._render_timer = QTimer(self)
        self._render_timer.setSingleShot(True)
        self._render_timer.timeout.connect(self._render_next_batch)

    def render_movies(self, movies, click_handler):
        self.cancel_render()
        self.grid_container.hide()
        while self.grid_layout.count():
            self.grid_layout.takeAt(0)

        for card in self._cards_by_id.values():
            card.hide()

        self.cards = []
        self._pending_movies = list(movies)
        self._render_click_handler = click_handler
        self._column_count = 0
        self._render_next_batch()

    def cancel_render(self):
        self._render_timer.stop()
        self._pending_movies = []

    def set_context(self, text):
        self.context_label.setText(text)
        self.context_label.setVisible(bool(text))

    def _render_next_batch(self):
        batch_size = 8
        batch_end = min(len(self._pending_movies), batch_size)
        batch = self._pending_movies[:batch_end]
        del self._pending_movies[:batch_end]

        for movie in batch:
            signature = (
                movie.title,
                movie.year,
                movie.director,
                movie.poster_path,
            )
            card = self._cards_by_id.get(movie.id)
            if card is not None and self._card_signatures[movie.id] != signature:
                card.deleteLater()
                del self._cards_by_id[movie.id]
                del self._card_signatures[movie.id]
                card = None

            if card is None:
                card = MovieCard(movie)
                card.clicked.connect(self._render_click_handler)
                card.favoriteChanged.connect(self.favoriteChanged.emit)
                card.watchedChanged.connect(self.watchedChanged.emit)
                self._cards_by_id[movie.id] = card
                self._card_signatures[movie.id] = signature
            else:
                card.update_favorite(movie.favorite)
                card.update_watched(movie.watched)

            self.cards.append(card)

        self._layout_cards()
        self.grid_layout.invalidate()
        self.grid_layout.activate()

        if self._pending_movies:
            self._render_timer.start(0)
        else:
            self.grid_container.show()
            self.grid_layout.invalidate()
            self.grid_layout.activate()
            for card in self.cards:
                card.show()
            self.grid_container.updateGeometry()
            self.renderFinished.emit()

    def retain_movies(self, movies):
        self.cancel_render()
        retained_ids = {movie.id for movie in movies}
        for movie_id, card in tuple(self._cards_by_id.items()):
            if movie_id in retained_ids:
                continue
            self.grid_layout.removeWidget(card)
            card.hide()
            card.deleteLater()
            del self._cards_by_id[movie_id]
            del self._card_signatures[movie_id]
        self.cards = [
            card
            for card in self.cards
            if card.movie_id in retained_ids
        ]

    def resizeEvent(self, event):

        super().resizeEvent(event)
        self._layout_cards()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(0, self._refresh_visible_layout)

    def _refresh_visible_layout(self):
        if not self.isVisible():
            return
        self._column_count = 0
        self._layout_cards()
        self.grid_layout.activate()
        self.grid_container.updateGeometry()

    def _layout_cards(self):
        self._column_count = layout_fixed_cards(
            self.grid_layout,
            self.scroll_area.viewport().width(),
            MovieCard.CARD_WIDTH,
            self.cards,
            self._column_count,
        )

    def update_movie_favorite(self, movie_id, is_favorite):

        for card in self.cards:
            if card.movie_id == movie_id:
                card.update_favorite(is_favorite)

    def update_movie_watched(self, movie_id, is_watched):

        for card in self.cards:
            if card.movie_id == movie_id:
                card.update_watched(is_watched)