from PySide6.QtCore import (
    QEasingCurve,
    QPointF,
    QRectF,
    Qt,
    QVariantAnimation,
)
from PySide6.QtGui import QColor, QPainter, QPen
from PySide6.QtWidgets import QPushButton


class DetailBackButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(36, 36)
        self.setCursor(Qt.PointingHandCursor)
        self.setFocusPolicy(Qt.NoFocus)
        self._hover_progress = 0.0
        self._hover_animation = QVariantAnimation(self)
        self._hover_animation.setDuration(200)
        self._hover_animation.setEasingCurve(QEasingCurve.OutCubic)
        self._hover_animation.setStartValue(0.0)
        self._hover_animation.setEndValue(1.0)
        self._hover_animation.valueChanged.connect(self._set_hover_progress)

    def enterEvent(self, event):
        self._hover_animation.setDirection(QVariantAnimation.Forward)
        self._hover_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hover_animation.setDirection(QVariantAnimation.Backward)
        self._hover_animation.start()
        super().leaveEvent(event)

    def _set_hover_progress(self, progress):
        self._hover_progress = float(progress)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = QRectF(self.rect()).adjusted(1, 1, -1, -1)
        painter.setBrush(QColor("#252d32"))
        painter.setPen(
            QPen(
                self._interpolate_color("#39434a", "#00e054"),
                1.4,
            )
        )
        painter.drawEllipse(rect)

        center = rect.center()
        painter.setPen(
            QPen(
                self._interpolate_color("#f2f4f5", "#00e054"),
                1.8,
                Qt.SolidLine,
                Qt.RoundCap,
                Qt.RoundJoin,
            )
        )
        painter.drawLine(
            QPointF(center.x() + 5, center.y()),
            QPointF(center.x() - 5, center.y()),
        )
        painter.drawLine(
            QPointF(center.x() - 5, center.y()),
            QPointF(center.x() + 1, center.y() - 6),
        )
        painter.drawLine(
            QPointF(center.x() - 5, center.y()),
            QPointF(center.x() + 1, center.y() + 6),
        )

    def _interpolate_color(self, start, end):
        start_color = QColor(start)
        end_color = QColor(end)
        progress = self._hover_progress
        return QColor.fromRgbF(
            start_color.redF() + (end_color.redF() - start_color.redF()) * progress,
            start_color.greenF() + (end_color.greenF() - start_color.greenF()) * progress,
            start_color.blueF() + (end_color.blueF() - start_color.blueF()) * progress,
        )
