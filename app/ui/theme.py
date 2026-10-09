APP_STYLESHEET = """
    QMainWindow, QWidget#appCentral, QWidget#appSidebar {
        background-color: #14181c;
        color: #e7eaec;
    }
    QWidget#homeContent, QScrollArea#homeScroll {
        background-color: #101417;
    }
    QFrame#genreSeparator {
        background-color: #252d32;
    }
    QDialog {
        background-color: #14181c;
        color: #e7eaec;
    }
    QWidget#appSidebar {
        border-right: 1px solid #293238;
    }
    QLabel {
        color: #e7eaec;
    }
    QScrollArea {
        border: none;
        background: transparent;
    }
    QToolTip {
        color: #f2f4f5;
        background-color: #20272c;
        border: 1px solid #39434a;
        padding: 4px 6px;
    }
    QListWidget#genreList {
        background-color: #191f23;
        border: 1px solid #293238;
        border-radius: 8px;
        padding: 6px;
        outline: none;
    }
    QListWidget#genreList::item {
        color: #c5cdd1;
        border-radius: 5px;
        padding: 8px 10px;
    }
    QListWidget#genreList::item:hover {
        background-color: #252e33;
        color: #ffffff;
    }
    QListWidget#genreList::item:selected {
        background-color: #173b2a;
        color: #00e054;
        font-weight: 600;
    }
    QLineEdit {
        color: #f2f4f5;
        background-color: #1b2227;
        border: 1px solid #354047;
        border-radius: 7px;
        padding: 9px 12px;
        selection-background-color: #087e3d;
    }
    QLineEdit:focus {
        border-color: #00e054;
    }
    QComboBox, QListWidget {
        color: #e7eaec;
        background-color: #1b2227;
        border: 1px solid #354047;
        border-radius: 6px;
        padding: 5px 8px;
    }
    QComboBox QAbstractItemView {
        color: #e7eaec;
        background-color: #1b2227;
        selection-background-color: #173b2a;
        selection-color: #00e054;
    }
    QListWidget::item {
        border-radius: 4px;
        padding: 6px;
    }
    QListWidget::item:selected {
        color: #00e054;
        background-color: #173b2a;
    }
    QPushButton {
        color: #d7dddf;
        padding: 7px 12px;
        border: 1px solid #354047;
        border-radius: 6px;
        background-color: #1b2227;
    }
    QPushButton:hover {
        color: #ffffff;
        background-color: #252f34;
        border-color: #00e054;
    }
    QPushButton:disabled {
        color: #6f787d;
        background-color: #171c20;
        border-color: #252c30;
    }
    QPushButton#libraryAction {
        color: #d7dddf;
        padding: 8px 10px;
        border: 1px solid #303b41;
        border-radius: 6px;
        background-color: #1b2227;
        text-align: left;
    }
    QPushButton#libraryAction:hover {
        color: #ffffff;
        background-color: #252f34;
        border-color: #00e054;
    }
    QPushButton#libraryAction:disabled {
        color: #6f787d;
        background-color: #171c20;
        border-color: #252c30;
    }
    QPushButton#settingsIcon {
        color: #89939a;
        padding: 0;
        border: none;
        border-radius: 0;
        background-color: transparent;
    }
    QPushButton#settingsIcon:hover {
        background-color: transparent;
    }
    QPushButton#settingsIcon:pressed {
        background-color: transparent;
    }
    QToolButton#tmdbLogoButton {
        padding: 0;
        border: none;
        background: transparent;
    }
    QToolButton#tmdbLogoButton:hover {
        background: transparent;
    }
    QToolButton#addLibraryButton {
        color: #00e054;
        text-align: left;
        font-size: 12px;
        font-weight: 600;
        padding: 8px 10px;
        border: 1px dashed #087e3d;
        border-radius: 6px;
        background-color: #17211c;
    }
    QToolButton#addLibraryButton:hover {
        background-color: #1d3025;
    }
    QFrame#libraryEntry,
    QFrame#activeLibraryEntry {
        background-color: #191f23;
        border: 1px solid #303b41;
        border-radius: 7px;
    }
    QFrame#activeLibraryEntry {
        border-color: #087e3d;
    }
    QToolButton#libraryButton,
    QToolButton#activeLibraryButton {
        color: #d7dddf;
        text-align: left;
        font-size: 12px;
        font-weight: 600;
        padding: 6px 5px;
        border: none;
        border-radius: 0;
        background-color: transparent;
    }
    QToolButton#deleteLibraryButton {
        padding: 0;
        border: none;
        border-radius: 5px;
        background: transparent;
    }
    QToolButton#deleteLibraryButton:hover {
        background: transparent;
    }
    QToolButton#libraryButton:hover,
    QToolButton#activeLibraryButton {
        color: #00e054;
        background-color: transparent;
    }
    QLabel#libraryDescription,
    QLabel#libraryEmptyLabel {
        color: #7e8a90;
        font-size: 11px;
    }
    QListWidget#libraryGenreList {
        background: transparent;
        border: none;
        padding: 0 0 0 12px;
    }
    QListWidget#libraryGenreList::item {
        padding: 6px 8px;
    }
    QPushButton#dangerButton {
        color: #fff1f1;
        font-weight: 700;
        border: 1px solid #8c2830;
        border-radius: 8px;
        background-color: #681d24;
    }
    QPushButton#dangerButton:hover {
        background-color: #8c2830;
        border-color: #be3843;
    }
    QScrollBar:vertical {
        width: 10px;
        margin: 2px;
        background: transparent;
    }
    QScrollBar::handle:vertical {
        min-height: 28px;
        border-radius: 4px;
        background-color: #39454b;
    }
    QScrollBar::handle:vertical:hover {
        background-color: #00a847;
    }
    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical,
    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {
        height: 0;
        background: transparent;
    }
    QScrollBar:horizontal {
        height: 8px;
        margin: 2px;
        background: transparent;
    }
    QScrollBar::handle:horizontal {
        min-width: 28px;
        border-radius: 4px;
        background-color: #39454b;
    }
    QScrollBar::handle:horizontal:hover {
        background-color: #00a847;
    }
    QScrollBar::add-line:horizontal,
    QScrollBar::sub-line:horizontal,
    QScrollBar::add-page:horizontal,
    QScrollBar::sub-page:horizontal {
        width: 0;
        background: transparent;
    }
"""

HEADER_BUTTON_STYLESHEET = """
    QPushButton {
        color: #d7dddf;
        padding: 6px 12px;
        border: 1px solid #354047;
        border-radius: 6px;
        background-color: #1b2227;
    }
    QPushButton:hover {
        color: #ffffff;
        background-color: #252f34;
        border-color: #00e054;
    }
    QPushButton:checked {
        color: #00e054;
        background-color: #173b2a;
        border-color: #087e3d;
        font-weight: 600;
    }
"""
