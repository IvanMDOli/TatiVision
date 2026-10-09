from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QScrollArea,
    QFrame,
    QStackedWidget,
)
from PySide6.QtCore import Signal

from app.services.movie_service import (
    get_movies_grouped_by_genre
)

from app.ui.widgets.movie_row import (
    MovieRow
)
from app.ui.views.empty_state_view import EmptyStateView


class HomeView(QWidget):

    favoriteChanged = Signal(int, bool)
    watchedChanged = Signal(int, bool)

    def __init__(
        self,
        click_handler
    ):

        super().__init__()
        self.setStyleSheet(
            "HomeView { background-color: #101417; }"
        )

        main_layout = QVBoxLayout()

        self.setLayout(
            main_layout
        )
        self.click_handler = click_handler
        self.rows = []

        self.pages = QStackedWidget()
        self.empty_state = EmptyStateView()

        scroll = QScrollArea()
        scroll.setObjectName("homeScroll")
        scroll.setWidgetResizable(
            True
        )

        container = QWidget()
        container.setObjectName("homeContent")

        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(18, 14, 18, 20)
        self.content_layout.setSpacing(8)

        container.setLayout(
            self.content_layout
        )

        scroll.setWidget(
            container
        )

        self.pages.addWidget(scroll)
        self.pages.addWidget(self.empty_state)
        main_layout.addWidget(self.pages)

    def reload(self, movies, root_path):

        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.rows = []

        grouped = get_movies_grouped_by_genre(movies)
        if not grouped:
            if root_path:
                self.empty_state.set_content(
                    "No se encontraron películas",
                    "La carpeta de películas seleccionada no contiene videos "
                    "reconocidos. Elegí otra carpeta desde Ajustes o analizá "
                    "nuevamente la biblioteca.",
                )
            else:
                self.empty_state.set_content(
                    "No se seleccionó una carpeta de películas",
                    "Abrí Ajustes para elegir la carpeta raíz de tu biblioteca.",
                )
            self.pages.setCurrentWidget(self.empty_state)
            return

        for index, (genre, movies) in enumerate(sorted(grouped.items())):
            if index:
                separator = QFrame()
                separator.setFrameShape(QFrame.HLine)
                separator.setObjectName("genreSeparator")
                separator.setFixedHeight(1)
                separator.setStyleSheet(
                    "background-color: #252d32; border: none;"
                )
                self.content_layout.addWidget(separator)

            row = MovieRow(
                genre,
                movies,
                self.click_handler
            )

            self.content_layout.addWidget(
                row
            )
            self.rows.append(row)
            row.favoriteChanged.connect(
                self.favoriteChanged.emit
            )
            row.watchedChanged.connect(
                self.watchedChanged.emit
            )

        self.content_layout.addStretch()
        self.pages.setCurrentIndex(0)

    def update_movie_favorite(self, movie_id, is_favorite):

        for row in self.rows:
            row.update_movie_favorite(
                movie_id,
                is_favorite,
            )

    def update_movie_watched(self, movie_id, is_watched):

        for row in self.rows:
            row.update_movie_watched(
                movie_id,
                is_watched,
            )