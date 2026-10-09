import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from app.ui.main_window import MainWindow
from app.ui.views.settings_dialog import SettingsDialog
from config.user_settings import get_user_settings, has_completed_initial_setup

from app.bootstrap import (
    initialize_database
)
from config.runtime import resource_path


def main():
    app = QApplication(sys.argv)
    application_icon = resource_path("assets/icons/app.ico")
    if application_icon.is_file():
        app.setWindowIcon(QIcon(str(application_icon)))

    try:
        get_user_settings()
        initial_setup_required = not has_completed_initial_setup()
    except RuntimeError as error:
        QMessageBox.critical(
            None,
            "No se pudo cargar la configuración",
            f"{error}\n\nCorregí o eliminá settings.json y volvé a iniciar.",
        )
        return

    initialize_database()

    window = MainWindow()
    window.showMaximized()

    if initial_setup_required:
        setup_dialog = SettingsDialog(window, initial_setup=True)
        if not setup_dialog.exec():
            window.close()
            return
        window.load_movies()

    sys.exit(app.exec())


if __name__ == "__main__":

    main()