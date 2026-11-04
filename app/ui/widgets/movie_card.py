from PySide6.QtCore import QEasingCurve, QSize, Qt, QVariantAnimation, Signal
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.services.movie_service import (
    toggle_favorite as toggle_movie_favorite,
    toggle_watched as toggle_movie_watched,
)
from app.ui.icon_utils import load_ui_icon
from app.ui.poster_utils import load_scaled_poster
from app.ui.theme import apply_theme, get_current_theme


def _scaled(value, scale):
    return max(1, round(value * scale))


def _interpolate_color(start, end, progress):
    return QColor.fromRgbF(
        start.redF() + (end.redF() - start.redF()) * progress,
        start.greenF() + (end.greenF() - start.greenF()) * progress,
        start.blueF() + (end.blueF() - start.blueF()) * progress,
        start.alphaF() + (end.alphaF() - start.alphaF()) * progress,
    )


class MovieCard(QWidget):
    CARD_SCALE = 1.13
    BASE_CARD_WIDTH = 189
    BASE_CARD_HEIGHT = 374
    BASE_POSTER_WIDTH = 185
    BASE_POSTER_HEIGHT = 284
    CARD_WIDTH = round(BASE_CARD_WIDTH * CARD_SCALE)
    CARD_HEIGHT = round(BASE_CARD_HEIGHT * CARD_SCALE)
    POSTER_WIDTH = CARD_WIDTH - 4
    POSTER_HEIGHT = round(
        POSTER_WIDTH * BASE_POSTER_HEIGHT / BASE_POSTER_WIDTH
    )
    CARD_RADIUS = _scaled(6, CARD_SCALE)

    clicked = Signal(int)
    favoriteChanged = Signal(int, bool)
    watchedChanged = Signal(int, bool)

    def __init__(self, movie):
        super().__init__()
        self.movie_id = movie.id
        self._favorite = bool(movie.favorite)
        self._watched = bool(movie.watched)
        self._hover_progress = 0.0
        self._border_color = QColor("#293238")
        self._background_color = QColor("#191f23")
        self._hover_animation = QVariantAnimation(self)
        self._hover_animation.setDuration(200)
        self._hover_animation.setEasingCurve(QEasingCurve.OutCubic)
        self._hover_animation.valueChanged.connect(self._set_hover_progress)
        scale = self.CARD_SCALE
        self.setObjectName("movieCard")
        self.setFixedSize(self.CARD_WIDTH, self.CARD_HEIGHT)
        self.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_Hover, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(
            _scaled(1, scale),
            _scaled(1, scale),
            _scaled(1, scale),
            _scaled(2, scale),
        )
        layout.setSpacing(0)

        status_row = QHBoxLayout()
        status_row.setContentsMargins(
            _scaled(3, scale),
            _scaled(3, scale),
            _scaled(3, scale),
            _scaled(3, scale),
        )
        status_row.setSpacing(0)
        self.watched_button = QPushButton()
        self.watched_button.setObjectName("watched")
        self.watched_button.setFixedSize(
            _scaled(25, scale),
            _scaled(25, scale),
        )
        self.watched_button.setIconSize(
            QSize(_scaled(14, scale), _scaled(14, scale))
        )
        self.watched_button.setCursor(Qt.PointingHandCursor)
        self.watched_button.clicked.connect(self.toggle_watched)
        self.update_watched(self._watched)

        self.favorite_button = QPushButton()
        self.favorite_button.setObjectName("favorite")
        self.favorite_button.setFixedSize(
            _scaled(25, scale),
            _scaled(25, scale),
        )
        self.favorite_button.setIconSize(
            QSize(_scaled(14, scale), _scaled(14, scale))
        )
        self.favorite_button.setCursor(Qt.PointingHandCursor)
        self.favorite_button.clicked.connect(self.toggle_favorite)
        self.update_favorite(self._favorite)
        status_row.addWidget(self.watched_button)
        status_row.addStretch()
        status_row.addWidget(self.favorite_button)
        layout.addLayout(status_row)

        poster = QLabel()
        poster.setObjectName("poster")
        poster.setAlignment(Qt.AlignCenter)
        poster.setFixedSize(self.POSTER_WIDTH, self.POSTER_HEIGHT)
        poster_canvas = load_scaled_poster(
            movie.poster_path,
            movie.title,
            self.POSTER_WIDTH,
            self.POSTER_HEIGHT,
        )
        if not poster_canvas.isNull():
            poster.setPixmap(poster_canvas)
        else:
            poster.setText("Sin póster")
        layout.addWidget(poster, 0, Qt.AlignHCenter)

        footer = QWidget()
        footer.setObjectName("cardFooter")
        footer_layout = QVBoxLayout(footer)
        footer_layout.setContentsMargins(
            _scaled(8, scale),
            _scaled(3, scale),
            _scaled(8, scale),
            _scaled(2, scale),
        )
        footer_layout.setSpacing(0)
        title = QLabel(movie.title or "Sin título")
        title.setObjectName("title")
        title.setFixedHeight(_scaled(20, scale))
        title.setToolTip(movie.title or "Sin título")
        title.setTextInteractionFlags(Qt.NoTextInteraction)
        year = QLabel(str(movie.year or ""))
        year.setObjectName("year")
        year.setFixedHeight(_scaled(15, scale))
        director = QLabel(movie.director or "Desconocido")
        director.setObjectName("director")
        director.setFixedHeight(_scaled(15, scale))
        director.setToolTip(movie.director or "Desconocido")
        footer_layout.addWidget(title)
        footer_layout.addWidget(year)
        footer_layout.addWidget(director)
        layout.addWidget(footer, 1)

        for label in (poster, footer, title, year, director):
            label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.setStyleSheet(f"""
            QWidget#movieCard {{
                background-color: #191f23;
                border: 1px solid #293238;
                border-radius: {_scaled(6, scale)}px;
            }}
            QWidget#movieCard QWidget#cardFooter {{
                background: transparent;
                border: none;
            }}
            QWidget#movieCard QLabel {{
                background: transparent;
                border: none;
                color: #f2f2f2;
            }}
            QWidget#movieCard QLabel#title {{
                font-weight: 700;
                font-size: {_scaled(13, scale)}px;
            }}
            QWidget#movieCard QLabel#year {{
                color: #00c94b;
                font-size: {_scaled(11, scale)}px;
                font-weight: 600;
            }}
            QWidget#movieCard QLabel#director {{
                color: #9ca7ac;
                font-size: {_scaled(10, scale)}px;
            }}
            QWidget#movieCard QPushButton#favorite,
            QWidget#movieCard QPushButton#watched {{
                padding: 0;
                border: none;
                background: transparent;
            }}
            QWidget#movieCard QPushButton#favorite:hover,
            QWidget#movieCard QPushButton#watched:hover {{
                background-color: #252f34;
                border-radius: {_scaled(12, scale)}px;
            }}
            QWidget#movieCard QLabel#poster {{
                background-color: #0e1113;
                border: none;
                border-radius: {_scaled(2, scale)}px;
                color: #929a9e;
            }}
        """)
        apply_theme(self, get_current_theme(), source_theme="dark")

    def apply_color_theme(self, theme):
        if theme == "light":
            self._border_color = QColor("#cbd4cf")
            self._background_color = QColor("#f8f9f8")
        else:
            self._border_color = QColor("#293238")
            self._background_color = QColor("#191f23")
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
        self.watched_button.setToolTip(
            "Marcar como no vista"
            if self._watched
            else "Marcar como vista"
        )

    def toggle_favorite(self):
        self.update_favorite(toggle_movie_favorite(self.movie_id))
        self.favoriteChanged.emit(self.movie_id, self._favorite)

    def toggle_watched(self):
        self.update_watched(toggle_movie_watched(self.movie_id))
        self.watchedChanged.emit(self.movie_id, self._watched)

    def paintEvent(self, event):
        super().paintEvent(event)
        is_light = get_current_theme() == "light"
        hover_background = QColor(
            "#e3e8e5" if is_light else "#20272c"
        )
        hover_border = QColor("#00a847")
        progress = self._hover_progress
        background_color = _interpolate_color(
            self._background_color,
            hover_background,
            progress,
        )
        border_color = _interpolate_color(
            self._border_color,
            hover_border,
            progress,
        )

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(background_color)
        painter.drawRoundedRect(
            self.rect(),
            self.CARD_RADIUS,
            self.CARD_RADIUS,
        )
        painter.setPen(QPen(border_color, 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(
            self.rect(),
            self.CARD_RADIUS,
            self.CARD_RADIUS,
        )

    def _set_hover_progress(self, progress):
        self._hover_progress = float(progress)
        self.update()

    def _animate_hover(self, hovered):
        self._hover_animation.stop()
        self._hover_animation.setStartValue(self._hover_progress)
        self._hover_animation.setEndValue(1.0 if hovered else 0.0)
        self._hover_animation.start()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.movie_id)
        super().mousePressEvent(event)

    def enterEvent(self, event):
        self._animate_hover(True)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._animate_hover(False)
        super().leaveEvent(event)
