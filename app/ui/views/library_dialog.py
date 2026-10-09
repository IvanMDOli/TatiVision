from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from config.user_settings import save_library


class LibraryDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Añadir biblioteca")
        self.setMinimumWidth(520)
        self.setModal(True)
        self.library = None

        layout = QVBoxLayout(self)
        description = QLabel(
            "Elegí un nombre y las carpetas que querés incluir en esta "
            "biblioteca. Podés configurar solo películas o solo series."
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #aab4ba;")
        layout.addWidget(description)

        form = QFormLayout()
        self.name_field = QLineEdit()
        self.name_field.setPlaceholderText("Ej.: Cine en casa")
        self.description_field = QLineEdit()
        self.description_field.setMaxLength(20)
        self.description_field.setPlaceholderText("Hasta 20 caracteres")
        self.movies_path_field, movies_row = self._directory_field()
        self.series_path_field, series_row = self._directory_field()
        form.addRow("Nombre *", self.name_field)
        form.addRow("Descripción", self.description_field)
        form.addRow("Carpeta de películas", movies_row)
        form.addRow("Carpeta de series", series_row)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel_button = QPushButton("Cancelar")
        confirm_button = QPushButton("Confirmar")
        cancel_button.setCursor(Qt.PointingHandCursor)
        confirm_button.setCursor(Qt.PointingHandCursor)
        confirm_button.setDefault(True)
        cancel_button.clicked.connect(self.reject)
        confirm_button.clicked.connect(self._save)
        buttons.addWidget(cancel_button)
        buttons.addWidget(confirm_button)
        layout.addLayout(buttons)

    def _directory_field(self):
        field = QLineEdit()
        field.setPlaceholderText("No seleccionada")
        browse_button = QPushButton("Elegir…")
        browse_button.setCursor(Qt.PointingHandCursor)
        browse_button.clicked.connect(
            lambda: self._browse_directory(field)
        )
        row = QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.addWidget(field, 1)
        row.addWidget(browse_button)
        wrapper = QWidget()
        wrapper.setLayout(row)
        return field, wrapper

    def _browse_directory(self, field):
        selected_path = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta",
            field.text() or str(Path.home()),
        )
        if selected_path:
            field.setText(selected_path)

    def _save(self):
        name = self.name_field.text().strip()
        description = self.description_field.text().strip()
        movies_path = self.movies_path_field.text().strip()
        series_path = self.series_path_field.text().strip()
        if not name:
            QMessageBox.warning(
                self,
                "Falta el nombre",
                "Ingresá un nombre para la biblioteca.",
            )
            return
        if not movies_path and not series_path:
            QMessageBox.warning(
                self,
                "Falta una carpeta",
                "Elegí al menos una carpeta de películas o series.",
            )
            return
        for label, path in (
            ("películas", movies_path),
            ("series", series_path),
        ):
            if path and not Path(path).is_dir():
                QMessageBox.warning(
                    self,
                    "Carpeta no disponible",
                    f"La carpeta de {label} no existe o no está accesible:\n"
                    f"{path}",
                )
                return
        try:
            self.library = save_library(
                name,
                description,
                movies_path,
                series_path,
            )
        except (RuntimeError, OSError) as error:
            QMessageBox.critical(
                self,
                "No se pudo guardar",
                str(error),
            )
            return
        self.accept()
