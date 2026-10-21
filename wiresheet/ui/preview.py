"""Anteprima: un cavo (draw_cable) oppure un foglio intero (draw_page), come nel PDF."""

from PySide6.QtCore import QRectF, QSizeF, Qt
from PySide6.QtGui import QColor, QPainter, QWheelEvent
from PySide6.QtWidgets import QWidget

from wiresheet.model import Cable, Project
from wiresheet.render.cable_drawer import cable_size, draw_cable
from wiresheet.render.sheet_layout import Placement, SheetGeometry, draw_page

PAD = 6.0  # margine attorno al cavo, in mm
MIN_ZOOM, MAX_ZOOM = 0.2, 8.0


class CablePreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._cable: Cable | None = None
        # progetto, cavi del foglio, geometria, numero del foglio, fogli totali
        self._page: tuple[Project, list[Placement], SheetGeometry, int, int] | None = None
        self._message = ""
        self.zoom = 1.0

    def set_cable(self, cable: Cable | None, message: str = "") -> None:
        self._cable = cable
        self._page = None
        self._message = message
        self._update_size()
        self.update()

    def set_page(self, project: Project, placements: list[Placement],
                 geometry: SheetGeometry, page: int = 1, pages: int = 1) -> None:
        self._cable = None
        self._page = (project, placements, geometry, page, pages)
        self._message = ""
        self._update_size()
        self.update()

    def set_zoom(self, zoom: float) -> None:
        self.zoom = min(MAX_ZOOM, max(MIN_ZOOM, zoom))
        self._update_size()
        self.update()

    def fit_to(self, width_px: int, height_px: int) -> None:
        """Sceglie lo zoom che fa stare il contenuto nell'area indicata."""
        size = self._content_size()
        if size is None:
            return
        px_per_mm = self.logicalDpiX() / 25.4
        self.set_zoom(min(width_px / size.width(), height_px / size.height()) / px_per_mm)

    def _content_size(self) -> QSizeF | None:
        """Dimensione del contenuto in mm (margine compreso)."""
        if self._page is not None:
            geometry = self._page[2]
            return QSizeF(geometry.width, geometry.height)
        if self._cable is not None:
            s = cable_size(self._cable)
            return QSizeF(s.width() + 2 * PAD, s.height() + 2 * PAD)
        return None

    def _scale(self) -> float:
        """Pixel per mm (zoom 1 = dimensione reale sullo schermo)."""
        return self.zoom * self.logicalDpiX() / 25.4

    def _update_size(self) -> None:
        size = self._content_size()
        if size is None:
            self.setFixedSize(360, 160)
            return
        k = self._scale()
        self.setFixedSize(int(size.width() * k), int(size.height() * k))

    def paintEvent(self, event) -> None:
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(255, 255, 255))
        if self._cable is None and self._page is None:
            p.setPen(QColor(180, 0, 0))
            p.drawText(QRectF(self.rect()).adjusted(10, 10, -10, -10),
                       Qt.TextFlag.TextWordWrap, self._message)
            return
        k = self._scale()
        p.scale(k, k)
        if self._page is not None:
            draw_page(p, *self._page)
        else:
            draw_cable(p, self._cable, PAD, PAD)

    def wheelEvent(self, event: QWheelEvent) -> None:
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            self.set_zoom(self.zoom * 1.15 ** (event.angleDelta().y() / 120))
            event.accept()
        else:
            event.ignore()
