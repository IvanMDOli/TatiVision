from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtCore import QSize
from PySide6.QtGui import QTransform
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QHBoxLayout,
    QListWidget,
    QScrollArea,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app.ui.icon_utils import load_ui_icon


class DeleteLibraryButton(QToolButton):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCursor(Qt.PointingHandCursor)

    def enterEvent(self, event):
        self.setIcon(load_ui_icon("delete", "#e7434b"))
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.setIcon(load_ui_icon("delete", "#a83c43"))
        super().leaveEvent(event)


class LibraryPanel(QWidget):

    addLibraryRequested = Signal()
    librarySelected = Signal(str)
    libraryDeleteRequested = Signal(str)
    genreSelected = Signal(object)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("libraryPanel")
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QScrollArea.NoFrame)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.viewport().setCursor(Qt.ArrowCursor)
        self.content = QWidget()
        self.layout = QVBoxLayout(self.content)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(5)
        self.layout.setAlignment(Qt.AlignTop)
        self.content.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Minimum,
        )
        self.scroll_area.setWidget(self.content)
        outer_layout.addWidget(self.scroll_area)
        self._library_ids = set()
        self._active_library_id = ""
        self._expanded_library_id = None
        self._libraries = []
        self._genres = []
        self._selected_genre = None
        self._genre_list = None

    def set_libraries(
        self,
        libraries,
        active_library_id,
        genres=(),
        selected_genre=None,
    ):
        previous_active_id = self._active_library_id
        self._libraries = list(libraries)
        self._genres = list(genres)
        self._selected_genre = selected_genre
        self._genre_list = None
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()

        self._library_ids = {item["id"] for item in libraries}
        self._active_library_id = active_library_id or ""
        if (
            self._active_library_id != previous_active_id
            or self._expanded_library_id is None
            or self._expanded_library_id not in self._library_ids
            and self._expanded_library_id != ""
        ):
            self._expanded_library_id = self._active_library_id

        add_button = QToolButton()
        add_button.setObjectName("addLibraryButton")
        add_button.setText("Añadir biblioteca")
        add_button.setIcon(load_ui_icon("add", "#00e054"))
        add_button.setIconSize(QSize(12, 12))
        add_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        add_button.setMinimumHeight(44)
        add_button.setStyleSheet(
            "QToolButton { text-align: center; padding: 3px 8px; }"
        )
        add_button.setCursor(Qt.PointingHandCursor)
        add_button.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed,
        )
        add_button.clicked.connect(self.addLibraryRequested.emit)
        self.layout.addWidget(add_button)

        if not libraries:
            empty_icon = QLabel()
            empty_icon.setAlignment(Qt.AlignCenter)
            empty_icon.setPixmap(
                load_ui_icon("library", "#42505a").pixmap(52, 52)
            )
            empty_label = QLabel("Todavía no hay bibliotecas.")
            empty_label.setObjectName("libraryEmptyLabel")
            empty_label.setWordWrap(True)
            empty_label.setAlignment(Qt.AlignCenter)
            empty_state = QWidget()
            empty_layout = QVBoxLayout(empty_state)
            empty_layout.addStretch(1)
            empty_layout.addWidget(empty_icon)
            empty_layout.addWidget(empty_label)
            empty_layout.addStretch(1)
            self.layout.addWidget(empty_state, 1)
            return

        for library in libraries:
            library_id = library["id"]
            is_active = library_id == self._active_library_id
            is_expanded = library_id == self._expanded_library_id

            row = QFrame()
            row.setObjectName(
                "activeLibraryEntry" if is_active else "libraryEntry"
            )
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(6, 0, 6, 0)
            row_layout.setSpacing(0)
            row.setFixedHeight(40)

            arrow_label = QLabel()
            arrow_label.setFixedSize(22, 22)
            arrow_label.setAlignment(Qt.AlignCenter)
            arrow_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            arrow_pixmap = load_ui_icon(
                "arrow",
                "#00c94b" if is_active else "#7f8a90",
            ).pixmap(QSize(12, 12))
            if is_expanded:
                arrow_pixmap = arrow_pixmap.transformed(
                    QTransform().rotate(180),
                    Qt.SmoothTransformation,
                )
            arrow_label.setPixmap(arrow_pixmap)
            row_layout.addWidget(arrow_label)

            button = QToolButton()
            button.setObjectName(
                "activeLibraryButton" if is_active else "libraryButton"
            )
            button.setText(
                str(library["name"]).upper()
            )
            button.setToolButtonStyle(Qt.ToolButtonTextOnly)
            button.setMinimumHeight(30)
            button.setCursor(Qt.PointingHandCursor)
            button.setStyleSheet(
                "QToolButton { text-align: center; font-size: 13px; "
                "font-weight: 700; }"
            )
            button.setSizePolicy(
                QSizePolicy.Expanding,
                QSizePolicy.Fixed,
            )
            button.setCheckable(True)
            button.setChecked(is_active)
            button.setToolTip(library.get("description", ""))
            button.clicked.connect(
                lambda _, item_id=library_id:
                    self._select_library(item_id)
            )
            row_layout.addWidget(button, 1)

            delete_button = DeleteLibraryButton()
            delete_button.setObjectName("deleteLibraryButton")
            delete_button.setIcon(load_ui_icon("delete", "#a83c43"))
            delete_button.setFixedSize(QSize(22, 22))
            delete_button.setToolButtonStyle(Qt.ToolButtonIconOnly)
            delete_button.setIconSize(QSize(12, 12))
            delete_button.setCursor(Qt.PointingHandCursor)
            delete_button.setAccessibleName(
                f"Borrar biblioteca {library['name']}"
            )
            delete_button.setToolTip(
                f"Borrar la biblioteca «{library['name']}»"
            )
            delete_button.clicked.connect(
                lambda _, item_id=library_id:
                    self.libraryDeleteRequested.emit(item_id)
            )
            row_layout.addWidget(
                delete_button,
                alignment=Qt.AlignVCenter,
            )
            self.layout.addWidget(row)

            if is_expanded and is_active:
                genre_list = QListWidget()
                genre_list.setObjectName("libraryGenreList")
                genre_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                genre_list.setCursor(Qt.PointingHandCursor)
                genre_list.addItem("Todos")
                for genre in genres:
                    genre_list.addItem(genre)
                selected_text = selected_genre or "Todos"
                matches = genre_list.findItems(
                    selected_text,
                    Qt.MatchExactly,
                )
                if matches:
                    genre_list.setCurrentItem(matches[0])
                genre_list.itemClicked.connect(
                    lambda item: self.genreSelected.emit(
                        None if item.text() == "Todos" else item.text()
                    )
                )
                genre_list.viewport().setCursor(Qt.PointingHandCursor)
                row_height = genre_list.sizeHintForRow(0)
                if row_height < 1:
                    row_height = 28
                self._genre_list = genre_list
                genre_list.setSizePolicy(
                    QSizePolicy.Expanding,
                    QSizePolicy.Expanding,
                )
                genre_list.setMinimumHeight(row_height + 8)
                self.layout.addWidget(genre_list, 1)

        if self._genre_list is None:
            self.layout.addStretch(1)
        QTimer.singleShot(0, self._resize_genre_list)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        QTimer.singleShot(0, self._resize_genre_list)

    def _resize_genre_list(self):
        if self._genre_list is None:
            return

        available_height = self._genre_list.geometry().height()
        content_height = (
            self._genre_list.count()
            * max(1, self._genre_list.sizeHintForRow(0))
            + 8
        )
        if available_height < content_height:
            self._genre_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        else:
            self._genre_list.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def _select_library(self, library_id):
        if library_id == self._active_library_id:
            self._expanded_library_id = (
                "" if self._expanded_library_id == library_id else library_id
            )
            self.set_libraries(
                self._libraries,
                self._active_library_id,
                self._genres,
                self._selected_genre,
            )
        else:
            self._active_library_id = library_id
            self._expanded_library_id = library_id
            self.librarySelected.emit(library_id)
