"""Widget che non rubano la rotella del mouse alla pila di card.

Scorrendo la pagina, la rotella non deve cambiare il valore della tendina
o del numero che si trova sotto il cursore: lo fa solo se il widget ha il focus.
"""

from PySide6.QtCore import QPointF, QRectF, QSize, Qt
from PySide6.QtGui import QColor, QFont, QPainter, QPainterPath
from PySide6.QtWidgets import (QAbstractButton, QComboBox, QDoubleSpinBox, QSpinBox,
                               QTableWidget, QWidget)

from wiresheet.components import CONNECTOR_KINDS, GM_LAYOUTS, EndKind
from wiresheet.render.symbols import (TERMINALS, connector_body, connector_height,
                                     contact_offsets, draw_connector, pen)
from wiresheet.ui.icons import icon
from wiresheet.ui.style import ACCENT


class NoWheelComboBox(QComboBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event):
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()


class NoWheelSpinBox(QSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event):
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()


class NoWheelDoubleSpinBox(QDoubleSpinBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def wheelEvent(self, event):
        if self.hasFocus():
            super().wheelEvent(event)
        else:
            event.ignore()


class FixedHeightTable(QTableWidget):
    """Tabella alta quanto le sue righe: niente scroll interno, la rotella scorre la pagina."""

    def __init__(self, rows: int, columns: int, parent=None):
        super().__init__(rows, columns, parent)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

    def fit_height(self) -> None:
        rows = sum(self.rowHeight(r) for r in range(self.rowCount()))
        header = self.horizontalHeader().sizeHint().height()
        self.setFixedHeight(header + rows + 2 * self.frameWidth())

    def wheelEvent(self, event):
        event.ignore()


class SideTab(QAbstractButton):
    """Linguetta verticale sul bordo destro, centrata, che apre/chiude un pannello."""

    WIDTH, HEIGHT = 30, 150

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.setText(text)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(self.WIDTH, self.HEIGHT)
        self.setToolTip(f"Mostra / nascondi {text.lower()} (F2)")

    def sizeHint(self) -> QSize:
        return QSize(self.WIDTH, self.HEIGHT)

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        r = QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5)
        # linguetta con gli angoli arrotondati solo sul lato sinistro
        path = QPainterPath()
        radius = 8.0
        path.moveTo(r.right(), r.top())
        path.lineTo(r.left() + radius, r.top())
        path.quadTo(r.left(), r.top(), r.left(), r.top() + radius)
        path.lineTo(r.left(), r.bottom() - radius)
        path.quadTo(r.left(), r.bottom(), r.left() + radius, r.bottom())
        path.lineTo(r.right(), r.bottom())
        checked = self.isChecked()
        hover = self.underMouse()
        fill = QColor(ACCENT) if checked else QColor("#dfe7f7" if hover else "#e8ecf2")
        p.setPen(QColor(ACCENT) if (checked or hover) else QColor("#c4cad4"))
        p.setBrush(fill)
        p.drawPath(path)

        fg = "#ffffff" if checked else ACCENT
        arrow = icon("chevron-right" if checked else "chevron-left", fg)
        arrow.paint(p, int(r.center().x() - 8), 10, 16, 16)

        p.save()
        p.translate(r.center().x(), r.center().y() + 10)
        p.rotate(-90)
        font = QFont(self.font())
        font.setBold(True)
        font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 1.5)
        p.setFont(font)
        p.setPen(QColor(fg))
        p.drawText(QRectF(-60, -10, 120, 20), Qt.AlignmentFlag.AlignCenter, self.text().upper())
        p.restore()

    def enterEvent(self, event) -> None:
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.update()
        super().leaveEvent(event)


class EndThumbnail(QWidget):
    """Miniatura del componente di un'estremita' (stessi simboli del disegno)."""

    ROW = 3.0
    STUB = 9.0   # tratto di filo disegnato, in mm
    WIRES = 3    # fili mostrati per le estremita' per filo

    def __init__(self, outward: int, parent=None):
        super().__init__(parent)
        self._outward = outward  # -1: P1 (simbolo a sinistra), +1: P2 (simbolo a destra)
        self._kind = EndKind.JST_XH
        self._positions = 2
        self.setFixedSize(96, 44)

    def set_end(self, kind: EndKind, positions: int) -> None:
        self._kind, self._positions = kind, positions
        self.update()

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setPen(QColor("#d5d9e0"))
        p.setBrush(QColor("#fafbfc"))
        p.drawRoundedRect(QRectF(self.rect()).adjusted(0.5, 0.5, -0.5, -0.5), 4, 4)

        connector = self._kind in CONNECTOR_KINDS
        rows = self._positions if connector else self.WIRES
        symbol = connector_body(self._kind, self.ROW) if connector else 11.0
        body_h = connector_height(self._kind, rows, self.ROW) if connector else 0.0
        straight = self._kind in GM_LAYOUTS  # fili dritti sui contatti, senza le righe
        width_mm = symbol + self.STUB + 2
        height_mm = max(0 if straight else max(rows, 3) * self.ROW, body_h) + 2
        k = min((self.width() - 8) / width_mm, (self.height() - 8) / height_mm)
        p.translate(self.width() / 2, self.height() / 2)
        p.scale(k, k)

        out = self._outward
        face = out * (width_mm / 2 - symbol - 1)  # lato filo del simbolo
        top = -rows * self.ROW / 2
        wire_end = face - out * self.STUB
        contacts = (contact_offsets(self._kind, rows, self.ROW) if connector
                    else [(i + 0.5 - rows / 2) * self.ROW for i in range(rows)])
        p.setPen(pen(0.7, QColor(90, 96, 108)))
        for i, contact in enumerate(contacts):
            y = contact if straight else top + (i + 0.5) * self.ROW
            p.drawLine(QPointF(wire_end, y), QPointF(face, contact))
        if connector:
            draw_connector(p, self._kind, face, top, rows, self.ROW, out)
            return
        for i in range(rows):
            TERMINALS[self._kind](p, face, top + (i + 0.5) * self.ROW, out)
