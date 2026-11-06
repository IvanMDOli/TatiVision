from itertools import chain

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QScrollArea,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.ui.widgets.movie_card import MovieCard
from app.ui.widgets.movie_row import (
    MovieRow,
    catalog_separator,
    group_catalog_items,
)
from app.ui.widgets.responsive_grid import layout_fixed_cards
from app.ui.widgets.series_card import SeriesCard


class SeriesGrid(QWidget):
    seriesSelected = Signal(int)
    favoriteChanged = Signal(int, bool)
    watchedChanged = Signal(int, bool)
    renderFinished = Signal()

    def __init__(self):
        super().__init__()
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet(
            "QScrollArea { background-color: #101417; }"
            "QScrollArea > QWidget > QWidget { background-color: #101417; }"
        )
        self.container = QWidget()
        self.container.setObjectName("catalogContent")
        self.container.setStyleSheet(
            "QWidget#catalogContent { background-color: #101417; }"
        )
        content_layout = QVBoxLayout(self.container)
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
        self.pages = QStackedWidget()
        self.rows_page = QWidget()
        self.layout = QVBoxLayout(self.rows_page)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        self.cards_page = QWidget()
        self.cards_layout = QGridLayout(self.cards_page)
        self.cards_layout.setContentsMargins(13, 8, 13, 8)
        self._card_spacing = round(13 * MovieCard.CARD_SCALE)
        self.cards_layout.setSpacing(self._card_spacing)
        self.pages.addWidget(self.rows_page)
        self.pages.addWidget(self.cards_page)
        content_layout.addWidget(self.pages)
        self.scroll_area.setWidget(self.container)
        outer_layout.addWidget(self.scroll_area)
        self.rows = []
        self.cards = []
        self._pending_cards = iter(())
        self._grid_columns = 0
        self._spread_cards = False
        self._card_render_timer = QTimer(self)
        self._card_render_timer.setInterval(8)
        self._card_render_timer.timeout.connect(self._render_next_card_batch)
        self._rows_to_start = []
        self._next_row_to_start = 0
        self._row_start_timer = QTimer(self)
        self._row_start_timer.setInterval(1)
        self._row_start_timer.timeout.connect(self._start_next_row)
        self._rendering = False

    def render_series(
        self,
        series_items,
        sort_order="title_asc",
        selected_genre=None,
        group_by_genre=True,
    ):
        self.cancel_render()
        self._clear_rows()
        self._clear_cards()
        self._rendering = True
        self.cards.clear()
        self._spread_cards = not group_by_genre
        if group_by_genre:
            self.pages.setCurrentWidget(self.rows_page)
            grouped_items = group_catalog_items(
                series_items,
                sort_order,
                selected_genre,
                group_by_genre,
            )
            total_cards = sum(len(items) for _, items in grouped_items)
            for index, (title, items) in enumerate(grouped_items):
                if index:
                    self.layout.addWidget(catalog_separator())
                row = MovieRow(title, items, self.seriesSelected.emit, "series")
                row.favoriteChanged.connect(self.favoriteChanged.emit)
                row.watchedChanged.connect(self.watchedChanged.emit)
                row.cardAdded.connect(self.cards.append)
                row.renderFinished.connect(self._row_rendered)
                self.layout.addWidget(row)
                self.rows.append(row)
            self._pending_rows = len(self.rows)
            if total_cards > 8:
                self._rows_to_start = self.rows.copy()
                self._next_row_to_start = 0
                self._row_start_timer.start()
            else:
                for row in self.rows:
                    row.start_render()
            self.layout.addStretch()
            if not self.rows:
                self._finish_render()
            return

        self.pages.setCurrentWidget(self.cards_page)
        self._pending_cards = iter(series_items)
        if series_items:
            if len(series_items) > 8:
                self._card_render_timer.start()
            else:
                self._render_next_card_batch()
        else:
            self._finish_render()

    def _render_next_card_batch(self):
        for _ in range(8):
            try:
                series = next(self._pending_cards)
            except StopIteration:
                self._card_render_timer.stop()
                self._layout_cards()
                self._finish_render()
                return

            card = SeriesCard(series)
            card.clicked.connect(self.seriesSelected.emit)
            card.favoriteChanged.connect(self.favoriteChanged.emit)
            card.watchedChanged.connect(self.watchedChanged.emit)
            self.cards.append(card)

        self._layout_cards()
        try:
            next_series = next(self._pending_cards)
        except StopIteration:
            self._finish_render()
        else:
            self._pending_cards = chain(
                (next_series,),
                self._pending_cards,
            )
            self._card_render_timer.start()

    def _layout_cards(self):
        self.cards_layout.setHorizontalSpacing(self._card_spacing)
        self._grid_columns = layout_fixed_cards(
            self.cards_layout,
            self.cards_page.width(),
            MovieCard.CARD_WIDTH,
            self.cards,
            self._grid_columns,
            spread=self._spread_cards,
        )

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.pages.currentWidget() == self.cards_page and self.cards:
            QTimer.singleShot(0, self._layout_cards)

    def _clear_rows(self):
        self._row_start_timer.stop()
        self._rows_to_start = []
        self._next_row_to_start = 0
        self._card_render_timer.stop()
        for row in self.rows:
            row.cancel_render()
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.rows = []

    def _clear_cards(self):
        while self.cards_layout.count():
            item = self.cards_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()

    def cancel_render(self):
        self._row_start_timer.stop()
        self._rows_to_start = []
        self._next_row_to_start = 0
        self._card_render_timer.stop()
        self._rendering = False
        for row in self.rows:
            row.cancel_render()

    def _finish_render(self):
        if not self._rendering:
            return
        self._rendering = False
        self.renderFinished.emit()

    def _row_rendered(self):
        self._pending_rows -= 1
        if self._pending_rows == 0:
            self._finish_render()

    def _start_next_row(self):
        if self._next_row_to_start >= len(self._rows_to_start):
            self._row_start_timer.stop()
            self._rows_to_start = []
            return

        row = self._rows_to_start[self._next_row_to_start]
        self._next_row_to_start += 1
        row.start_render()
        if self._next_row_to_start >= len(self._rows_to_start):
            self._row_start_timer.stop()
            self._rows_to_start = []

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
        self.container.setStyleSheet(
            "QWidget#catalogContent { background-color: "
            f"{surface}; }}"
        )
