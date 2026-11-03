from app.ui.widgets.movie_card import MovieCard


class SeriesCard(MovieCard):
    def __init__(self, series):
        self.series_id = series.id
        super().__init__(series)

    def update_watched(self, is_watched):
        super().update_watched(is_watched)
        self.watched_button.setToolTip(
            "Marcar serie como no vista"
            if self._watched
            else "Marcar todos los capítulos como vistos"
        )

    def toggle_favorite(self):
        self.favoriteChanged.emit(
            self.series_id,
            not self._favorite,
        )

    def toggle_watched(self):
        self.watchedChanged.emit(
            self.series_id,
            not self._watched,
        )
