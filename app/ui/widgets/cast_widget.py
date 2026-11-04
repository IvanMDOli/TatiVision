import json

from PySide6.QtCore import QRect, QSize, Qt
from PySide6.QtGui import QFont, QFontMetrics
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLayout, QLabel, QWidget

from app.ui.theme import apply_theme, get_current_theme


class FlowLayout(QLayout):
    def __init__(self, parent=None, horizontal_spacing=4, vertical_spacing=4):
        super().__init__(parent)
        self._items = []
        self._horizontal_spacing = horizontal_spacing
        self._vertical_spacing = vertical_spacing
        self.setContentsMargins(0, 0, 0, 0)

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientations(Qt.Orientation(0))

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        return self._do_layout(QRect(0, 0, width, 0), True)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        margins = self.contentsMargins()
        size += QSize(
            margins.left() + margins.right(),
            margins.top() + margins.bottom(),
        )
        return size

    def setGeometry(self, rect):
        super().setGeometry(rect)
        self._do_layout(rect, False)

    def _do_layout(self, rect, test_only):
        margins = self.contentsMargins()
        effective = rect.adjusted(
            margins.left(),
            margins.top(),
            -margins.right(),
            -margins.bottom(),
        )
        x = effective.x()
        y = effective.y()
        line_height = 0

        for item in self._items:
            hint = item.sizeHint()
            next_x = x + hint.width() + self._horizontal_spacing
            if line_height and next_x - self._horizontal_spacing > effective.right() + 1:
                x = effective.x()
                y += line_height + self._vertical_spacing
                next_x = x + hint.width() + self._horizontal_spacing
                line_height = 0

            if not test_only:
                item.setGeometry(
                    QRect(x, y, hint.width(), hint.height())
                )
            x = next_x
            line_height = max(line_height, hint.height())

        margins_height = margins.top() + margins.bottom()
        return y + line_height + margins_height - rect.y()


class CastWidget(QWidget):
    def __init__(self, cast_members, parent=None):
        super().__init__(parent)
        self.flow_layout = FlowLayout(self, horizontal_spacing=4, vertical_spacing=4)
        self.member_cards = []

        for member in self._normalize_cast(cast_members):
            name = member.get("name")
            if not name:
                continue

            character = (member.get("character") or "").strip()
            card = QFrame()
            card.setObjectName("castMember")
            card.setFixedHeight(25)
            card.setToolTip(character)

            name_label = QLabel(name, card)
            name_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
            font = name_label.font()
            font.setPointSize(10)
            font.setWeight(QFont.DemiBold)
            name_label.setFont(font)
            metrics = QFontMetrics(font)
            text_width = min(metrics.horizontalAdvance(name), 240)
            name_label.setText(metrics.elidedText(name, Qt.ElideRight, text_width))
            name_label.setFixedSize(text_width, 23)
            name_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            chip_layout = QHBoxLayout(card)
            chip_layout.setContentsMargins(8, 0, 8, 0)
            chip_layout.setSpacing(0)
            chip_layout.addWidget(name_label)
            card.setFixedWidth(text_width + 16)
            self.flow_layout.addWidget(card)
            self.member_cards.append(card)

        if not self.member_cards:
            empty = QLabel("No hay información del reparto disponible.")
            empty.setObjectName("castEmpty")
            self.flow_layout.addWidget(empty)

        apply_theme(self, get_current_theme(), source_theme="dark")
        self.apply_color_theme(get_current_theme())

    def apply_color_theme(self, theme):
        for card in self.member_cards:
            card.setStyleSheet("""
                QFrame#castMember {
                    background-color: #292f34;
                    border: 1px solid #414a50;
                    border-radius: 2px;
                }
                QFrame#castMember:hover {
                    border-color: #00a847;
                    background-color: #252f34;
                }
            """)
            label = card.findChild(QLabel)
            if label:
                label.setStyleSheet(
                    "border: none; background: transparent; color: #BCBCBC;"
                )

    @staticmethod
    def _normalize_cast(cast_members):
        if not cast_members:
            return []
        if isinstance(cast_members, str):
            try:
                cast_members = json.loads(cast_members)
            except json.JSONDecodeError:
                return []
        if not isinstance(cast_members, list):
            return []
        return [member for member in cast_members if isinstance(member, dict)]
