from PySide6.QtWidgets import (
    QLineEdit
)


class SearchBar(QLineEdit):

    def __init__(self):

        super().__init__()

        self.setPlaceholderText(
            "Buscar película o director..."
        )

    def set_catalog(self, catalog):

        self.setPlaceholderText(
            "Buscar serie o creador..."
            if catalog == "series"
            else "Buscar película o director..."
        )