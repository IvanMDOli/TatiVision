import os
from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
)

from app.services.catalog_service import reset_catalog
from config.user_settings import get_user_settings, save_user_settings
from app.vlc.player_catalog import discover_players, programs_directory


class SettingsDialog(QDialog):

    databaseReset = Signal()

    def __init__(self, parent=None, initial_setup=False):
        super().__init__(parent)
        self.setWindowTitle("Ajustes de TatiVision")
        self.setWindowModality(Qt.WindowModal)
        self.setMinimumWidth(540)
        self.setModal(True)
        self.initial_setup = initial_setup

        settings = get_user_settings()
        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        description = QLabel(
            (
                "Antes de empezar, elegí el reproductor que querés usar. "
                "Podés agregar bibliotecas desde el panel izquierdo."
                if initial_setup
                else "Configurá el reproductor y la clave de TMDb. Las "
                "bibliotecas se administran desde el panel izquierdo."
            ),
            self,
        )
        description.setWordWrap(True)
        description.setStyleSheet("color: #aab4ba;")
        layout.addWidget(description)

        form = QFormLayout()
        form.setSpacing(10)

        self.player_mode = QComboBox(self)
        self.player_mode.addItem("Predeterminado de Windows", "system")
        current_mode = settings["player_mode"]
        current_player_path = settings["custom_player_path"]
        selected_index = 0
        for name, executable_path in discover_players():
            self.player_mode.addItem(
                name,
                ("custom", executable_path),
            )
            self.player_mode.setItemData(
                self.player_mode.count() - 1,
                executable_path,
                Qt.ToolTipRole,
            )
            if (
                current_mode == "custom"
                and os.path.normcase(os.path.abspath(current_player_path))
                == os.path.normcase(executable_path)
            ):
                selected_index = self.player_mode.count() - 1

        configured_player_found = selected_index != 0
        if current_mode == "custom":
            current_player = Path(current_player_path)
            if current_player.is_file() and not configured_player_found:
                self.player_mode.addItem(
                    current_player.stem,
                    ("custom", str(current_player.resolve())),
                )
                selected_index = self.player_mode.count() - 1
            elif not current_player.is_file():
                self.player_mode.addItem(
                    f"{current_player.stem} (no encontrado)",
                    ("custom", current_player_path),
                )
                selected_index = self.player_mode.count() - 1

        self.player_mode.addItem(
            "Buscar otro reproductor en Windows…",
            "browse",
        )
        self.player_mode.setToolTip(
            "Elegí un reproductor detectado o buscá manualmente su archivo .exe. "
            "La selección solo afecta a TatiVision."
        )
        if initial_setup:
            self.player_mode.setCurrentIndex(-1)
            self.player_mode.setPlaceholderText("Elegí un reproductor")
        else:
            self.player_mode.setCurrentIndex(selected_index)
        self._last_valid_player_index = (
            self.player_mode.currentIndex()
            if not initial_setup
            else -1
        )
        self.player_mode.activated.connect(self._player_selected)
        form.addRow(
            "Reproductor *" if initial_setup else "Reproductor",
            self.player_mode,
        )

        self.tmdb_key = QLineEdit(settings["tmdb_api_key"], self)
        self.tmdb_key.setEchoMode(QLineEdit.Password)
        self.tmdb_key.setPlaceholderText("Clave API de TMDb")
        self.tmdb_key.setToolTip("La clave se guarda en settings.json junto a la app.")
        form.addRow("Clave API de TMDb", self.tmdb_key)
        layout.addLayout(form)

        self.reset_database_button = QPushButton(
            "Borrar base de datos",
            self,
        )
        self.reset_database_button.setCursor(Qt.PointingHandCursor)
        self.reset_database_button.setObjectName("dangerButton")
        self.reset_database_button.setMinimumHeight(48)
        if initial_setup:
            self.reset_database_button.hide()
        self.reset_database_button.clicked.connect(self._reset_database)
        layout.addWidget(self.reset_database_button)

        buttons = QHBoxLayout()
        buttons.addStretch()
        cancel_button = QPushButton("Cancelar", self)
        cancel_button.setCursor(Qt.PointingHandCursor)
        if initial_setup:
            cancel_button.hide()
        save_button = QPushButton("Guardar", self)
        save_button.setCursor(Qt.PointingHandCursor)
        save_button.setDefault(True)
        cancel_button.clicked.connect(self.reject)
        save_button.clicked.connect(self._save)
        buttons.addWidget(cancel_button)
        buttons.addWidget(save_button)
        layout.addLayout(buttons)

    def _save(self):
        try:
            player_settings = self._selected_player_settings()
            if player_settings is None:
                QMessageBox.warning(
                    self,
                    "Falta elegir reproductor",
                    "Elegí un reproductor instalado o buscá un archivo .exe.",
                )
                return
            save_user_settings({
                **player_settings,
                "tmdb_api_key": self.tmdb_key.text().strip(),
            })
        except RuntimeError as error:
            QMessageBox.critical(self, "No se pudo guardar", str(error))
            return

        self.accept()

    def _reset_database(self):
        answer = QMessageBox.question(
            self,
            "Borrar base de datos",
            "Se eliminarán las películas, series, episodios, metadatos, "
            "bibliotecas y pósteres guardados por TatiVision. "
            "Los archivos de video y el reproductor configurado no se "
            "modificarán. Esta acción no se puede deshacer.\n\n"
            "¿Querés continuar?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if answer != QMessageBox.Yes:
            return

        try:
            reset_catalog()
        except Exception as error:
            QMessageBox.critical(
                self,
                "No se pudo borrar la base de datos",
                str(error),
            )
            return

        self.databaseReset.emit()
        QMessageBox.information(
            self,
            "Base de datos borrada",
            "Se borraron el catálogo y las bibliotecas. Los videos del disco "
            "siguen intactos.",
        )

    def _selected_player_settings(self):
        selected = self.player_mode.currentData()
        if selected == "system":
            return {
                "player_mode": "system",
                "custom_player_path": "",
            }
        if (
            isinstance(selected, tuple)
            and len(selected) == 2
            and selected[0] == "custom"
        ):
            executable_path = selected[1]
            if not Path(executable_path).is_file():
                return None
            return {
                "player_mode": "custom",
                "custom_player_path": str(Path(executable_path).resolve()),
            }
        return None

    def _player_selected(self, index):
        if self.player_mode.itemData(index) != "browse":
            self._last_valid_player_index = index
            return

        previous_index = self._last_valid_player_index
        selected_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar reproductor",
            programs_directory(),
            "Aplicaciones de Windows (*.exe)",
        )
        if not selected_path:
            self.player_mode.setCurrentIndex(previous_index)
            return

        executable_path = Path(selected_path)
        if executable_path.suffix.casefold() != ".exe":
            QMessageBox.warning(
                self,
                "Archivo no compatible",
                "Seleccioná el ejecutable de Windows del reproductor (.exe).",
            )
            self.player_mode.setCurrentIndex(previous_index)
            return

        normalized_path = str(executable_path.resolve())
        for existing_index in range(self.player_mode.count() - 1):
            existing_data = self.player_mode.itemData(existing_index)
            if (
                isinstance(existing_data, tuple)
                and len(existing_data) == 2
                and os.path.normcase(existing_data[1])
                == os.path.normcase(normalized_path)
            ):
                self.player_mode.setCurrentIndex(existing_index)
                self._last_valid_player_index = existing_index
                return

        self.player_mode.insertItem(
            self.player_mode.count() - 1,
            executable_path.stem,
            ("custom", normalized_path),
        )
        self.player_mode.setCurrentIndex(self.player_mode.count() - 2)
        self._last_valid_player_index = self.player_mode.currentIndex()
