from PySide6.QtCore import QEvent, QRectF, QTimer, Qt
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class LoadingOverlay(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_OpaquePaintEvent, True)
        self._background_color = QColor("#101417")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        layout.addStretch()

        self.spinner = Spinner(self)
        layout.addWidget(self.spinner, alignment=Qt.AlignCenter)

        label = QLabel("Actualizando vista…", self)
        label.setStyleSheet(
            "background: transparent; color: #e5e9eb; font-size: 13px;"
        )
        layout.addWidget(label, alignment=Qt.AlignCenter)
        layout.addStretch()
        self._geometry_parent = None

    def attach_to(self, parent):
        if self._geometry_parent is not None:
            self._geometry_parent.removeEventFilter(self)
        self.setParent(parent)
        self._geometry_parent = parent
        parent.installEventFilter(self)
        self.setGeometry(parent.rect())

    def eventFilter(self, watched, event):
        if (
            watched is self._geometry_parent
            and event.type() == QEvent.Resize
        ):
            self.setGeometry(watched.rect())
        return super().eventFilter(watched, event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), self._background_color)


class Spinner(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(38, 38)
        self._angle = 0
        self._timer = QTimer(self)
        self._timer.setInterval(35)
        self._timer.timeout.connect(self._advance)

    def showEvent(self, event):
        super().showEvent(event)
        self._timer.start()

    def hideEvent(self, event):
        self._timer.stop()
        super().hideEvent(event)

    def _advance(self):
        self._angle = (self._angle + 30) % 360
        self.update()

    def paintEvent(self, _event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor("#00c94b"), 3)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        painter.drawArc(
            QRectF(3, 3, 32, 32),
            self._angle * 16,
            270 * 16,
        )
