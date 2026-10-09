from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QStackedWidget, QVBoxLayout, QWidget

from app.ui.views.empty_state_view import EmptyStateView
from app.ui.views.series_detail_view import SeriesDetailView
from app.ui.widgets.series_grid import SeriesGrid


class SeriesCatalogView(QWidget):

    seriesSelected = Signal(int)

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout(self)
        self.context_label = QLabel()
        self.context_label.setStyleSheet(
            "color: #c7d0d4; font-size: 16px; font-weight: 700; "
            "padding: 14px 18px 10px;"
        )
        self.context_label.hide()
        layout.addWidget(self.context_label)
        self.pages = QStackedWidget()
        self.grid = SeriesGrid()
        self.detail = SeriesDetailView()
        self.empty_state = EmptyStateView()
        self.empty_state.set_content(
            "No se encontraron series",
            "La carpeta de series seleccionada no contiene episodios "
            "reconocidos. Elegí otra carpeta desde Ajustes o analizá "
            "nuevamente la biblioteca.",
        )

        self.grid.seriesSelected.connect(
            self.seriesSelected.emit
        )
        self.detail.backRequested.connect(
            self.show_catalog
        )

        self.pages.addWidget(self.grid)
        self.pages.addWidget(self.detail)
        self.pages.addWidget(self.empty_state)
        layout.addWidget(self.pages)

    def render_series(self, series_items, root_path, catalog_has_series=False):

        self.grid.render_series(series_items)
        if not series_items:
            if catalog_has_series:
                self.empty_state.set_content(
                    "No hay series que coincidan",
                    "Probá cambiar la búsqueda o quitar los filtros activos.",
                )
            elif root_path:
                self.empty_state.set_content(
                    "No se encontraron series",
                    "La carpeta de series seleccionada no contiene episodios "
                    "reconocidos. Elegí otra carpeta desde Ajustes o analizá "
                    "nuevamente la biblioteca.",
                )
            else:
                self.empty_state.set_content(
                    "No se seleccionó una carpeta de series",
                    "Abrí Ajustes para elegir la carpeta raíz de tu biblioteca.",
                )
        self.pages.setCurrentWidget(
            self.grid if series_items else self.empty_state
        )

    def set_context(self, text):
        self.context_label.setText(text)
        self.context_label.setVisible(bool(text))

    def show_detail(self, series, episodes):

        self.context_label.hide()
        self.detail.show_series(series, episodes)
        self.pages.setCurrentWidget(self.detail)

    def show_catalog(self):

        self.context_label.setVisible(bool(self.context_label.text()))
        self.pages.setCurrentWidget(
            self.grid if self.grid.cards else self.empty_state
        )
