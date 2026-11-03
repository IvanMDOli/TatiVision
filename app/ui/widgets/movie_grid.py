from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from app.ui.widgets.movie_row import (
    MovieRow,
    catalog_separator,
    group_catalog_items,
)


class MovieGrid(QWidget):
    favoriteChanged = Signal(int, bool)
    watchedChanged = Signal(int, bool)
    renderFinished = Signal()

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(
            "QScrollArea { background-color: #101417; }"
            "QScrollArea > QWidget > QWidget { background-color: #101417; }"
        )
        self.grid_container = QWidget()
        self.grid_container.setObjectName("catalogContent")
        self.grid_container.setStyleSheet(
            "QWidget#catalogContent { background-color: #101417; }"
        )
        content_layout = QVBoxLayout(self.grid_container)
        content_layout.setContentsMargins(18, 14, 18, 20)
        content_layout.setSpacing(8)

        self.context_label = QLabel()
        self.context_label.setObjectName("filteredContext")
        self.context_label.setStyleSheet(
            "color: #c7d0d4; font-size: 16px; font-weight: 700; "
            "padding: 0 0 10px;"
        )
        self.context_label.hide()
        content_layout.addWidget(self.context_label)
        self.rows_layout = QVBoxLayout()
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        self.rows_layout.setSpacing(8)
        content_layout.addLayout(self.rows_layout)
        self.scroll_area.setWidget(self.grid_container)
        layout.addWidget(self.scroll_area)

        self.rows = []
        self.cards = []
        self._items = []
        self._render_click_handler = None
        self._sort_order = "title_asc"
        self._pending_rows = 0

    def render_movies(
        self,
        movies,
        click_handler,
        sort_order="title_asc",
        selected_genre=None,
    ):
        self.cancel_render()
        self._clear_rows()
        self._items = list(movies)
        self._render_click_handler = click_handler
        self._sort_order = sort_order
        self._selected_genre = selected_genre
        self.cards.clear()
        grouped_items = group_catalog_items(
            movies,
            sort_order,
            selected_genre,
        )
        for index, (title, items) in enumerate(grouped_items):
            if index:
                self.rows_layout.addWidget(catalog_separator())
            row = MovieRow(title, items, click_handler)
            self._connect_row(row)
            row.renderFinished.connect(self._row_rendered)
            self.rows_layout.addWidget(row)
            self.rows.append(row)
        self._pending_rows = len(self.rows)
        if not self.rows:
            self.renderFinished.emit()
        for row in self.rows:
            row.start_render()
        self.rows_layout.addStretch()

    def cancel_render(self):
        for row in self.rows:
            row.cancel_render()

    def set_context(self, text):
        self.context_label.setText(text)
        self.context_label.setVisible(bool(text))

    def apply_color_theme(self, theme):
        surface = "#f4f6f5" if theme == "light" else "#101417"
        self.scroll_area.setStyleSheet(
            "QScrollArea { background-color: "
            f"{surface}; }}"
            "QScrollArea > QWidget > QWidget { background-color: "
            f"{surface}; }}"
        )
        self.grid_container.setStyleSheet(
            "QWidget#catalogContent { background-color: "
            f"{surface}; }}"
        )

    def retain_movies(self, movies):
        if self._render_click_handler is None:
            return
        retained_ids = {movie.id for movie in movies}
        retained_items = [
            movie for movie in self._items if movie.id in retained_ids
        ]
        self.render_movies(
            retained_items,
            self._render_click_handler,
            self._sort_order,
            self._selected_genre,
        )

    def _clear_rows(self):
        while self.rows_layout.count():
            item = self.rows_layout.takeAt(0)
            widget = item.widget()
            if widget:
                if isinstance(widget, MovieRow):
                    widget.cancel_render()
                widget.deleteLater()
        self.rows = []
        self.cards = []

    def _connect_row(self, row):
        row.favoriteChanged.connect(self.favoriteChanged.emit)
        row.watchedChanged.connect(self.watchedChanged.emit)
        row.cardAdded.connect(self.cards.append)

    def _row_rendered(self):
        self._pending_rows -= 1
        if self._pending_rows == 0:
            self.renderFinished.emit()

    def update_movie_favorite(self, movie_id, is_favorite):
        for row in self.rows:
            row.update_movie_favorite(movie_id, is_favorite)

    def update_movie_watched(self, movie_id, is_watched):
        for row in self.rows:
            row.update_movie_watched(movie_id, is_watched)
