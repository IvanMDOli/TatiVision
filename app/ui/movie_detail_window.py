from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.services.movie_service import (
    toggle_favorite,
    toggle_watched,
)
from app.ui.poster_utils import load_poster
from app.ui.icon_utils import load_ui_icon
from app.vlc.player import play_movie


class MovieDetailWindow(QWidget):

    backRequested = Signal()
    favoriteChanged = Signal(int, bool)
    watchedChanged = Signal(int, bool)
    metadataRefreshRequested = Signal(int)

    def __init__(self, parent=None):

        super().__init__(parent)
        self.movie = None
        self.setObjectName("movieDetailView")
        self.setStyleSheet("""
            QWidget#movieDetailView {
                background-color: #14181c;
                color: #f2f2f2;
            }
            QLabel {
                color: #f2f2f2;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QPushButton {
                color: #f2f2f2;
                background-color: #20272c;
                border: 1px solid #39434a;
                border-radius: 6px;
                padding: 8px 14px;
            }
            QPushButton:hover {
                background-color: #2c373e;
                border-color: #00e054;
            }
        """)

        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        outer_layout.setSpacing(0)

        self.back_button = QPushButton("←  Volver al catálogo")
        self.back_button.setObjectName("backButton")
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.setStyleSheet("""
            QPushButton#backButton {
                text-align: left;
                background: transparent;
                border: none;
                padding: 12px 18px;
                color: #c9d1d9;
                font-size: 14px;
            }
            QPushButton#backButton:hover {
                color: #00e054;
            }
        """)
        self.back_button.clicked.connect(self.backRequested.emit)
        outer_layout.addWidget(self.back_button, alignment=Qt.AlignLeft)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setContentsMargins(26, 14, 26, 30)
        self.content_layout.setSpacing(20)
        self.scroll_area.setWidget(content)
        outer_layout.addWidget(self.scroll_area)

    def show_movie(self, movie):

        self.movie = movie
        self._clear_content()

        hero = QFrame()
        hero.setObjectName("movieHero")
        hero.setStyleSheet("""
            QFrame#movieHero {
                background-color: #1b2227;
                border: 1px solid #2e383e;
                border-radius: 12px;
            }
        """)
        hero_layout = QHBoxLayout(hero)
        hero_layout.setContentsMargins(22, 22, 22, 22)
        hero_layout.setSpacing(26)

        poster = QLabel()
        poster.setObjectName("detailPoster")
        poster.setFixedSize(260, 390)
        poster.setAlignment(Qt.AlignCenter)
        poster.setStyleSheet("""
            QLabel#detailPoster {
                background-color: #0e1113;
                border: 1px solid #343d42;
                border-radius: 8px;
                color: #929a9e;
            }
        """)

        pixmap = load_poster(movie.poster_path, movie.title)
        if not pixmap.isNull():
            poster.setPixmap(
                pixmap.scaled(
                    poster.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        else:
            poster.setText("Sin póster")

        hero_layout.addWidget(poster, alignment=Qt.AlignTop)

        details = QVBoxLayout()
        details.setSpacing(12)

        eyebrow = QLabel("FICHA DE PELÍCULA")
        eyebrow.setStyleSheet(
            "color: #00e054; font-size: 11px; font-weight: 700; letter-spacing: 1px;"
        )
        details.addWidget(eyebrow)

        title = QLabel(movie.title or "Película sin título")
        title.setWordWrap(True)
        title.setStyleSheet("font-size: 32px; font-weight: 700;")
        details.addWidget(title)

        metadata_parts = []
        if movie.year:
            metadata_parts.append(str(movie.year))
        if movie.runtime:
            metadata_parts.append(f"{movie.runtime} min")
        metadata = QLabel("  ·  ".join(metadata_parts) or "Datos no disponibles")
        metadata.setStyleSheet("color: #aab4ba; font-size: 14px;")
        details.addWidget(metadata)

        genre = QLabel(movie.genre or "Género no disponible")
        genre.setWordWrap(True)
        genre.setStyleSheet("color: #00e054; font-size: 13px;")
        details.addWidget(genre)

        director = QLabel(
            f"Dirección  ·  {movie.director or 'No disponible'}"
        )
        director.setWordWrap(True)
        director.setStyleSheet("color: #d1d7da; font-size: 14px;")
        details.addWidget(director)

        overview_heading = QLabel("SINOPSIS")
        overview_heading.setStyleSheet(
            "color: #89949b; font-size: 11px; font-weight: 700; letter-spacing: 1px;"
        )
        details.addWidget(overview_heading)

        overview = QLabel(
            movie.overview or "No hay una sinopsis disponible para esta película."
        )
        overview.setWordWrap(True)
        overview.setStyleSheet(
            "color: #d5dbde; font-size: 14px; line-height: 1.4;"
        )
        details.addWidget(overview)
        details.addStretch()

        actions = QHBoxLayout()
        actions.setSpacing(10)

        self.play_button = QPushButton("Reproducir")
        self.play_button.setIcon(load_ui_icon("play", "#101712"))
        self.play_button.setIconSize(QSize(16, 16))
        self.play_button.setObjectName("playButton")
        self.play_button.setCursor(Qt.PointingHandCursor)
        self.play_button.setStyleSheet("""
            QPushButton#playButton {
                background-color: #00e054;
                color: #101712;
                border: none;
                font-weight: 700;
            }
            QPushButton#playButton:hover {
                background-color: #20f06b;
            }
        """)
        self.play_button.clicked.connect(self.play_movie)
        actions.addWidget(self.play_button)

        self.metadata_button = QPushButton()
        self.metadata_button.setObjectName("metadataButton")
        self.metadata_button.setIcon(load_ui_icon("edit", "#c9d1d9"))
        self.metadata_button.setIconSize(QSize(18, 18))
        self.metadata_button.setCursor(Qt.PointingHandCursor)
        self.metadata_button.setFixedSize(42, 36)
        self.metadata_button.setToolTip(
            "Volver a consultar TMDb y corregir los metadatos de esta película"
        )
        self.metadata_button.clicked.connect(self.request_metadata_refresh)
        actions.addWidget(self.metadata_button)

        self.favorite_button = QPushButton()
        self.favorite_button.setIconSize(QSize(18, 18))
        self.favorite_button.setCursor(Qt.PointingHandCursor)
        self.favorite_button.clicked.connect(self.toggle_movie_favorite)
        actions.addWidget(self.favorite_button)

        self.watched_button = QPushButton()
        self.watched_button.setIconSize(QSize(18, 18))
        self.watched_button.setCursor(Qt.PointingHandCursor)
        self.watched_button.clicked.connect(self.toggle_movie_watched)
        actions.addWidget(self.watched_button)

        details.addLayout(actions)
        hero_layout.addLayout(details, 1)
        self.content_layout.addWidget(hero)

        self.update_favorite_button()
        self.update_watched_button()

    def _clear_content(self):

        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget:
                widget.deleteLater()
            elif child_layout:
                self._clear_layout(child_layout)

    @staticmethod
    def _clear_layout(layout):

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget:
                widget.deleteLater()
            elif child_layout:
                MovieDetailWindow._clear_layout(child_layout)

    def play_movie(self):

        if not self.movie or not self.movie.video_path:
            QMessageBox.warning(
                self,
                "Archivo no disponible",
                "Esta película no tiene una ruta de video asociada.",
            )
            return

        try:
            play_movie(self.movie.video_path)
        except (FileNotFoundError, OSError) as error:
            QMessageBox.critical(
                self,
                "No se pudo reproducir la película",
                str(error),
            )

    def request_metadata_refresh(self):
        if self.movie:
            self.metadataRefreshRequested.emit(self.movie.id)

    def update_favorite_button(self):

        if not self.movie:
            return

        is_favorite = bool(self.movie.favorite)
        self.favorite_button.setText(
            "  En favoritos" if is_favorite else "  Añadir a favoritos"
        )
        self.favorite_button.setIcon(
            load_ui_icon(
                "fav",
                "#ed4650" if is_favorite else "#b24a50",
                filled=is_favorite,
            )
        )
        self.favorite_button.setToolTip(
            "Quitar de favoritos"
            if is_favorite
            else "Agregar a favoritos"
        )

    def update_watched_button(self):

        if not self.movie:
            return

        is_watched = bool(self.movie.watched)
        self.watched_button.setText(
            "  Vista" if is_watched else "  Marcar como vista"
        )
        self.watched_button.setIcon(
            load_ui_icon(
                "view",
                "#00c94b" if is_watched else "#879197",
            )
        )

    def toggle_movie_favorite(self):

        self.movie.favorite = toggle_favorite(self.movie.id)
        self.update_favorite_button()
        self.favoriteChanged.emit(
            self.movie.id,
            bool(self.movie.favorite),
        )

    def toggle_movie_watched(self):

        self.movie.watched = toggle_watched(self.movie.id)
        self.update_watched_button()
        self.watchedChanged.emit(
            self.movie.id,
            bool(self.movie.watched),
        )
