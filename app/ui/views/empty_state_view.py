from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from app.ui.icon_utils import load_ui_icon


class EmptyStateView(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 32, 32, 32)
        layout.setSpacing(0)
        layout.addStretch()

        message = QWidget()
        message_layout = QVBoxLayout(message)
        message_layout.setContentsMargins(0, 0, 0, 0)
        message_layout.setSpacing(12)

        self.icon = QLabel()
        self.icon.setAlignment(Qt.AlignCenter)
        self.icon.setPixmap(
            load_ui_icon("movie", "#566168").pixmap(72, 72)
        )
        self.icon.setStyleSheet("padding-bottom: 6px;")
        message_layout.addWidget(self.icon)

        self.title = QLabel()
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setStyleSheet("font-size: 24px; font-weight: 700;")
        message_layout.addWidget(self.title)

        self.description = QLabel()
        self.description.setAlignment(Qt.AlignCenter)
        self.description.setWordWrap(True)
        self.description.setMaximumWidth(520)
        self.description.setStyleSheet(
            "color: #aab4ba; font-size: 14px;"
        )
        message_layout.addWidget(
            self.description,
            alignment=Qt.AlignHCenter,
        )
        layout.addWidget(message, alignment=Qt.AlignCenter)
        layout.addStretch()

    def set_content(self, title, description):
        self.title.setText(title)
        self.description.setText(description)
