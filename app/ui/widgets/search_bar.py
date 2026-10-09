from PySide6.QtWidgets import (
    QLineEdit
)


class SearchBar(QLineEdit):

    def __init__(self):

        super().__init__()

        self.setPlaceholderText(
            "Buscar película..."
        )

    def set_catalog(self, catalog):

        self.setPlaceholderText(
            "Buscar serie..."
            if catalog == "series"
            else "Buscar película..."
        )