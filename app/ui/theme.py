import colorsys
import re

from PySide6.QtWidgets import QWidget


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
        border-top: 1px solid #3B3B3B;
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
    QComboBox#catalogSort {
        padding: 2px 30px 2px 11px;
        border: 1px solid #39454b;
        border-radius: 6px;
        background-color: #20272c;
    }
    QComboBox#catalogSort:hover,
    QComboBox#catalogSort:focus {
        border-color: #00a847;
    }
    QComboBox#catalogSort::drop-down {
        width: 24px;
        border: none;
        border-left: 1px solid #354047;
        border-top-right-radius: 6px;
        border-bottom-right-radius: 6px;
    }
    QComboBox#catalogSort::down-arrow {
        image: none;
        width: 0;
        height: 0;
    }
    QComboBox#catalogSort QAbstractItemView {
        padding: 4px;
        border: 1px solid #354047;
        border-radius: 6px;
        background-color: #1b2227;
        selection-background-color: #173b2a;
        selection-color: #00e054;
        outline: none;
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
        padding: 0;
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
    QCheckBox#darkModeCheck {
        spacing: 9px;
        color: #d7dddf;
        padding: 4px 0;
    }
    QCheckBox#darkModeCheck::indicator {
        width: 18px;
        height: 18px;
        border: 1px solid #536168;
        border-radius: 5px;
        background-color: #1b2227;
    }
    QCheckBox#darkModeCheck::indicator:checked {
        border-color: #00c94b;
        background-color: #087e3d;
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

DARK_TO_LIGHT = {
    "#81a8d1": "#81a8d1",
    "#14181c": "#f4f6f5",
    "#101417": "#eef1ef",
    "#0e1113": "#e4e9e6",
    "#171c20": "#e8ecea",
    "#191f23": "#e9edeb",
    "#1b2227": "#f8f9f8",
    "#20272c": "#e3e8e5",
    "#242e33": "#dce3df",
    "#25272c": "#dde2df",
    "#252d32": "#dfe5e2",
    "#252e33": "#e1e7e4",
    "#252f34": "#dce3df",
    "#293238": "#cbd4cf",
    "#2c373e": "#d5dcd8",
    "#2e383e": "#c8d1cc",
    "#303a3f": "#cbd4cf",
    "#303b41": "#cbd4cf",
    "#343d42": "#c1cbc6",
    "#354047": "#c1cbc6",
    "#39434a": "#b9c3be",
    "#39454b": "#aeb9b3",
    "#536168": "#818c86",
    "#6f787d": "#929c97",
    "#7e8a90": "#69756f",
    "#879197": "#717d77",
    "#89939a": "#69756f",
    "#89949b": "#69756f",
    "#929a9e": "#66716b",
    "#9aa5ab": "#68746e",
    "#9ca7ac": "#68746e",
    "#aab4ba": "#55615b",
    "#aaaaaa": "#626d67",
    "#c5cdd1": "#414b45",
    "#c7d0d4": "#414b45",
    "#c9d1d9": "#3e4842",
    "#cbd2d6": "#414b45",
    "#d1d7da": "#39443e",
    "#d5dbde": "#37423c",
    "#d7dddf": "#37423c",
    "#e5e9eb": "#303b35",
    "#e7eaec": "#303b35",
    "#f2f2f2": "#252d28",
    "#f2f4f5": "#252d28",
    "#e8edef": "#303b35",
    "rgba(20, 24, 28, 225)": "rgba(248, 249, 248, 235)",
    "white": "#252d28",
    "#ffffff": "#202722",
}

LIGHT_TO_DARK = {
    light: dark
    for dark, light in DARK_TO_LIGHT.items()
    if light not in {
        "#55615b",
    }
}

CURRENT_THEME = "dark"


def _replace_colors(stylesheet, replacements):
    if not stylesheet:
        return stylesheet
    non_hex = {
        color: f"__TV_COLOR_{index}__"
        for index, color in enumerate(replacements)
        if not color.startswith("#")
    }
    for color, token in non_hex.items():
        stylesheet = stylesheet.replace(color, token)

    def replace_match(match):
        color = match.group(0).lower()
        if color in replacements:
            return replacements[color]
        if replacements is not DARK_TO_LIGHT:
            return color
        red, green, blue = (
            int(color[index:index + 2], 16) / 255
            for index in (1, 3, 5)
        )
        hue, lightness, saturation = colorsys.rgb_to_hls(
            red,
            green,
            blue,
        )
        if saturation > 0.68:
            return color
        if lightness < 0.30:
            lightness = 0.92
        elif lightness > 0.76:
            lightness = 0.23
        else:
            lightness = 0.35 if lightness > 0.50 else 0.72
        red, green, blue = colorsys.hls_to_rgb(hue, lightness, saturation)
        return "#{:02x}{:02x}{:02x}".format(
            round(red * 255),
            round(green * 255),
            round(blue * 255),
        )

    stylesheet = re.sub(r"#[0-9a-fA-F]{6}", replace_match, stylesheet)
    for color, token in non_hex.items():
        stylesheet = stylesheet.replace(token, replacements[color])
    return stylesheet


def apply_theme(root, theme, source_theme=None):
    global CURRENT_THEME
    if theme not in ("dark", "light"):
        raise ValueError(f"Tema desconocido: {theme}")
    source_theme = source_theme or CURRENT_THEME
    if source_theme not in ("dark", "light"):
        raise ValueError(f"Tema desconocido: {source_theme}")
    widgets = [root, *root.findChildren(QWidget)]
    dark_stylesheets = {}
    for widget in widgets:
        dark_stylesheet = widget.property("_tativision_dark_stylesheet")
        if dark_stylesheet is None:
            dark_stylesheet = widget.styleSheet()
            if source_theme == "light":
                dark_stylesheet = _replace_colors(
                    dark_stylesheet,
                    LIGHT_TO_DARK,
                )
            widget.setProperty(
                "_tativision_dark_stylesheet",
                dark_stylesheet,
            )
        dark_stylesheets[widget] = dark_stylesheet

    for widget in widgets:
        dark_stylesheet = dark_stylesheets[widget]
        widget.setStyleSheet(
            dark_stylesheet
            if theme == "dark"
            else _replace_colors(dark_stylesheet, DARK_TO_LIGHT)
        )

    for widget in widgets:
        color_theme_handler = getattr(widget, "apply_color_theme", None)
        if callable(color_theme_handler):
            color_theme_handler(theme)
    CURRENT_THEME = theme


def get_current_theme():
    return CURRENT_THEME
