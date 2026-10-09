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

from app.vlc.player import play_movie
from app.ui.poster_utils import load_poster
from app.ui.icon_utils import load_ui_icon


class SeriesDetailView(QWidget):

    backRequested = Signal()

    def __init__(self):

        super().__init__()
        self.episodes = []

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.back_button = QPushButton("← Volver al catálogo")
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.setStyleSheet("""
            QPushButton {
                text-align: left;
                background: transparent;
                border: none;
                padding: 12px 18px;
                color: #c9d1d9;
                font-size: 14px;
            }
            QPushButton:hover {
                color: #00e054;
            }
        """)
        self.back_button.clicked.connect(self.backRequested.emit)
        layout.addWidget(self.back_button, alignment=Qt.AlignLeft)

        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setWidget(content)
        self.content_layout.setContentsMargins(26, 14, 26, 30)
        self.content_layout.setSpacing(20)
        layout.addWidget(self.scroll_area)

    def show_series(self, series, episodes):

        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.episodes = episodes

        hero = QFrame()
        hero.setObjectName("seriesHero")
        hero.setStyleSheet("""
            QFrame#seriesHero {
                background-color: #1b2227;
                border: 1px solid #2e383e;
                border-radius: 12px;
            }
        """)
        header = QHBoxLayout(hero)
        header.setContentsMargins(22, 22, 22, 22)
        header.setSpacing(26)

        poster = QLabel()
        poster.setFixedSize(240, 340)
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
        poster.setAlignment(Qt.AlignCenter)
        poster.setStyleSheet(
            "background-color: #0e1113; border: 1px solid #343d42; "
            "border-radius: 8px; color: #929a9e;"
        )
        header.addWidget(poster, alignment=Qt.AlignTop)

        information = QVBoxLayout()
        information.setSpacing(12)
        eyebrow = QLabel("FICHA DE SERIE")
        eyebrow.setStyleSheet(
            "color: #00e054; font-size: 11px; font-weight: 700; "
            "letter-spacing: 1px;"
        )
        information.addWidget(eyebrow)

        title = QLabel(series.title or "Serie sin título")
        title.setStyleSheet("font-size: 32px; font-weight: 700;")
        title.setWordWrap(True)
        information.addWidget(title)

        genres = QLabel(series.genre or "Género desconocido")
        genres.setStyleSheet("color: #00c94b; font-size: 13px;")
        genres.setWordWrap(True)
        information.addWidget(genres)

        overview_heading = QLabel("SINOPSIS")
        overview_heading.setStyleSheet(
            "color: #89949b; font-size: 11px; font-weight: 700; "
            "letter-spacing: 1px;"
        )
        information.addWidget(overview_heading)

        overview = QLabel(series.overview or "Sin sinopsis disponible.")
        overview.setWordWrap(True)
        overview.setStyleSheet("color: #d5dbde; font-size: 14px;")
        information.addWidget(overview)
        information.addStretch()
        header.addLayout(information, 1)
        self.content_layout.addWidget(hero)

        episodes_heading = QLabel(f"CAPÍTULOS  ·  {len(episodes)}")
        episodes_heading.setStyleSheet(
            "color: #cbd2d6; font-size: 13px; font-weight: 700; "
            "letter-spacing: 1px;"
        )
        self.content_layout.addWidget(episodes_heading)

        seasons = {}
        for episode in episodes:
            seasons.setdefault(episode.season, []).append(episode)

        for season_number, season_episodes in sorted(seasons.items()):
            season_title = QLabel(f"Temporada {season_number}")
            season_title.setStyleSheet(
                "font-size: 18px; font-weight: 700; color: #f2f4f5; "
                "padding: 4px 0;"
            )
            self.content_layout.addWidget(season_title)

            for episode in season_episodes:
                episode_button = QPushButton(
                    f"S{episode.season:02}E{episode.episode:02}  "
                    f"{episode.title or 'Episodio sin título'}"
                )
                episode_button.setIcon(load_ui_icon("play", "#c9d1d9"))
                episode_button.setIconSize(QSize(14, 14))
                episode_button.setMinimumHeight(38)
                episode_button.setCursor(Qt.PointingHandCursor)
                episode_button.setStyleSheet("""
                    QPushButton {
                        text-align: left;
                        padding: 9px 12px;
                        border: 1px solid #303b41;
                        border-radius: 6px;
                        background-color: #1b2227;
                        color: #d7dddf;
                    }
                    QPushButton:hover {
                        background-color: #252f34;
                        border-color: #00e054;
                        color: #ffffff;
                    }
                """)
                episode_button.clicked.connect(
                    lambda _checked=False, path=episode.video_path: self.play_episode(path)
                )
                self.content_layout.addWidget(episode_button)

        self.content_layout.addStretch()

    def play_episode(self, video_path):

        try:
            play_movie(video_path)
        except (FileNotFoundError, OSError) as error:
            QMessageBox.critical(
                self,
                "No se pudo reproducir el capítulo",
                str(error),
            )
