from PySide6.QtCore import Qt
from PySide6.QtCore import Signal

from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QScrollArea
)

from app.ui.widgets.movie_card import (
    MovieCard
)

CAROUSEL_ARROW_STYLESHEET = """
    QPushButton {
        border: 1px solid rgba(255, 255, 255, 55);
        border-radius: 18px;
        background-color: rgba(20, 24, 28, 225);
        color: white;
        font-size: 18px;
    }
    QPushButton:hover {
        background-color: rgba(0, 168, 71, 235);
        border-color: rgba(255, 255, 255, 150);
    }
    QPushButton:pressed {
        background-color: rgba(0, 115, 49, 245);
    }
"""


class MovieRow(QWidget):

    favoriteChanged = Signal(int, bool)
    watchedChanged = Signal(int, bool)

    def __init__(
        self,
        title,
        movies,
        click_handler
    ):

        super().__init__()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

        self.click_handler = click_handler

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        title_label = QLabel(
            title
        )
        title_label.setObjectName("genreTitle")
        title_label.setStyleSheet(
            "color: #e8edef; font-size: 17px; font-weight: 700; "
            "letter-spacing: 0.2px; padding: 2px 0;"
        )

        layout.addWidget(
            title_label
        )

        self.card_step = 235

        self.scroll = QScrollArea()
        self.scroll.setStyleSheet(
            "QScrollArea { background: transparent; }"
            "QScrollArea > QWidget > QWidget { background: transparent; }"
        )

        self.scroll.setWidgetResizable(
            False
        )

        self.scroll.setFrameShape(
            QScrollArea.NoFrame
        )

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff
        )

        self.scroll.setFixedHeight(420)

        container = QWidget()
        container.setAttribute(Qt.WA_TranslucentBackground)
        container.setStyleSheet("background: transparent;")

        self.row_layout = QHBoxLayout(container)
        self.row_layout.setContentsMargins(14, 12, 14, 18)

        self.row_layout.setSpacing(
            15
        )

        self.row_layout.setAlignment(
            Qt.AlignLeft
        )

        self.cards = []

        for movie in movies:

            card = MovieCard(
                movie
            )
            self.cards.append(card)

            card.clicked.connect(
                click_handler
            )
            card.favoriteChanged.connect(
                self.favoriteChanged.emit
            )
            card.watchedChanged.connect(
                self.watchedChanged.emit
            )

            self.row_layout.addWidget(
                card
            )

        container.adjustSize()

        self.scroll.setWidget(
            container
        )
        self.scroll.horizontalScrollBar().rangeChanged.connect(
            lambda *_: self.update_arrows()
        )

        layout.addWidget(
            self.scroll
        )

        self.left_button = QPushButton(
            "❮"
        )

        self.right_button = QPushButton(
            "❯"
        )
        self.left_button.setCursor(Qt.PointingHandCursor)
        self.right_button.setCursor(Qt.PointingHandCursor)

        self.left_button.setFocusPolicy(
            Qt.NoFocus
        )

        self.right_button.setFocusPolicy(
            Qt.NoFocus
        )

        self.left_button.setParent(
            self
        )

        self.right_button.setParent(
            self
        )

        self.left_button.setFixedSize(36, 36)

        self.right_button.setFixedSize(36, 36)

        self.left_button.setStyleSheet(CAROUSEL_ARROW_STYLESHEET)
        self.right_button.setStyleSheet(CAROUSEL_ARROW_STYLESHEET)

        self.left_button.clicked.connect(
            self.scroll_left
        )

        self.right_button.clicked.connect(
            self.scroll_right
        )

        self.scroll.horizontalScrollBar().valueChanged.connect(
            lambda *_: self.update_arrows()
        )

        self.update_arrows()

    def resizeEvent(self, event):

        super().resizeEvent(event)

        center_y = (
            self.scroll.geometry().y()
            + (self.scroll.height() - self.left_button.height()) // 2
        )

        self.left_button.move(
            5,
            center_y
        )

        self.right_button.move(
            self.width() - 41,
            center_y
        )

        self.update_arrows()

    def update_movie_favorite(self, movie_id, is_favorite):

        for card in self.cards:
            if card.movie_id == movie_id:
                card.update_favorite(is_favorite)
                return

    def update_movie_watched(self, movie_id, is_watched):

        for card in self.cards:
            if card.movie_id == movie_id:
                card.update_watched(is_watched)
                return

    def update_arrows(self):

        bar = self.scroll.horizontalScrollBar()

        has_overflow = (
            bar.maximum() > 0
        )

        if not has_overflow:

            self.left_button.hide()

            self.right_button.hide()

            return

        self.left_button.setVisible(
            bar.value() > 0
        )

        self.right_button.setVisible(
            bar.value() < bar.maximum()
        )

    def scroll_right(self):

        bar = self.scroll.horizontalScrollBar()

        bar.setValue(
            bar.value() + self.card_step
        )

    def scroll_left(self):

        bar = self.scroll.horizontalScrollBar()

        bar.setValue(
            bar.value() - self.card_step
        )