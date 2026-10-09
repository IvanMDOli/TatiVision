from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGridLayout,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.ui.widgets.series_card import SeriesCard
from app.ui.widgets.responsive_grid import layout_fixed_cards


class SeriesGrid(QWidget):

    seriesSelected = Signal(int)

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.container = QWidget()
        self.grid_layout = QGridLayout(self.container)
        self.grid_layout.setContentsMargins(16, 16, 16, 16)
        self.grid_layout.setHorizontalSpacing(16)
        self.grid_layout.setVerticalSpacing(16)
        self.grid_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        self.scroll_area.setWidget(self.container)
        layout.addWidget(self.scroll_area)

        self.cards = []
        self._column_count = 0

    def render_series(self, series_items):

        while self.grid_layout.count():
            self.grid_layout.takeAt(0)

        for card in self.cards:
            card.deleteLater()

        self.cards = []

        for series in series_items:
            card = SeriesCard(series)
            card.clicked.connect(self.seriesSelected.emit)
            self.cards.append(card)

        self._column_count = 0
        self._layout_cards()

    def resizeEvent(self, event):

        super().resizeEvent(event)
        self._layout_cards()

    def _layout_cards(self):
        self._column_count = layout_fixed_cards(
            self.grid_layout,
            self.scroll_area.viewport().width(),
            SeriesCard.WIDTH,
            self.cards,
            self._column_count,
        )
