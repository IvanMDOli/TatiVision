from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QButtonGroup,
    QComboBox,
)
from PySide6.QtCore import QPointF, QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from app.ui.theme import HEADER_BUTTON_STYLESHEET
from app.ui.icon_utils import load_ui_icon

from app.ui.widgets.search_bar import (
    SearchBar
)


class CatalogSortComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._arrow_color = QColor("#c9d1d9")

    def set_theme(self, theme):
        self._arrow_color = QColor(
            "#303b35" if theme == "light" else "#c9d1d9"
        )
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(self._arrow_color, 1.8)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)
        center_x = self.width() - 13
        center_y = self.height() / 2
        painter.drawLine(
            QPointF(center_x - 3.5, center_y - 1.5),
            QPointF(center_x, center_y + 2),
        )
        painter.drawLine(
            QPointF(center_x, center_y + 2),
            QPointF(center_x + 3.5, center_y - 1.5),
        )


class HeaderWidget(QWidget):

    catalogChanged = Signal(str)

    def __init__(self):

        super().__init__()

        main_layout = QVBoxLayout()

        self.setLayout(main_layout)

        self.title = QLabel()
        self.title.setStyleSheet("font-size: 26px; font-weight: 800;")

        self.search_bar = SearchBar()

        catalog_row = QHBoxLayout()
        self.catalog_group = QButtonGroup(self)
        self.catalog_group.setExclusive(True)

        self.movies_catalog_button = QPushButton("Películas")
        self.series_catalog_button = QPushButton("Series")
        self.movies_catalog_button.setObjectName("catalogButton")
        self.series_catalog_button.setObjectName("catalogButton")

        for catalog, button in (
            ("movies", self.movies_catalog_button),
            ("series", self.series_catalog_button),
        ):
            button.setCheckable(True)
            button.setMinimumHeight(36)
            button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet(HEADER_BUTTON_STYLESHEET)
            self.catalog_group.addButton(button)
            button.clicked.connect(
                lambda _checked=False, name=catalog: self.catalogChanged.emit(name)
            )
            catalog_row.addWidget(button)

        self.movies_catalog_button.setChecked(True)
        catalog_row.addStretch()

        bottom_row = QHBoxLayout()

        self.favorites_button = QPushButton("Favoritos")
        self.favorites_button.setCheckable(True)
        self.favorites_button.setIcon(
            load_ui_icon("fav", "#b24a50")
        )
        self.favorites_button.setIconSize(QSize(15, 15))

        self.watched_filter_button = QPushButton("No vistas")
        self.watched_filter_button.setCheckable(True)
        self.watched_filter_button.setChecked(False)
        self.watched_filter_button.setIcon(
            load_ui_icon("view", "#879197")
        )
        self.watched_filter_button.setIconSize(QSize(16, 16))
        self.watched_filter_button.setToolTip(
            "Mostrar solo películas no vistas"
        )
        self.sort_combo = CatalogSortComboBox()
        self.sort_combo.setObjectName("catalogSort")
        self.sort_combo.addItem("Sin filtro", "title_asc")
        self.sort_combo.addItem("Director · A–Z", "director_asc")
        self.sort_combo.addItem("Director · Z–A", "director_desc")
        self.sort_combo.addItem("Año · antiguo primero", "year_asc")
        self.sort_combo.addItem("Año · reciente primero", "year_desc")
        self.sort_combo.addItem("Duración · menor primero", "runtime_asc")
        self.sort_combo.addItem("Duración · mayor primero", "runtime_desc")
        self.sort_combo.setFixedHeight(32)
        self.sort_combo.setMinimumWidth(190)
        self.sort_combo.setCursor(Qt.PointingHandCursor)
        self.sort_combo.setToolTip("Ordenar el catálogo de películas")
        self.favorites_button.setObjectName("filterButton")
        self.watched_filter_button.setObjectName("filterButton")

        for button in (
            self.favorites_button,
            self.watched_filter_button,
        ):
            button.setFixedHeight(32)
            button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet(HEADER_BUTTON_STYLESHEET)

        self.movie_count = QLabel(
            "Películas: 0"
        )
        self.movie_count.setStyleSheet(
            "color: #9aa5ab; font-size: 12px;"
        )

        bottom_row.addWidget(
            self.favorites_button
        )

        bottom_row.addWidget(
            self.watched_filter_button
        )

        bottom_row.addWidget(self.sort_combo)

        bottom_row.addStretch()

        bottom_row.addWidget(
            self.movie_count
        )

        main_layout.addWidget(
            self.title
        )

        main_layout.addLayout(catalog_row)

        main_layout.addWidget(
            self.search_bar
        )

        main_layout.addLayout(
            bottom_row
        )
        self.set_theme("dark")

    def set_theme(self, theme):
        tati_color = "#252d28" if theme == "light" else "#f2f4f5"
        self.title.setText(
            f'<span style="color:{tati_color}">Tati</span>'
            '<span style="color:#00e054">Vision</span>'
        )
        self.sort_combo.set_theme(theme)