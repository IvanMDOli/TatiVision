from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QStackedWidget, QVBoxLayout, QWidget

from app.ui.views.empty_state_view import EmptyStateView
from app.ui.views.series_detail_view import SeriesDetailView
from app.ui.widgets.series_grid import SeriesGrid


class SeriesCatalogView(QWidget):

    seriesSelected = Signal(int)
    backRequested = Signal()
    favoriteChanged = Signal(int, bool)
    watchedChanged = Signal(int, bool)
    renderFinished = Signal()

    def __init__(self):

        super().__init__()

        self.setObjectName("seriesCatalogView")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            QWidget#seriesCatalogView {
                background-color: #101417;
            }
        """)
        layout = QVBoxLayout(self)
        self.pages = QStackedWidget()
        self.grid = SeriesGrid()
        self.scroll_area = self.grid.scroll_area
        self._catalog_has_series = False
        self.context_label = self.grid.context_label
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
        self.grid.favoriteChanged.connect(self.favoriteChanged.emit)
        self.grid.watchedChanged.connect(self.watchedChanged.emit)
        self.grid.renderFinished.connect(self.renderFinished.emit)
        self.detail.backRequested.connect(
            self.backRequested.emit
        )

        self.pages.addWidget(self.grid)
        self.pages.addWidget(self.detail)
        self.pages.addWidget(self.empty_state)
        layout.addWidget(self.pages)

    def render_series(
        self,
        series_items,
        root_path,
        catalog_has_series=False,
        sort_order="title_asc",
        selected_genre=None,
        group_by_genre=True,
    ):

        self._catalog_has_series = bool(series_items)
        self.grid.render_series(
            series_items,
            sort_order,
            selected_genre,
            group_by_genre,
        )
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
        self.grid.set_context(text)

    def show_detail(self, series, episodes):

        self.context_label.hide()
        self.detail.show_series(series, episodes)
        self.pages.setCurrentWidget(self.detail)

    def show_catalog(self):

        self.context_label.setVisible(bool(self.context_label.text()))
        self.pages.setCurrentWidget(
            self.grid if self._catalog_has_series else self.empty_state
        )
