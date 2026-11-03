from PySide6.QtCore import Signal
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QScrollArea, QVBoxLayout, QWidget

from app.ui.widgets.movie_row import (
    MovieRow,
    catalog_separator,
    group_catalog_items,
)


class SeriesGrid(QWidget):
    seriesSelected = Signal(int)
    favoriteChanged = Signal(int, bool)
    watchedChanged = Signal(int, bool)

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
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(8)
        content_layout.addLayout(self.layout)
        self.scroll_area.setWidget(self.container)
        outer_layout.addWidget(self.scroll_area)
        self.rows = []
        self.cards = []

    def render_series(
        self,
        series_items,
        sort_order="title_asc",
        selected_genre=None,
    ):
        self._clear_rows()
        self.cards.clear()
        grouped_items = group_catalog_items(
            series_items,
            sort_order,
            selected_genre,
        )
        for index, (title, items) in enumerate(grouped_items):
            if index:
                self.layout.addWidget(catalog_separator())
            row = MovieRow(title, items, self.seriesSelected.emit, "series")
            row.favoriteChanged.connect(self.favoriteChanged.emit)
            row.watchedChanged.connect(self.watchedChanged.emit)
            row.cardAdded.connect(self.cards.append)
            self.layout.addWidget(row)
            self.rows.append(row)
        for row in self.rows:
            row.start_render()
        self.layout.addStretch()

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

    def _clear_rows(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget:
                if isinstance(widget, MovieRow):
                    widget.cancel_render()
                widget.deleteLater()
        self.rows = []
        self.cards = []

    def cancel_render(self):
        for row in self.rows:
            row.cancel_render()
