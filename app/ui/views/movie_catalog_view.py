from PySide6.QtWidgets import QStackedWidget, QVBoxLayout, QWidget
from PySide6.QtCore import Signal

from app.ui.views.empty_state_view import EmptyStateView
from app.ui.widgets.movie_grid import (
    MovieGrid
)


class MovieCatalogView(QWidget):

    favoriteChanged = Signal(int, bool)
    watchedChanged = Signal(int, bool)
    renderFinished = Signal()

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout(self)
        self.movie_grid = MovieGrid()
        self.scroll_area = self.movie_grid.scroll_area
        self.empty_state = EmptyStateView()
        self.pages = QStackedWidget()
        self.pages.addWidget(self.movie_grid)
        self.pages.addWidget(self.empty_state)

        self.movie_grid.favoriteChanged.connect(
            self.favoriteChanged.emit
        )
        self.movie_grid.watchedChanged.connect(
            self.watchedChanged.emit
        )
        self.movie_grid.renderFinished.connect(
            self.renderFinished.emit
        )

        layout.addWidget(self.pages)

    def render_movies(
        self,
        movies,
        click_handler,
        sort_order="title_asc",
        selected_genre=None,
        group_by_genre=True,
        root_path=None,
        catalog_has_movies=False,
    ):
        self.movie_grid.render_movies(
            movies,
            click_handler,
            sort_order,
            selected_genre,
            group_by_genre,
        )
        if not movies:
            if catalog_has_movies:
                self.empty_state.set_content(
                    "No hay películas que coincidan",
                    "Probá cambiar la búsqueda o quitar los filtros activos.",
                )
            elif root_path:
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
        self.pages.setCurrentWidget(
            self.movie_grid if movies else self.empty_state
        )

    def set_context(self, text):
        self.movie_grid.set_context(text)

    def retain_movies(self, movies):
        self.movie_grid.retain_movies(movies)

    def cancel_render(self):
        self.movie_grid.cancel_render()

    def update_movie_favorite(self, movie_id, is_favorite):

        self.movie_grid.update_movie_favorite(
            movie_id,
            is_favorite,
        )

    def update_movie_watched(self, movie_id, is_watched):

        self.movie_grid.update_movie_watched(
            movie_id,
            is_watched,
        )