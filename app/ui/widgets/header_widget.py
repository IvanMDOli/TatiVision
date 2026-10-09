from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QButtonGroup,
)
from PySide6.QtCore import QSize, Qt, Signal
from app.ui.theme import HEADER_BUTTON_STYLESHEET
from app.ui.icon_utils import load_ui_icon

from app.ui.widgets.search_bar import (
    SearchBar
)


class HeaderWidget(QWidget):

    catalogChanged = Signal(str)

    def __init__(self):

        super().__init__()

        main_layout = QVBoxLayout()

        self.setLayout(main_layout)

        title = QLabel(
            '<span style="color:#f2f4f5">Tati</span>'
            '<span style="color:#00e054">Vision</span>'
        )
        title.setStyleSheet("font-size: 26px; font-weight: 800;")

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
        self.favorites_button.setObjectName("filterButton")
        self.watched_filter_button.setObjectName("filterButton")

        for button in (
            self.favorites_button,
            self.watched_filter_button,
        ):
            button.setMinimumHeight(32)
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

        bottom_row.addStretch()

        bottom_row.addWidget(
            self.movie_count
        )

        main_layout.addWidget(
            title
        )

        main_layout.addLayout(catalog_row)

        main_layout.addWidget(
            self.search_bar
        )

        main_layout.addLayout(
            bottom_row
        )