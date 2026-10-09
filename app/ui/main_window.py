import os
import math
from threading import Event

from PySide6.QtCore import QPointF, QRectF, Qt, QUrl
from PySide6.QtGui import (
    QColor,
    QDesktopServices,
    QIcon,
    QPainter,
    QPainterPath,
    QPixmap,
)
from PySide6.QtWidgets import (
    QDialog,
    QMainWindow,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QStackedWidget,
    QPushButton,
    QLabel,
    QMessageBox,
    QProgressBar,
    QToolButton,
)
from PySide6.QtCore import QThread, QTimer, QSize, Signal

from app.services.movie_service import (
    delete_movies_by_ids,
    get_all_movies,
    get_all_genres,
    get_movie_by_id
)
from app.services.series_service import (
    get_all_series,
    get_all_series_genres,
    get_episodes_for_series,
    get_series_by_id,
)
from app.ui.views.library_dialog import LibraryDialog
from app.ui.widgets.library_panel import LibraryPanel

from app.ui.movie_detail_window import (
    MovieDetailWindow
)

from app.ui.widgets.header_widget import (
    HeaderWidget
)

from app.ui.views.home_view import (
    HomeView
)

from app.ui.views.filtered_view import (
    FilteredView
)
from app.ui.views.series_catalog_view import (
    SeriesCatalogView
)
from app.ui.theme import APP_STYLESHEET
from app.ui.views.metadata_candidate_dialog import MetadataCandidateDialog
from app.ui.views.settings_dialog import SettingsDialog
from app.ui.icon_utils import load_ui_icon
from config.user_settings import (
    get_active_library,
    delete_library,
    get_libraries,
    get_user_setting,
    select_library,
)


class LibraryTask(QThread):

    completed = Signal(object)
    failed = Signal(str)
    metadataReviewRequested = Signal(object)
    metadataProgress = Signal(int, int, int, str)

    def __init__(
        self,
        action,
        parent=None,
        configured_libraries=None,
        movie_id=None,
        library=None,
    ):

        super().__init__(parent)
        self.action = action
        self.movie_id = movie_id
        self.library = library or get_active_library() or {}
        self.movie_path = self.library.get(
            "movies_path",
            get_user_setting("movies_path"),
        )
        self.series_path = self.library.get(
            "series_path",
            get_user_setting("series_path"),
        )
        self.cancel_event = Event()
        self.configured_libraries = configured_libraries or {
            "movies",
            "series",
        }

    def _select_metadata_candidate(self, movie, candidates):
        decision = {
            "movie": movie,
            "candidates": candidates,
            "event": Event(),
            "selected_tmdb_id": None,
        }
        self.metadataReviewRequested.emit(decision)
        decision["event"].wait()
        return decision["selected_tmdb_id"]

    def cancel(self):
        self.cancel_event.set()

    def _report_metadata_progress(self, processed, total, updated, title):
        self.metadataProgress.emit(processed, total, updated, title)

    def run(self):

        try:
            from app.tasks.scan_library import run as scan_library
            from app.tasks.update_metadata import run as update_metadata

            if self.action == "scan":
                result = scan_library(
                    self.movie_path,
                    cancel_event=self.cancel_event,
                )
            elif self.action == "import_movies":
                root_path = self.movie_path
                scanned = scan_library(
                    root_path,
                    cancel_event=self.cancel_event,
                )
                metadata = (
                    update_metadata(
                        root_path=root_path,
                        cancel_event=self.cancel_event,
                        progress_callback=self._report_metadata_progress,
                    )
                    if not self.cancel_event.is_set()
                    else {
                        "updated": 0,
                        "not_found": 0,
                        "failed": [],
                        "skipped": 0,
                        "cancelled": True,
                    }
                )
                result = {
                    **metadata,
                    "scanned": scanned["scanned"],
                    "missing": scanned["missing"],
                    "cancelled": (
                        scanned["cancelled"]
                        or metadata["cancelled"]
                    ),
                }
            elif self.action == "scan_series":
                from app.tasks.scan_series_library import run as scan_series_library
                from app.tasks.update_series_metadata import run as update_series_metadata

                root_path = self.series_path
                scanned = scan_series_library(
                    root_path,
                    update_metadata=False,
                    cancel_event=self.cancel_event,
                )
                metadata = (
                    update_series_metadata(
                        root_path=root_path,
                        cancel_event=self.cancel_event,
                    )
                    if not self.cancel_event.is_set()
                    else {
                        "series_found": 0,
                        "episodes_found": 0,
                        "metadata_updated": 0,
                        "not_found": [],
                        "failed": [],
                        "cancelled": True,
                    }
                )
                result = {
                    **metadata,
                    "series_found": scanned["series_found"],
                    "episodes_found": scanned["episodes_found"],
                    "series_import": True,
                    "cancelled": (
                        scanned["cancelled"]
                        or metadata["cancelled"]
                    ),
                }
            elif self.action == "series_metadata":
                from app.tasks.update_series_metadata import run as update_series_metadata

                result = update_series_metadata(
                    root_path=self.series_path,
                    cancel_event=self.cancel_event,
                )
            elif self.action == "series_force":
                from app.tasks.scan_series_library import run as scan_series_library
                from app.tasks.update_series_metadata import run as update_series_metadata

                scanned = scan_series_library(
                    self.series_path,
                    update_metadata=False,
                    cancel_event=self.cancel_event,
                )
                result = (
                    update_series_metadata(
                        root_path=self.series_path,
                        force_update=True,
                        cancel_event=self.cancel_event,
                    )
                    if not self.cancel_event.is_set()
                    else {
                        "series_found": 0,
                        "episodes_found": 0,
                        "metadata_updated": 0,
                        "not_found": [],
                        "failed": [],
                        "cancelled": True,
                    }
                )
                result["scanned_series"] = scanned["series_found"]
                result["scanned_episodes"] = scanned["episodes_found"]
                result["cancelled"] = (
                    scanned["cancelled"]
                    or result["cancelled"]
                )
            elif self.action == "scan_configured":
                from app.tasks.scan_series_library import run as scan_series_library
                from app.tasks.update_series_metadata import run as update_series_metadata

                movie_path = self.movie_path
                series_path = self.series_path
                movie_result = (
                    scan_library(
                        movie_path,
                        cancel_event=self.cancel_event,
                    )
                    if movie_path and "movies" in self.configured_libraries
                    else {"scanned": 0, "missing": []}
                )
                movie_metadata = (
                    update_metadata(
                        root_path=movie_path,
                        cancel_event=self.cancel_event,
                        progress_callback=self._report_metadata_progress,
                    )
                    if (
                        movie_path
                        and "movies" in self.configured_libraries
                        and not self.cancel_event.is_set()
                    )
                    else {
                        "updated": 0,
                        "not_found": 0,
                        "failed": [],
                        "skipped": 0,
                        "cancelled": self.cancel_event.is_set(),
                    }
                )
                series_result = (
                    scan_series_library(
                        series_path,
                        update_metadata=False,
                        cancel_event=self.cancel_event,
                    )
                    if (
                        series_path
                        and "series" in self.configured_libraries
                        and not self.cancel_event.is_set()
                    )
                    else {
                        "series_found": 0,
                        "episodes_found": 0,
                        "metadata_updated": 0,
                        "not_found": [],
                        "failed": [],
                        "cancelled": self.cancel_event.is_set(),
                    }
                )
                series_metadata = (
                    update_series_metadata(
                        root_path=series_path,
                        cancel_event=self.cancel_event,
                    )
                    if (
                        series_path
                        and "series" in self.configured_libraries
                        and not self.cancel_event.is_set()
                    )
                    else {
                        "metadata_updated": 0,
                        "not_found": [],
                        "failed": [],
                        "cancelled": self.cancel_event.is_set(),
                    }
                )
                result = {
                    "configured_scan": True,
                    "scanned": movie_result["scanned"],
                    "missing": movie_result["missing"],
                    "movie_metadata": movie_metadata,
                    "series_found": series_result["series_found"],
                    "episodes_found": series_result["episodes_found"],
                    "metadata_updated": series_metadata["metadata_updated"],
                    "not_found": series_metadata["not_found"],
                    "failed": series_metadata["failed"],
                    "series_import": bool(
                        "series" in self.configured_libraries
                    ),
                    "cancelled": self.cancel_event.is_set(),
                }
            elif self.action == "metadata":
                result = update_metadata(
                    root_path=self.movie_path,
                    cancel_event=self.cancel_event,
                    progress_callback=self._report_metadata_progress,
                )
            elif self.action == "metadata_movie":
                result = update_metadata(
                    root_path=self.movie_path,
                    movie_id=self.movie_id,
                    candidate_selector=self._select_metadata_candidate,
                    progress_callback=self._report_metadata_progress,
                )
            elif self.action == "force":
                scanned = scan_library(
                    self.movie_path,
                    cancel_event=self.cancel_event,
                )
                result = (
                    update_metadata(
                        force_update=True,
                        root_path=self.movie_path,
                        cancel_event=self.cancel_event,
                        progress_callback=self._report_metadata_progress,
                    )
                    if not self.cancel_event.is_set()
                    else {
                        "updated": 0,
                        "not_found": 0,
                        "failed": [],
                        "skipped": 0,
                        "cancelled": True,
                    }
                )
                result["scanned"] = scanned["scanned"]
                result["missing"] = scanned["missing"]
                result["cancelled"] = (
                    result["cancelled"] or scanned["cancelled"]
                )
            else:
                raise ValueError(
                    f"Acción de biblioteca desconocida: {self.action}"
                )

            self.completed.emit(result)

        except Exception as error:
            self.failed.emit(str(error))


def _settings_icon(color="#7f8a91"):
    custom_icon = load_ui_icon("setting", color)
    if not custom_icon.isNull():
        return custom_icon

    center = 12
    path = QPainterPath()
    for tooth in range(8):
        angle = tooth * math.tau / 8
        for offset, radius in (
            (-math.pi / 8, 8),
            (-math.pi / 8 + 0.035, 8),
            (-math.pi / 8 + 0.035, 11),
            (math.pi / 8 - 0.035, 11),
            (math.pi / 8 - 0.035, 8),
            (math.pi / 8, 8),
        ):
            point = QPointF(
                center + math.cos(angle + offset) * radius,
                center + math.sin(angle + offset) * radius,
            )
            if path.elementCount() == 0:
                path.moveTo(point)
            else:
                path.lineTo(point)
    path.closeSubpath()
    path.addEllipse(QRectF(8.5, 8.5, 7, 7))
    path.setFillRule(Qt.OddEvenFill)

    pixmap = QPixmap(24, 24)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.fillPath(path, QColor(color))
    painter.end()
    return QIcon(pixmap)


class SettingsButton(QPushButton):

    def enterEvent(self, event):
        self.setIcon(_settings_icon("#b0bac0"))
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setIcon(_settings_icon("#7f8a91"))
        super().leaveEvent(event)


class MainWindow(QMainWindow):

    def __init__(self):

        super().__init__()

        self.setWindowTitle(
            "TatiVision"
        )

        self.resize(
            1200,
            800
        )
        self.setStyleSheet(APP_STYLESHEET)

        self.movies = []
        self.series = []
        self.library_worker = None
        self._settings_dialog = None
        self.active_catalog = "movies"

        self.showing_favorites = False
        self.showing_unwatched = False

        self.selected_genre = None

        self.search_text = ""
        self.filter_timer = QTimer(self)
        self.filter_timer.setSingleShot(True)
        self.filter_timer.timeout.connect(self._apply_filters_now)

        central_widget = QWidget()
        central_widget.setObjectName("appCentral")

        self.setCentralWidget(
            central_widget
        )

        main_layout = QHBoxLayout()

        central_widget.setLayout(
            main_layout
        )

        # -------------------------
        # Panel izquierdo
        # -------------------------

        sidebar = QWidget()
        sidebar.setObjectName("appSidebar")
        left_panel = QVBoxLayout(sidebar)
        left_panel.setContentsMargins(12, 16, 12, 14)
        left_panel.setSpacing(8)

        library_heading = QLabel("BIBLIOTECA")
        library_heading.setStyleSheet(
            "color: #7e8a90; font-size: 10px; font-weight: 700; "
            "letter-spacing: 1px; padding: 4px 2px;"
        )
        left_panel.addWidget(library_heading)

        self.library_panel = LibraryPanel()
        self.library_panel.addLibraryRequested.connect(
            self.add_library
        )
        self.library_panel.librarySelected.connect(
            self.select_active_library
        )
        self.library_panel.libraryDeleteRequested.connect(
            self.delete_library
        )
        self.library_panel.genreSelected.connect(
            self.filter_by_genre
        )
        left_panel.addWidget(self.library_panel, 1)

        self.scan_button = QPushButton("Analizar y cargar películas")
        self.metadata_button = QPushButton("Cargar datos pendientes")
        self.force_update_button = QPushButton("Carga forzada")

        self.scan_button.setToolTip(
            "Analiza la carpeta, agrega los archivos nuevos y carga sus "
            "metadatos pendientes desde TMDb."
        )
        self.metadata_button.setToolTip(
            "Consulta TMDb para el contenido que todavía no tiene datos."
        )
        self.force_update_button.setToolTip(
            "Vuelve a analizar la biblioteca y actualiza todos sus metadatos."
        )

        for button in (
            self.scan_button,
            self.metadata_button,
            self.force_update_button,
        ):
            button.setMinimumHeight(36)
            button.setObjectName("libraryAction")
            button.setCursor(Qt.PointingHandCursor)
            left_panel.addWidget(button)

        self.library_buttons = (
            self.scan_button,
            self.metadata_button,
            self.force_update_button,
        )

        self.library_progress = QProgressBar()
        self.library_progress.setRange(0, 0)
        self.library_progress.setTextVisible(False)
        self.library_progress.setFixedHeight(5)
        self.library_progress.setStyleSheet("""
            QProgressBar {
                background-color: #252d32;
                border: none;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #00c94b;
                border-radius: 2px;
            }
        """)
        self.library_progress.hide()
        left_panel.addWidget(self.library_progress)

        self.cancel_library_button = QPushButton("Cancelar")
        self.cancel_library_button.setObjectName("libraryAction")
        self.cancel_library_button.setMinimumHeight(32)
        self.cancel_library_button.setCursor(Qt.PointingHandCursor)
        self.cancel_library_button.clicked.connect(self.cancel_library_task)
        self.cancel_library_button.hide()
        left_panel.addWidget(self.cancel_library_button)

        self.library_status = QLabel()
        self.library_status.setWordWrap(True)
        self.library_status.setStyleSheet(
            "color: #aaaaaa; font-size: 11px;"
        )
        left_panel.addWidget(self.library_status)

        self.settings_button = SettingsButton()
        self.settings_button.setObjectName("settingsIcon")
        self.settings_button.setIcon(_settings_icon())
        self.settings_button.setIconSize(QSize(23, 23))
        self.settings_button.setFixedSize(30, 32)
        self.settings_button.setCursor(Qt.PointingHandCursor)
        self.settings_button.setAccessibleName("Ajustes")
        self.settings_button.setToolTip("Ajustes")
        self.settings_button.clicked.connect(self.open_settings)
        tmdb_logo_button = QToolButton()
        tmdb_logo_button.setObjectName("tmdbLogoButton")
        tmdb_logo_button.setIcon(
            load_ui_icon("tmdb_logo")
        )
        tmdb_logo_button.setIconSize(QSize(96, 14))
        tmdb_logo_button.setFixedSize(104, 28)
        tmdb_logo_button.setAutoRaise(True)
        tmdb_logo_button.setCursor(Qt.PointingHandCursor)
        tmdb_logo_button.setAccessibleName("TMDB")
        tmdb_logo_button.setToolTip(
            "Este producto usa TMDB y sus API, pero no está respaldado, "
            "certificado ni aprobado por TMDB. Abrir TMDB."
        )
        tmdb_logo_button.clicked.connect(
            lambda: QDesktopServices.openUrl(
                QUrl("https://www.themoviedb.org")
            )
        )
        settings_footer = QHBoxLayout()
        settings_footer.setContentsMargins(0, 0, 0, 0)
        settings_footer.addWidget(self.settings_button)
        settings_footer.addStretch()
        settings_footer.addWidget(tmdb_logo_button)
        left_panel.addLayout(settings_footer)

        tmdb_attribution = QLabel(
            "This product uses TMDB and the TMDB APIs but is not endorsed, "
            "certified, or otherwise approved by TMDB."
        )
        tmdb_attribution.setWordWrap(True)
        tmdb_attribution.setStyleSheet(
            "color: #7e8a90; font-size: 9px;"
        )
        left_panel.addWidget(tmdb_attribution)

        self.scan_button.clicked.connect(
            lambda: self.start_library_task(
                "import_movies"
                if self.active_catalog == "movies"
                else "scan_series"
            )
        )
        self.metadata_button.clicked.connect(
            lambda: self.start_library_task(
                "metadata"
                if self.active_catalog == "movies"
                else "series_metadata"
            )
        )
        self.force_update_button.clicked.connect(
            lambda: self.start_library_task(
                "force"
                if self.active_catalog == "movies"
                else "series_force"
            )
        )

        # -------------------------
        # Panel derecho
        # -------------------------

        right_panel = QVBoxLayout()

        self.header = HeaderWidget()

        self.header.catalogChanged.connect(
            self.switch_catalog
        )
        self.header.search_bar.textChanged.connect(
            self.filter_movies
        )

        self.header.favorites_button.clicked.connect(
            self.toggle_favorites
        )
        self.header.watched_filter_button.clicked.connect(
            self.toggle_watched_filter
        )

        # -------------------------
        # Vistas
        # -------------------------

        self.stacked_widget = QStackedWidget()

        self.home_view = HomeView(
            self.open_movie
        )

        self.filtered_view = FilteredView()
        self.movie_detail_view = MovieDetailWindow()
        self.movie_detail_view.backRequested.connect(
            self.close_movie_detail
        )
        self.movie_detail_view.favoriteChanged.connect(
            self.update_movie_favorite
        )
        self.movie_detail_view.watchedChanged.connect(
            self.update_movie_watched
        )
        self.movie_detail_view.metadataRefreshRequested.connect(
            self.refresh_movie_metadata
        )
        self.movie_return_view = None

        self.series_view = SeriesCatalogView()
        self.series_view.seriesSelected.connect(
            self.open_series
        )
        self.home_view.favoriteChanged.connect(
            self.update_movie_favorite
        )
        self.home_view.watchedChanged.connect(
            self.update_movie_watched
        )
        self.filtered_view.favoriteChanged.connect(
            self.update_movie_favorite
        )
        self.filtered_view.watchedChanged.connect(
            self.update_movie_watched
        )

        self.stacked_widget.addWidget(
            self.home_view
        )

        self.stacked_widget.addWidget(
            self.filtered_view
        )
        self.stacked_widget.addWidget(
            self.series_view
        )
        self.stacked_widget.addWidget(
            self.movie_detail_view
        )

        right_panel.addWidget(
            self.header
        )

        right_panel.addWidget(
            self.stacked_widget
        )

        main_layout.addWidget(sidebar, 1)

        main_layout.addLayout(
            right_panel,
            5
        )

        self.load_movies()

    def load_movies(self, apply_filters=True):
        movies_path = get_user_setting("movies_path")
        series_path = get_user_setting("series_path")
        self.movies = get_all_movies(movies_path) if movies_path else []
        self.series = get_all_series(series_path) if series_path else []
        self.filtered_view.retain_movies(self.movies)
        self.home_view.reload(self.movies, movies_path or "")
        self.series_view.render_series(self.series, series_path or "")
        self.refresh_genres()
        self.refresh_library_buttons()
        if apply_filters:
            self.apply_filters()

    def open_settings(self):
        if self._settings_dialog is not None:
            self._settings_dialog.raise_()
            self._settings_dialog.activateWindow()
            return

        self.filter_timer.stop()
        self.filtered_view.cancel_render()
        dialog = SettingsDialog(self)
        self._settings_dialog = dialog
        dialog.databaseReset.connect(self.load_movies)
        dialog.finished.connect(self._settings_dialog_finished)
        dialog.open()

    def _settings_dialog_finished(self, result):
        if result == QDialog.DialogCode.Accepted:
            self.library_status.setText("Ajustes guardados.")
        dialog = self._settings_dialog
        self._settings_dialog = None
        if dialog is not None:
            dialog.deleteLater()
        self.apply_filters()

    def add_library(self):
        dialog = LibraryDialog(self)
        if not dialog.exec() or dialog.library is None:
            return
        library = dialog.library
        self.selected_genre = None
        self.load_movies()
        configured_libraries = set()
        if library["movies_path"]:
            configured_libraries.add("movies")
        if library["series_path"]:
            configured_libraries.add("series")
        self.library_status.setText(
            f"Analizando la biblioteca «{library['name']}»..."
        )
        self.start_library_task(
            "scan_configured",
            configured_libraries=configured_libraries,
            library=library,
        )

    def select_active_library(self, library_id):
        try:
            select_library(library_id)
        except (LookupError, RuntimeError) as error:
            QMessageBox.critical(
                self,
                "No se pudo cambiar la biblioteca",
                str(error),
            )
            return
        self.selected_genre = None
        self.showing_favorites = False
        self.showing_unwatched = False
        self.header.favorites_button.setChecked(False)
        self.header.watched_filter_button.setChecked(False)
        self._sync_filter_icons()
        self.load_movies()
        self.library_status.setText("Biblioteca seleccionada.")

    def delete_library(self, library_id):
        library = next(
            (
                item for item in get_libraries()
                if item["id"] == library_id
            ),
            None,
        )
        if library is None:
            QMessageBox.warning(
                self,
                "Biblioteca no encontrada",
                "La biblioteca seleccionada ya no existe.",
            )
            self.load_movies()
            return

        answer = QMessageBox.question(
            self,
            "Borrar biblioteca",
            (
                f"¿Querés borrar la biblioteca «{library['name']}»?\n\n"
                "Se quitarán sus rutas y su configuración de TatiVision. "
                "Las películas, series y metadatos guardados en el catálogo "
                "no se borrarán."
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return

        try:
            deleted_library = delete_library(library_id)
        except (LookupError, RuntimeError) as error:
            QMessageBox.critical(
                self,
                "No se pudo borrar la biblioteca",
                str(error),
            )
            return

        self.selected_genre = None
        self.showing_favorites = False
        self.showing_unwatched = False
        self.header.favorites_button.setChecked(False)
        self.header.watched_filter_button.setChecked(False)
        self._sync_filter_icons()
        self.load_movies()
        self.library_status.setText(
            f"Biblioteca «{deleted_library['name']}» borrada. "
            "El catálogo y sus metadatos se conservaron."
        )

    def refresh_library_buttons(self):
        movies_path = get_user_setting("movies_path")
        series_path = get_user_setting("series_path")
        active_path = (
            series_path if self.active_catalog == "series" else movies_path
        )
        self.scan_button.setEnabled(
            bool(active_path and os.path.isdir(active_path))
        )
        has_catalog_content = bool(
            self.series if self.active_catalog == "series" else self.movies
        )
        self.metadata_button.hide()
        self.metadata_button.setEnabled(has_catalog_content)
        self.force_update_button.setEnabled(has_catalog_content)
        if self.library_worker and self.library_worker.isRunning():
            for button in self.library_buttons:
                button.setEnabled(False)
            self.settings_button.setEnabled(False)
            self.library_panel.setEnabled(False)
        else:
            self.settings_button.setEnabled(True)
            self.library_panel.setEnabled(True)

    def refresh_genres(self):
        if self.active_catalog == "movies":
            movies_path = get_user_setting("movies_path")
            genres = get_all_genres(movies_path) if movies_path else []
        else:
            series_path = get_user_setting("series_path")
            genres = get_all_series_genres(series_path) if series_path else []

        if (
            self.selected_genre
            and self.selected_genre not in genres
        ):
            self.selected_genre = None
        active_library = get_active_library()
        self.library_panel.set_libraries(
            get_libraries(),
            active_library["id"] if active_library else "",
            genres,
            self.selected_genre,
        )

    def switch_catalog(self, catalog):

        self.active_catalog = catalog
        self.selected_genre = None
        self.showing_favorites = False
        self.showing_unwatched = False
        self.header.search_bar.set_catalog(catalog)
        self.header.favorites_button.setChecked(False)
        self.header.watched_filter_button.blockSignals(True)
        self.header.watched_filter_button.setChecked(False)
        self.header.watched_filter_button.blockSignals(False)
        self._sync_filter_icons()

        if catalog == "movies":
            self.scan_button.setText("Analizar y cargar películas")
            self.scan_button.setToolTip(
                "Analiza la carpeta, agrega los archivos nuevos y carga sus "
                "metadatos pendientes desde TMDb."
            )
            self.metadata_button.hide()
            self.header.favorites_button.show()
            self.header.watched_filter_button.show()
        else:
            self.scan_button.setText("Analizar y cargar series")
            self.scan_button.setToolTip(
                "Analiza la carpeta, agrega series y episodios nuevos y carga "
                "los metadatos pendientes desde TMDb."
            )
            self.metadata_button.setText("Cargar datos de series")
            self.metadata_button.setToolTip(
                "Consulta TMDb para las series que todavía no tienen datos."
            )
            self.force_update_button.setText("Carga forzada de series")
            self.force_update_button.setToolTip(
                "Vuelve a analizar la carpeta y actualiza en TMDb todas las series."
            )
            self.header.favorites_button.hide()
            self.header.watched_filter_button.hide()
            self.series_view.show_catalog()

        if catalog == "movies":
            self.metadata_button.setText("Cargar datos pendientes")
            self.force_update_button.setText("Carga forzada")

        self.refresh_library_buttons()
        self.refresh_genres()
        self.apply_filters()

    def start_library_task(
        self,
        action,
        configured_libraries=None,
        movie_id=None,
        library=None,
    ):

        if (
            self.library_worker
            and self.library_worker.isRunning()
        ):
            return

        is_series_action = action in (
            "scan_series",
            "series_metadata",
            "series_force",
        )
        selected_library = library or get_active_library() or {}
        root_path = selected_library.get(
            "series_path" if is_series_action else "movies_path",
            "",
        )
        requires_root = action in (
            "scan",
            "import_movies",
            "scan_series",
            "force",
            "series_metadata",
            "series_force",
            "metadata_movie",
        )
        if requires_root and not root_path:
            QMessageBox.information(
                self,
                "No hay una carpeta seleccionada",
                "Agregá una biblioteca con una carpeta de contenido antes "
                "de iniciar esta tarea.",
            )
            self.add_library()
            return
        if requires_root and not os.path.isdir(root_path):
            QMessageBox.information(
                self,
                "Carpeta no disponible",
                "La carpeta configurada para esta biblioteca ya no está "
                "disponible.",
            )
            return

        task_status = {
            "scan": "Analizando la biblioteca de películas...",
            "import_movies": "Analizando películas y cargando metadatos...",
            "scan_series": "Analizando series y cargando metadatos pendientes...",
            "force": "Analizando películas y actualizando metadatos...",
            "series_force": "Analizando series y actualizando metadatos...",
            "scan_configured": "Actualizando las bibliotecas...",
            "metadata_movie": "Buscando coincidencias de TMDb para la película...",
        }
        self.library_status.setText(
            task_status.get(action, "Actualizando información desde TMDb...")
        )

        for button in self.library_buttons:
            button.setEnabled(False)
        self.settings_button.setEnabled(False)
        self.library_panel.setEnabled(False)
        self.library_progress.show()
        cancellable = action in (
            "scan",
            "import_movies",
            "scan_series",
            "metadata",
            "series_metadata",
            "force",
            "series_force",
            "scan_configured",
        )
        self.cancel_library_button.setEnabled(True)
        self.cancel_library_button.setText("Cancelar")
        self.cancel_library_button.setVisible(cancellable)

        self.library_worker = LibraryTask(
            action,
            self,
            configured_libraries=configured_libraries,
            movie_id=movie_id,
            library=selected_library,
        )
        self.library_worker.completed.connect(
            self.library_task_completed
        )
        self.library_worker.metadataReviewRequested.connect(
            self.review_metadata_candidates
        )
        self.library_worker.metadataProgress.connect(
            self.update_metadata_progress
        )
        self.library_worker.failed.connect(
            self.library_task_failed
        )
        self.library_worker.finished.connect(
            self.library_task_finished
        )
        self.library_worker.start()

    def cancel_library_task(self):
        if not self.library_worker or not self.library_worker.isRunning():
            return
        self.library_worker.cancel()
        self.cancel_library_button.setEnabled(False)
        self.cancel_library_button.setText("Cancelando…")
        self.library_status.setText(
            "Cancelando el proceso. Se conservará lo ya analizado/procesado..."
        )

    def update_metadata_progress(self, processed, total, updated, title):
        self.library_status.setText(
            f"Metadatos: {processed}/{total} películas procesadas; "
            f"{updated} cargadas. Última: {title}"
        )

    def review_metadata_candidates(self, decision):
        dialog = MetadataCandidateDialog(
            decision["movie"],
            decision["candidates"][:10],
            self,
        )
        try:
            if dialog.exec():
                decision["selected_tmdb_id"] = dialog.selected_tmdb_id()
        finally:
            decision["event"].set()

    def library_task_completed(self, result):
        movie_id = result.get("movie_id")
        self.load_movies(apply_filters=movie_id is None)

        if movie_id is not None:
            movie = get_movie_by_id(movie_id)
            if movie is not None:
                self.movie_detail_view.show_movie(movie)
                self._set_main_view(self.movie_detail_view)

        if "series_found" in result:
            if result.get("configured_scan"):
                status = (
                    f"Bibliotecas actualizadas: {result['scanned']} películas, "
                    f"{result['series_found']} series y "
                    f"{result['episodes_found']} episodios; metadatos de "
                    f"series actualizados: {result['metadata_updated']}; "
                    f"metadatos de películas actualizados: "
                    f"{result['movie_metadata']['updated']}."
                )
            if result.get("cancelled"):
                if result.get("configured_scan"):
                    status = (
                        f"Proceso cancelado. Se analizaron "
                        f"{result['scanned']} películas y "
                        f"{result['series_found']} series; se actualizaron "
                        f"{result['metadata_updated']} metadatos de series y "
                        f"{result['movie_metadata']['updated']} de películas. "
                        "Los cambios completados quedaron guardados."
                    )
                else:
                    status = (
                        f"Proceso de series cancelado. Se analizaron "
                        f"{result['series_found']} series y "
                        f"{result['episodes_found']} episodios; se "
                        f"actualizaron {result['metadata_updated']} "
                        "metadatos. Los cambios completados quedaron "
                        "guardados."
                    )
            elif "scanned_series" in result:
                status = (
                    f"Escaneo forzado: {result['scanned_series']} series, "
                    f"{result['scanned_episodes']} episodios; "
                    f"metadatos TMDb actualizados: "
                    f"{result['metadata_updated']}."
                )
            elif result.get("series_import"):
                status = (
                    f"Biblioteca de series actualizada: "
                    f"{result['series_found']} series y "
                    f"{result['episodes_found']} episodios; metadatos "
                    f"actualizados: {result['metadata_updated']}."
                )
            elif result.get("series_scan_only"):
                status = (
                    f"Series encontradas: {result['series_found']}; "
                    f"episodios: {result['episodes_found']}; "
                    f"metadatos TMDb actualizados: "
                    f"{result['metadata_updated']}."
                )
            else:
                status = (
                    f"Series con metadatos procesadas: "
                    f"{result['series_found']}; episodios: "
                    f"{result['episodes_found']}; actualizadas: "
                    f"{result['metadata_updated']}."
                )
            self.library_status.setText(status)

            has_movie_metadata_errors = bool(
                result.get("configured_scan")
                and (
                    result["movie_metadata"]["failed"]
                    or result["movie_metadata"]["not_found"]
                )
            )
            if result["failed"] or result["not_found"] or has_movie_metadata_errors:
                details = [
                    f"{failure['title']}: {failure['error']}"
                    for failure in result["failed"]
                ]
                details.extend(
                    f"{title}: no se encontró en TMDb"
                    for title in result["not_found"]
                )
                if result.get("configured_scan"):
                    movie_metadata = result["movie_metadata"]
                    details.extend(
                        f"{failure['title']}: {failure['error']}"
                        for failure in movie_metadata["failed"]
                    )
                    if movie_metadata["not_found"]:
                        details.append(
                            f"{movie_metadata['not_found']} películas no "
                            "encontradas en TMDb."
                        )
                QMessageBox.warning(
                    self,
                    (
                        "Actualización de bibliotecas incompleta"
                        if result.get("configured_scan")
                        else "Actualización de series incompleta"
                    ),
                    status + "\n\n" + "\n".join(details),
                )
            if result.get("configured_scan"):
                self.confirm_missing_movies(
                    result["missing"],
                    result["scanned"],
                )
            return

        if "updated" in result:
            metadata_status = (
                f"Metadatos actualizados: {result['updated']}. "
                f"Sin coincidencia: {result['not_found']}. "
                f"Omitidos: {result.get('skipped', 0)}. "
                f"Fallidos: {len(result['failed'])}."
            )
            if result.get("movie_id") is not None:
                metadata_status = (
                    f"Actualización individual: {metadata_status}"
                )
            status = metadata_status
            if "scanned" in result:
                status = (
                    f"Escaneo terminado ({result['scanned']} archivos). "
                    + metadata_status
                )
            if result.get("configured_scan"):
                movie_metadata = result["movie_metadata"]
                status = (
                    f"Biblioteca actualizada ({result['scanned']} archivos). "
                    f"Metadatos: {movie_metadata['updated']} actualizados, "
                    f"{movie_metadata['not_found']} sin coincidencia, "
                    f"{len(movie_metadata['failed'])} fallidos."
                )
            if result.get("cancelled"):
                status = (
                    f"Proceso cancelado. Se analizaron {result.get('scanned', 0)} "
                    f"archivos y se actualizaron {result['updated']} metadatos; "
                    "los cambios completados quedaron guardados."
                )
            self.library_status.setText(status)

            failures = list(result["failed"])
            if result.get("configured_scan"):
                failures.extend(result["movie_metadata"]["failed"])
            if failures:
                failures = "\n".join(
                    f"{failure['title']}: {failure['error']}"
                    for failure in failures[:10]
                )
                if len(result["failed"]) > 10:
                    failures += (
                        f"\n… y {len(result['failed']) - 10} más"
                    )
                QMessageBox.warning(
                    self,
                    "Actualización incompleta",
                    status + "\n\n" + failures,
                )
            elif result["not_found"] or (
                result.get("configured_scan")
                and result["movie_metadata"]["not_found"]
            ):
                QMessageBox.information(
                    self,
                    "Actualización terminada",
                    status,
                )
            if "missing" in result:
                self.confirm_missing_movies(
                    result["missing"],
                    result["scanned"],
                )
            return

        self.library_status.setText(
            f"Análisis terminado. Archivos de video encontrados: {result['scanned']}."
        )
        self.confirm_missing_movies(
            result["missing"],
            result["scanned"],
        )

    def confirm_missing_movies(self, missing_movies, scanned_count):

        if not missing_movies:
            return

        movie_list = "\n".join(
            f"- {movie['title']}"
            for movie in missing_movies[:10]
        )
        if len(missing_movies) > 10:
            movie_list += (
                f"\n… y {len(missing_movies) - 10} más"
            )

        answer = QMessageBox.question(
            self,
            "Películas que ya no están en el disco",
            (
                f"Se encontraron {len(missing_movies)} registros cuyo archivo "
                "ya no aparece en la carpeta de películas:\n\n"
                f"{movie_list}\n\n"
                "¿Querés borrarlos de la base de datos? "
                "Los archivos del disco no se modifican."
            ),
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if answer != QMessageBox.Yes:
            self.library_status.setText(
                f"Análisis terminado. {scanned_count} archivos encontrados; "
                f"{len(missing_movies)} registros faltantes conservados."
            )
            return

        try:
            still_missing_ids = []
            for movie in missing_movies:
                try:
                    os.stat(movie["path"])
                except FileNotFoundError:
                    still_missing_ids.append(movie["id"])

            deleted_count = delete_movies_by_ids(still_missing_ids)
        except Exception as error:
            self.library_task_failed(str(error))
            return

        self.load_movies()
        self.library_status.setText(
            f"Análisis terminado. {scanned_count} archivos encontrados; "
            f"{deleted_count} registros eliminados de la base."
        )

    def library_task_failed(self, message):

        self.library_status.setText(
            f"No se pudo completar la tarea: {message}"
        )
        QMessageBox.critical(
            self,
            "Error al actualizar la biblioteca",
            message,
        )

    def library_task_finished(self):

        self.library_worker = None
        self.library_progress.hide()
        self.cancel_library_button.hide()
        self.refresh_library_buttons()

    def filter_movies(self, text):

        self.search_text = text

        self.apply_filters()

    def toggle_favorites(self):
        self.showing_favorites = self.header.favorites_button.isChecked()
        self._sync_filter_icons()
        self.apply_filters()

    def toggle_watched_filter(self):
        self.showing_unwatched = self.header.watched_filter_button.isChecked()
        self._sync_filter_icons()
        self.apply_filters()

    def _sync_filter_icons(self):
        self.header.favorites_button.setIcon(
            load_ui_icon(
                "fav",
                "#ed4650" if self.showing_favorites else "#b24a50",
                filled=self.showing_favorites,
            )
        )
        self.header.watched_filter_button.setIcon(
            load_ui_icon(
                "view",
                "#00c94b" if self.showing_unwatched else "#879197",
            )
        )
        self.header.watched_filter_button.setText(
            "Todas" if self.showing_unwatched else "No vistas"
        )

    def _filter_context(self):
        parts = []
        if self.selected_genre:
            parts.append(f"Género: {self.selected_genre}")
        if self.showing_favorites:
            parts.append("Favoritos")
        if self.showing_unwatched:
            parts.append("No vistas")
        if self.search_text:
            parts.append(f"Búsqueda: «{self.search_text.strip()}»")
        return "Catálogo · " + " · ".join(parts)

    def filter_series(self, series_items):

        filtered_series = series_items

        if self.selected_genre:
            filtered_series = [
                series
                for series in filtered_series
                if self.selected_genre in {
                    genre.strip()
                    for genre in (series.genre or "").split(",")
                }
            ]

        if self.search_text:
            search = self.search_text.casefold()
            filtered_series = [
                series
                for series in filtered_series
                if search in (series.title or "").casefold()
            ]

        return filtered_series

    def filter_by_genre(self, genre):
        self.selected_genre = genre
        self.apply_filters()

    def _filter_movies(self):
        search = self.search_text.casefold()
        selected_genre = self.selected_genre
        filtered_movies = []
        for movie in self.movies:
            if self.showing_favorites and not bool(movie.favorite):
                continue
            if self.showing_unwatched and bool(movie.watched):
                continue
            if selected_genre and selected_genre not in {
                genre.strip()
                for genre in (movie.genre or "").split(",")
            }:
                continue
            if search and search not in (movie.title or "").casefold():
                continue
            filtered_movies.append(movie)
        return filtered_movies

    def apply_filters(self):
        self.filtered_view.cancel_render()
        self.filter_timer.start(0)

    def _apply_filters_now(self):

        if self.active_catalog == "series":
            series_items = self.filter_series(self.series)
            context_parts = []
            if self.selected_genre:
                context_parts.append(f"Género: {self.selected_genre}")
            if self.search_text:
                context_parts.append(
                    f"Búsqueda: «{self.search_text.strip()}»"
                )
            self.series_view.set_context(
                "Catálogo · " + " · ".join(context_parts)
                if context_parts
                else ""
            )
            self.header.movie_count.setText(
                f"Series: {len(series_items)} de {len(self.series)}"
            )
            self.series_view.render_series(
                series_items,
                get_user_setting("series_path"),
                catalog_has_series=bool(self.series),
            )
            self.series_view.show_catalog()
            self._set_main_view(self.series_view)
            return

        use_home_view = (

            not self.search_text

            and not self.selected_genre

            and not self.showing_favorites

            and not self.showing_unwatched
        )

        if use_home_view:

            self.header.movie_count.setText(
                f"Películas: {len(self.movies)}"
            )

            self._set_main_view(self.home_view)
            return

        movies = self._filter_movies()
        self.filtered_view.set_context(self._filter_context())

        self.header.movie_count.setText(
            f"Películas: {len(movies)} de {len(self.movies)}"
        )

        self.filtered_view.render_movies(
            movies,
            self.open_movie
        )
        self._set_main_view(self.filtered_view)

    def resizeEvent(self, event):
        super().resizeEvent(event)

    def open_movie(self, movie_id):

        movie = get_movie_by_id(
            movie_id
        )

        if movie is None:
            QMessageBox.warning(
                self,
                "Película no encontrada",
                f"No se encontró la película con id {movie_id}.",
            )
            return

        self.movie_return_view = self.stacked_widget.currentWidget()
        self.movie_detail_view.show_movie(movie)
        self._set_main_view(self.movie_detail_view)

    def refresh_movie_metadata(self, movie_id):
        self.start_library_task(
            "metadata_movie",
            movie_id=movie_id,
        )

    def _set_main_view(self, view):
        self.stacked_widget.setCurrentWidget(view)

    def close_movie_detail(self):

        if self.movie_return_view is None:
            self.movie_return_view = self.home_view

        return_view = self.movie_return_view
        self.movie_return_view = None

        if return_view is self.series_view:
            self._set_main_view(return_view)
            return

        self.apply_filters()

    def open_series(self, series_id):

        series_path = get_user_setting("series_path")
        series = get_series_by_id(series_id, series_path)
        if series is None:
            QMessageBox.warning(
                self,
                "Serie no encontrada",
                f"No se encontró la serie con id {series_id}.",
            )
            return

        episodes = get_episodes_for_series(series_id, series_path)
        self.series_view.show_detail(series, episodes)
        self._set_main_view(self.series_view)

    def update_movie_favorite(self, movie_id, is_favorite):

        for movie in self.movies:
            if movie.id == movie_id:
                movie.favorite = is_favorite
                break

        self.home_view.update_movie_favorite(
            movie_id,
            is_favorite,
        )
        self.filtered_view.update_movie_favorite(
            movie_id,
            is_favorite,
        )
        if self.stacked_widget.currentWidget() is not self.movie_detail_view:
            self.apply_filters()

    def update_movie_watched(self, movie_id, is_watched):

        for movie in self.movies:
            if movie.id == movie_id:
                movie.watched = is_watched
                break

        self.home_view.update_movie_watched(
            movie_id,
            is_watched,
        )
        self.filtered_view.update_movie_watched(
            movie_id,
            is_watched,
        )
        if self.stacked_widget.currentWidget() is not self.movie_detail_view:
            self.apply_filters()