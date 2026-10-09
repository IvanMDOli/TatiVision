from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
)


class MetadataCandidateDialog(QDialog):

    def __init__(self, movie, candidates, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Corregir metadatos de la película")
        self.setMinimumSize(560, 460)

        layout = QVBoxLayout(self)
        movie_year = f" ({movie.year})" if movie.year else ""
        heading = QLabel(
            f"Elegí la coincidencia correcta de TMDb para "
            f"{movie.title or 'Sin título'}{movie_year}."
        )
        heading.setWordWrap(True)
        heading.setStyleSheet("font-size: 15px; font-weight: 600;")
        layout.addWidget(heading)

        self.candidate_list = QListWidget()
        self.candidate_list.setSelectionMode(QListWidget.SingleSelection)
        for candidate in candidates:
            release_date = candidate.get("release_date") or ""
            release_year = release_date[:4] if release_date else "año desconocido"
            original_title = candidate.get("original_title") or ""
            display = f"{candidate.get('title') or 'Sin título'} ({release_year})"
            if original_title and original_title.casefold() != (
                candidate.get("title") or ""
            ).casefold():
                display += f"  ·  {original_title}"
            item = QListWidgetItem(display)
            item.setData(Qt.UserRole, candidate["id"])
            item.setData(Qt.UserRole + 1, candidate.get("overview") or "")
            self.candidate_list.addItem(item)
        self.candidate_list.currentItemChanged.connect(
            self._show_candidate_overview
        )
        layout.addWidget(self.candidate_list, 1)

        self.overview = QLabel(
            "Revisá el año y la sinopsis antes de confirmar."
        )
        self.overview.setWordWrap(True)
        self.overview.setMinimumHeight(70)
        self.overview.setStyleSheet("color: #aab4ba;")
        layout.addWidget(self.overview)

        buttons = QDialogButtonBox()
        self.confirm_button = buttons.addButton(
            "Usar esta película",
            QDialogButtonBox.AcceptRole,
        )
        self.skip_button = buttons.addButton(
            "Omitir",
            QDialogButtonBox.RejectRole,
        )
        self.confirm_button.setEnabled(False)
        self.confirm_button.clicked.connect(self.accept)
        self.skip_button.clicked.connect(self.reject)
        layout.addWidget(buttons)

    def selected_tmdb_id(self):
        item = self.candidate_list.currentItem()
        return item.data(Qt.UserRole) if item else None

    def _show_candidate_overview(self, current, _previous):
        self.confirm_button.setEnabled(current is not None)
        if current is None:
            self.overview.setText(
                "Revisá el año y la sinopsis antes de confirmar."
            )
            return

        overview = current.data(Qt.UserRole + 1)
        self.overview.setText(overview or "Sin sinopsis disponible.")
