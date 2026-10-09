from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.ui.poster_utils import load_poster


class SeriesCard(QWidget):

    WIDTH = 220
    HEIGHT = 384

    clicked = Signal(int)

    def __init__(self, series):

        super().__init__()
        self.series_id = series.id

        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)

        eyebrow = QLabel("SERIE")
        eyebrow.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        eyebrow.setFixedHeight(18)
        eyebrow.setStyleSheet(
            "color: #00c94b; font-size: 10px; font-weight: 700; "
            "letter-spacing: 1px;"
        )
        layout.addWidget(eyebrow)

        poster = QLabel()
        poster.setAlignment(Qt.AlignCenter)
        poster.setFixedSize(198, 270)
        pixmap = load_poster(series.poster_path, series.title)
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
        poster.setStyleSheet(
            "background-color: #0e1113; border: 1px solid #303a3f; "
            "border-radius: 8px; color: #929a9e;"
        )
        layout.addWidget(poster, alignment=Qt.AlignHCenter)

        title = QLabel(series.title or "Serie sin título")
        title.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title.setWordWrap(True)
        title.setFixedHeight(34)
        title.setToolTip(series.title or "Serie sin título")
        title.setStyleSheet(
            "font-size: 14px; font-weight: 700; color: #f2f4f5;"
        )
        layout.addWidget(title)

        genres = QLabel(series.genre or "Género desconocido")
        genres.setAlignment(Qt.AlignLeft | Qt.AlignTop)
        genres.setWordWrap(True)
        genres.setFixedHeight(24)
        genres.setStyleSheet("color: #9ca7ac; font-size: 10px;")
        layout.addWidget(genres)

        for label in (eyebrow, poster, title, genres):
            label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.setFixedSize(self.WIDTH, self.HEIGHT)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet("""
            SeriesCard {
                background-color: #191f23;
                border: 1px solid #293238;
                border-radius: 9px;
            }
            SeriesCard:hover {
                background-color: #20272c;
                border: 1px solid #00a847;
            }
        """)

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            self.clicked.emit(self.series_id)

        super().mousePressEvent(event)
