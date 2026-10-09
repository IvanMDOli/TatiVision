from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import Signal

from app.ui.widgets.movie_grid import (
    MovieGrid
)


class FilteredView(QWidget):

    favoriteChanged = Signal(int, bool)
    watchedChanged = Signal(int, bool)
    renderFinished = Signal()

    def __init__(self):

        super().__init__()

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.setLayout(layout)
        self.movie_grid = MovieGrid()

        self.movie_grid.favoriteChanged.connect(
            self.favoriteChanged.emit
        )
        self.movie_grid.watchedChanged.connect(
            self.watchedChanged.emit
        )
        self.movie_grid.renderFinished.connect(
            self.renderFinished.emit
        )

        layout.addWidget(
            self.movie_grid
        )

    def render_movies(
        self,
        movies,
        click_handler
    ):

        self.movie_grid.render_movies(
            movies,
            click_handler
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