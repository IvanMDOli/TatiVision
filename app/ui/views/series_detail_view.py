from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.ui.icon_utils import load_ui_icon
from app.ui.poster_utils import load_poster
from app.ui.widgets.cast_widget import CastWidget
from app.ui.widgets.detail_back_button import DetailBackButton
from app.ui.theme import apply_theme, get_current_theme
from app.vlc.player import play_movie


class SeriesDetailView(QWidget):

    backRequested = Signal()
    favoriteChanged = Signal(int, bool)
    watchedChanged = Signal(int, bool)
    episodeWatchedChanged = Signal(int, bool)
    seasonWatchedChanged = Signal(int, int, bool)
    metadataRefreshRequested = Signal(int)

    def __init__(self):
        super().__init__()
        self.series = None
        self.episodes = []
        self.episode_checks = {}
        self.season_checks = {}
        self.progress_bar = None
        self.progress_label = None

        self.setObjectName("seriesDetailView")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet("""
            QWidget#seriesDetailView {
                background-color: #101417;
                color: #f2f2f2;
            }
            QWidget#seriesDetailContent {
                background-color: #101417;
            }
            QLabel {
                background: transparent;
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
            QCheckBox {
                spacing: 6px;
                color: #d7dddf;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #536168;
                border-radius: 3px;
                background-color: #1b2227;
            }
            QCheckBox::indicator:checked {
                border-color: #00c94b;
                background-color: #087e3d;
            }
            QCheckBox::indicator:indeterminate {
                border-color: #00c94b;
                background-color: #234b35;
            }
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        back_row = QHBoxLayout()
        back_row.setContentsMargins(26, 14, 26, 0)
        back_row.setSpacing(0)
        self.back_button = DetailBackButton()
        self.back_button.setObjectName("backButton")
        self.back_button.clicked.connect(self.backRequested.emit)
        back_row.addWidget(self.back_button, alignment=Qt.AlignLeft)
        back_row.addStretch()
        layout.addLayout(back_row)

        content = QWidget()
        content.setObjectName("seriesDetailContent")
        self.content_layout = QVBoxLayout(content)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.viewport().setStyleSheet(
            "background-color: #101417;"
        )
        self.scroll_area.setWidget(content)
        self.content_layout.setContentsMargins(26, 14, 26, 30)
        self.content_layout.setSpacing(14)
        layout.addWidget(self.scroll_area)

    def show_series(self, series, episodes):
        self._clear_content()
        self.series = series
        self.episodes = episodes
        self.episode_checks = {}
        self.season_checks = {}

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
        poster.setFixedSize(260, 390)
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
        information.setSpacing(10)
        eyebrow = QLabel("FICHA DE SERIE")
        eyebrow.setStyleSheet(
            "background: transparent; color: #00e054; font-size: 11px; "
            "font-weight: 700; "
            "letter-spacing: 1px;"
        )
        information_header = QHBoxLayout()
        information_header.addWidget(eyebrow)
        information_header.addStretch()
        self.metadata_button = QPushButton()
        self.metadata_button.setIcon(load_ui_icon("edit", "#c9d1d9"))
        self.metadata_button.setIconSize(QSize(18, 18))
        self.metadata_button.setFixedSize(42, 36)
        self.metadata_button.setCursor(Qt.PointingHandCursor)
        self.metadata_button.setToolTip(
            "Volver a consultar TMDb y corregir los metadatos de esta serie"
        )
        self._style_detail_button(self.metadata_button)
        self.metadata_button.clicked.connect(self.request_metadata_refresh)
        information_header.addWidget(self.metadata_button)
        information.addLayout(information_header)

        title = QLabel(series.title or "Serie sin título")
        title.setStyleSheet(
            "background: transparent; font-size: 32px; font-weight: 700;"
        )
        title.setWordWrap(True)
        information.addWidget(title)

        metadata_parts = []
        if series.year:
            metadata_parts.append(str(series.year))
        if series.runtime:
            metadata_parts.append(f"{series.runtime} min/episodio")
        if metadata_parts:
            metadata = QLabel("  ·  ".join(metadata_parts))
            metadata.setStyleSheet(
                "background: transparent; color: #aab4ba; font-size: 14px;"
            )
            information.addWidget(metadata)

        genres = QLabel(series.genre or "Género desconocido")
        genres.setStyleSheet(
            "background: transparent; color: #00c94b; font-size: 13px;"
        )
        genres.setWordWrap(True)
        information.addWidget(genres)

        if series.director:
            creator = QLabel(f"Creada por  ·  {series.director}")
            creator.setWordWrap(True)
            creator.setStyleSheet(
                "background: transparent; color: #d1d7da; font-size: 14px;"
            )
            information.addWidget(creator)

        overview_heading = QLabel("SINOPSIS")
        overview_heading.setStyleSheet(
            "background: transparent; color: #89949b; font-size: 11px; "
            "font-weight: 700; "
            "letter-spacing: 1px;"
        )
        information.addWidget(overview_heading)

        overview = QLabel(series.overview or "Sin sinopsis disponible.")
        overview.setWordWrap(True)
        overview.setStyleSheet(
            "background: transparent; color: #d5dbde; font-size: 14px;"
        )
        information.addWidget(overview)

        cast_heading = QLabel("REPARTO")
        cast_heading.setStyleSheet(
            "background: transparent; color: #89949b; font-size: 11px; "
            "font-weight: 700; "
            "letter-spacing: 1px;"
        )
        information.addWidget(cast_heading)
        information.addWidget(CastWidget(series.cast_members))

        actions = QHBoxLayout()
        actions.setSpacing(8)
        self.favorite_button = QPushButton()
        self.favorite_button.setIconSize(QSize(18, 18))
        self.favorite_button.setCursor(Qt.PointingHandCursor)
        self._style_detail_button(self.favorite_button)
        self.favorite_button.clicked.connect(self.toggle_favorite)
        actions.addWidget(self.favorite_button)

        self.watched_button = QPushButton()
        self.watched_button.setIconSize(QSize(18, 18))
        self.watched_button.setCursor(Qt.PointingHandCursor)
        self._style_detail_button(self.watched_button)
        self.watched_button.clicked.connect(self.toggle_watched)
        actions.addWidget(self.watched_button)

        actions.addStretch()
        information.addLayout(actions)
        information.addStretch()
        header.addLayout(information, 1)
        self.content_layout.addWidget(hero)
        self.update_favorite(bool(series.favorite))
        self.update_watched(bool(series.watched))

        progress_row = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #252d32;
                border: none;
                border-radius: 4px;
            }
            QProgressBar::chunk {
                background-color: #00c94b;
                border-radius: 4px;
            }
        """)
        self.progress_label = QLabel()
        self.progress_label.setMinimumWidth(132)
        self.progress_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.progress_label.setStyleSheet(
            "background: transparent; color: #9ca7ac; font-size: 11px;"
        )
        progress_row.addWidget(self.progress_bar, 1)
        progress_row.addWidget(self.progress_label)
        self.content_layout.addLayout(progress_row)
        self._update_progress()

        episodes_heading = QLabel(f"CAPÍTULOS  ·  {len(episodes)}")
        episodes_heading.setStyleSheet(
            "background: transparent; color: #cbd2d6; font-size: 13px; "
            "font-weight: 700; "
            "letter-spacing: 1px;"
        )
        self.content_layout.addWidget(episodes_heading)

        seasons = {}
        for episode in episodes:
            seasons.setdefault(episode.season, []).append(episode)

        for season_number, season_episodes in sorted(seasons.items()):
            season_row = QHBoxLayout()
            season_check = QCheckBox()
            season_check.setTristate(True)
            season_check.setCursor(Qt.PointingHandCursor)
            watched_count = sum(bool(episode.watched) for episode in season_episodes)
            if watched_count == len(season_episodes):
                season_check.setCheckState(Qt.Checked)
            elif watched_count:
                season_check.setCheckState(Qt.PartiallyChecked)
            else:
                season_check.setCheckState(Qt.Unchecked)
            season_check.clicked.connect(
                lambda _checked=False, number=season_number, checkbox=season_check:
                self.seasonWatchedChanged.emit(
                    self.series.id,
                    number,
                    checkbox.checkState() != Qt.Unchecked,
                )
            )
            self.season_checks[season_number] = season_check
            season_row.addWidget(season_check)

            season_title = QLabel(f"Temporada {season_number}")
            season_title.setStyleSheet(
                "background: transparent; font-size: 18px; "
                "font-weight: 700; color: #f2f4f5; "
                "padding: 4px 0;"
            )
            season_row.addWidget(season_title)
            season_row.addStretch()
            self.content_layout.addLayout(season_row)

            for episode in season_episodes:
                episode_row = QHBoxLayout()
                episode_check = QCheckBox()
                episode_check.setCursor(Qt.PointingHandCursor)
                episode_check.setChecked(bool(episode.watched))
                episode_check.setToolTip(
                    "Capítulo visto" if episode.watched else "Marcar capítulo como visto"
                )
                episode_check.clicked.connect(
                    lambda watched, episode_id=episode.id:
                    self.episodeWatchedChanged.emit(episode_id, watched)
                )
                self.episode_checks[episode.id] = episode_check
                episode_row.addWidget(episode_check)

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
                    lambda _checked=False, path=episode.video_path:
                    self.play_episode(path)
                )
                episode_row.addWidget(episode_button, 1)
                self.content_layout.addLayout(episode_row)

        self.content_layout.addStretch()
        apply_theme(self, get_current_theme(), source_theme="dark")

    def update_favorite(self, is_favorite):
        if self.series is None:
            return
        self.series.favorite = bool(is_favorite)
        self.favorite_button.setIcon(
            load_ui_icon(
                "fav",
                "#ed4650" if is_favorite else "#b24a50",
                filled=is_favorite,
            )
        )
        self.favorite_button.setText(
            "  En favoritos" if is_favorite else "  Añadir a favoritos"
        )
        self.favorite_button.setToolTip(
            "Quitar de favoritos" if is_favorite else "Agregar a favoritos"
        )

    def update_watched(self, is_watched):
        if self.series is None:
            return
        self.series.watched = bool(is_watched)
        self.watched_button.setIcon(
            load_ui_icon(
                "view",
                "#00c94b" if is_watched else "#879197",
            )
        )
        self.watched_button.setText(
            "  Vista" if is_watched else "  Marcar todos como vistos"
        )

    def toggle_favorite(self):
        if self.series:
            self.favoriteChanged.emit(
                self.series.id,
                not bool(self.series.favorite),
            )

    def toggle_watched(self):
        if self.series:
            self.watchedChanged.emit(
                self.series.id,
                not bool(self.series.watched),
            )

    def request_metadata_refresh(self):
        if self.series:
            self.metadataRefreshRequested.emit(self.series.id)

    def _update_progress(self):
        total = len(self.episodes)
        watched = sum(bool(episode.watched) for episode in self.episodes)
        percent = round(watched * 100 / total) if total else 0
        self.progress_bar.setValue(percent)
        self.progress_label.setText(
            f"{watched}/{total} capítulos · {percent}%"
        )

    @staticmethod
    def _style_detail_button(button):
        button.setStyleSheet("""
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

    def _clear_content(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget:
                widget.hide()
                widget.deleteLater()
            elif child_layout:
                self._clear_layout(child_layout)
                child_layout.deleteLater()

    @staticmethod
    def _clear_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget:
                widget.hide()
                widget.deleteLater()
            elif child_layout:
                SeriesDetailView._clear_layout(child_layout)
                child_layout.deleteLater()

    def play_episode(self, video_path):
        try:
            play_movie(video_path)
        except (FileNotFoundError, OSError) as error:
            QMessageBox.critical(
                self,
                "No se pudo reproducir el capítulo",
                str(error),
            )
