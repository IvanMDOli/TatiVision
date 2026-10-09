from PySide6.QtCore import Property, QPropertyAnimation, QSize, Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QLabel,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)

from app.services.movie_service import (
    toggle_favorite as toggle_movie_favorite,
    toggle_watched as toggle_movie_watched,
)
from app.ui.icon_utils import load_ui_icon
from app.ui.poster_utils import load_scaled_poster


class MovieCard(QWidget):

    CARD_WIDTH = 220
    CARD_HEIGHT = 384
    POSTER_WIDTH = 198
    POSTER_HEIGHT = 270

    clicked = Signal(int)
    favoriteChanged = Signal(int, bool)
    watchedChanged = Signal(int, bool)
    borderColor = Property(
        QColor,
        lambda self: self._border_color,
        lambda self, color: self._set_border_color(color),
    )
    backgroundColor = Property(
        QColor,
        lambda self: self._background_color,
        lambda self, color: self._set_background_color(color),
    )

    def __init__(self, movie):

        super().__init__()

        self.movie_id = movie.id
        self._favorite = bool(movie.favorite)
        self._watched = bool(movie.watched)
        self._border_color = QColor("#293238")
        self._background_color = QColor("#191f23")

        layout = QVBoxLayout()
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(1)
        self.setLayout(layout)

        status_row = QHBoxLayout()
        status_row.setContentsMargins(0, 0, 0, 0)
        status_row.setSpacing(0)

        self.watched_button = QPushButton()
        self.watched_button.setObjectName("watched")
        self.watched_button.setFixedSize(26, 22)
        self.watched_button.setIconSize(QSize(15, 15))
        self.watched_button.setCursor(Qt.PointingHandCursor)
        self.watched_button.setToolTip("Marcar como vista")
        self.watched_button.clicked.connect(
            self.toggle_watched
        )
        self.update_watched(self._watched)

        self.favorite_button = QPushButton()
        self.favorite_button.setObjectName("favorite")
        self.favorite_button.setFixedSize(26, 22)
        self.favorite_button.setIconSize(QSize(15, 15))
        self.favorite_button.setCursor(Qt.PointingHandCursor)
        self.favorite_button.setToolTip("Añadir a favoritos")
        self.favorite_button.clicked.connect(
            self.toggle_favorite
        )
        self.update_favorite(self._favorite)

        status_row.addWidget(self.watched_button)
        status_row.addStretch()
        status_row.addWidget(self.favorite_button)
        layout.addLayout(status_row)

        poster = QLabel()
        poster_canvas = load_scaled_poster(
            movie.poster_path,
            movie.title,
            self.POSTER_WIDTH,
            self.POSTER_HEIGHT,
        )

        if not poster_canvas.isNull():
            poster.setPixmap(poster_canvas)
        else:
            poster.setText("Sin poster")

        poster.setObjectName("poster")
        poster.setAlignment(Qt.AlignCenter)
        poster.setFixedSize(
            self.POSTER_WIDTH,
            self.POSTER_HEIGHT,
        )
        layout.addWidget(poster, alignment=Qt.AlignHCenter)

        title = QLabel(movie.title or "Sin título")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title.setWordWrap(True)
        title.setFixedHeight(34)
        title.setToolTip(movie.title or "Sin título")
        layout.addWidget(title)

        year = QLabel(str(movie.year or ""))
        year.setObjectName("year")
        year.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        year.setFixedHeight(17)
        layout.addWidget(year)

        director = QLabel(movie.director or "Desconocido")
        director.setObjectName("director")
        director.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        director.setFixedHeight(22)
        director.setToolTip(movie.director or "Desconocido")
        layout.addWidget(director)

        for label in (
            poster,
            title,
            year,
            director,
        ):
            label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.setObjectName("movieCard")
        self.setFixedSize(self.CARD_WIDTH, self.CARD_HEIGHT)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)
        self.setStyleSheet("""
            QLabel {
                background: transparent;
                border: none;
                color: #f2f2f2;
            }
            QLabel#title {
                font-weight: 700;
                font-size: 14px;
            }
            QLabel#year {
                color: #00c94b;
                font-size: 11px;
                font-weight: 600;
            }
            QLabel#director {
                color: #9ca7ac;
                font-size: 10px;
            }
            QLabel#favorite {
                color: #ffc857;
                font-size: 15px;
            }
            QPushButton#favorite,
            QPushButton#watched {
                padding: 0;
                border: none;
                background: transparent;
                font-size: 17px;
            }
            QPushButton#favorite {
                color: #ffc857;
            }
            QPushButton#watched {
                color: #00c94b;
            }
            QPushButton#favorite:hover,
            QPushButton#watched:hover {
                background-color: #252f34;
                border-radius: 10px;
            }
            QLabel#poster {
                background-color: #0e1113;
                border: 1px solid #303a3f;
                border-radius: 8px;
                color: #929a9e;
            }
        """)

        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(12)
        self.shadow.setOffset(0, 2)
        self.shadow.setColor(QColor(0, 0, 0, 150))
        self.setGraphicsEffect(self.shadow)

        self.shadow_animation = QPropertyAnimation(
            self.shadow,
            b"blurRadius",
            self,
        )
        self.shadow_animation.setDuration(180)

        self.border_animation = QPropertyAnimation(
            self,
            b"borderColor",
            self,
        )
        self.border_animation.setDuration(180)

        self.background_animation = QPropertyAnimation(
            self,
            b"backgroundColor",
            self,
        )
        self.background_animation.setDuration(180)

    def _set_border_color(self, color):

        self._border_color = color
        self.update()

    def _set_background_color(self, color):

        self._background_color = color
        self.update()

    def update_favorite(self, is_favorite):

        self._favorite = bool(is_favorite)
        self.favorite_button.setIcon(
            load_ui_icon(
                "fav",
                "#ed4650" if self._favorite else "#b24a50",
                filled=self._favorite,
            )
        )
        self.favorite_button.setText("")
        self.favorite_button.setToolTip(
            "Quitar de favoritos"
            if self._favorite
            else "Añadir a favoritos"
        )

    def update_watched(self, is_watched):

        self._watched = bool(is_watched)
        self.watched_button.setIcon(
            load_ui_icon(
                "view",
                "#00c94b" if self._watched else "#879197",
            )
        )
        self.watched_button.setText("")
        self.watched_button.setToolTip(
            "Marcar como no vista"
            if self._watched
            else "Marcar como vista"
        )

    def toggle_favorite(self):

        self.update_favorite(
            toggle_movie_favorite(self.movie_id)
        )
        self.favoriteChanged.emit(
            self.movie_id,
            self._favorite,
        )

    def toggle_watched(self):

        self.update_watched(
            toggle_movie_watched(self.movie_id)
        )
        self.watchedChanged.emit(
            self.movie_id,
            self._watched,
        )

    def paintEvent(self, event):

        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self._background_color)
        painter.drawRoundedRect(
            self.rect().adjusted(0, 0, -1, -1),
            10,
            10,
        )
        painter.setPen(QPen(self._border_color, 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(
            self.rect().adjusted(0, 0, -1, -1),
            10,
            10,
        )

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.movie_id)

        super().mousePressEvent(event)

    def enterEvent(self, event):

        self.shadow_animation.stop()
        self.shadow_animation.setStartValue(self.shadow.blurRadius())
        self.shadow_animation.setEndValue(20)
        self.shadow_animation.start()

        self.border_animation.stop()
        self.border_animation.setStartValue(self._border_color)
        self.border_animation.setEndValue(QColor("#00a847"))
        self.border_animation.start()

        self.background_animation.stop()
        self.background_animation.setStartValue(self._background_color)
        self.background_animation.setEndValue(QColor("#242e33"))
        self.background_animation.start()

        super().enterEvent(event)

    def leaveEvent(self, event):

        self.shadow_animation.stop()
        self.shadow_animation.setStartValue(self.shadow.blurRadius())
        self.shadow_animation.setEndValue(12)
        self.shadow_animation.start()

        self.border_animation.stop()
        self.border_animation.setStartValue(self._border_color)
        self.border_animation.setEndValue(QColor("#293238"))
        self.border_animation.start()

        self.background_animation.stop()
        self.background_animation.setStartValue(self._background_color)
        self.background_animation.setEndValue(QColor("#191f23"))
        self.background_animation.start()

        super().leaveEvent(event)
