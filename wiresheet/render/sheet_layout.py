"""Impaginazione dei cavi su fogli verticali con cornice e cartiglio."""

from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QPainter

from wiresheet.model import Cable, Project
from wiresheet.render.cable_drawer import CABLE_WIDTH, cable_size, draw_cable
from wiresheet.render.symbols import pen, text, text_width

PAGE_SIZES = {"A3": (297.0, 420.0), "A4": (210.0, 297.0)}  # verticale, mm
FRAME_MARGIN = 10.0
TB_ROW = 9.0         # cartiglio in basso a destra: TB_ROWS righe alte TB_ROW
TB_ROWS = 3
TB_CAPTION = 1.8     # didascalia in alto a sinistra di ogni casella
TB_VALUE = 3.5       # valore; si riduce se non sta nella casella
TB_WIDTH = 0.5       # larghezza del cartiglio, frazione della cornice (in basso a destra)
PAD = 10.0       # spazio tra la cornice (e il cartiglio) e cavi e tabelle, su ogni lato
GAP = 8.0        # spazio verticale tra due cavi
COLUMNS = 1      # colonne per foglio; i cavi si ingrandiscono per riempire la colonna


@dataclass
class Placement:
    cable: Cable
    x: float
    y: float
    scale: float = 1.0  # il cavo e' disegnato in mm e poi ingrandito di questo fattore


@dataclass
class SheetGeometry:
    width: float
    height: float
    frame: QRectF
    content: QRectF
    columns: int

    @property
    def column_width(self) -> float:
        return self.frame.width() / self.columns

    @property
    def scale(self) -> float:
        """Ingrandimento dei cavi: la larghezza del cavo riempie la colonna."""
        return (self.column_width - 2 * PAD) / CABLE_WIDTH


def sheet_geometry(page: str = "A3") -> SheetGeometry:
    w, h = PAGE_SIZES[page]
    frame = QRectF(FRAME_MARGIN, FRAME_MARGIN, w - 2 * FRAME_MARGIN, h - 2 * FRAME_MARGIN)
    content = frame.adjusted(0, PAD, 0, -(TB_ROWS * TB_ROW + PAD))
    return SheetGeometry(w, h, frame, content, COLUMNS)


def layout_pages(cables: list[Cable], geometry: SheetGeometry) -> list[list[Placement]]:
    """Riempie le colonne dall'alto verso il basso; a foglio pieno ne apre uno nuovo."""
    pages: list[list[Placement]] = [[]]
    column = 0
    y = geometry.content.top()
    for cable in cables:
        size = cable_size(cable)
        # riempie la larghezza della colonna, ma un cavo molto alto deve stare nel foglio
        scale = min(geometry.scale, geometry.content.height() / size.height())
        size = size * scale
        if y > geometry.content.top() and y + size.height() > geometry.content.bottom():
            column += 1
            y = geometry.content.top()
            if column == geometry.columns:
                pages.append([])
                column = 0
        col_left = geometry.frame.left() + column * geometry.column_width
        x = col_left + (geometry.column_width - size.width()) / 2
        pages[-1].append(Placement(cable, x, y, scale))
        y += size.height() + GAP
    return pages


def title_block_rows(project: Project, page: int, pages: int) -> list[list[tuple[str, float, str]]]:
    """Caselle del cartiglio, riga per riga: (didascalia, frazione della larghezza, valore)."""
    return [
        [("TITLE", 1.0, project.title)],
        [("COMPANY", 0.5, project.company), ("PROJECT", 0.5, project.machine)],
        [("DRAWN BY", 0.35, project.drawn_by), ("DATE", 0.25, project.date),
         ("REV", 0.15, str(project.revision)), ("PAGE", 0.25, f"{page}/{pages}")],
    ]


def _draw_title_block(p: QPainter, project: Project, frame: QRectF, page: int, pages: int) -> None:
    top = frame.bottom() - TB_ROWS * TB_ROW
    p.setPen(pen(0.5))
    p.setBrush(Qt.BrushStyle.NoBrush)
    width = frame.width() * TB_WIDTH
    left = frame.right() - width
    p.drawRect(QRectF(left, top, width, TB_ROWS * TB_ROW))
    for r, cells in enumerate(title_block_rows(project, page, pages)):
        y = top + r * TB_ROW
        x = left
        for caption, fraction, value in cells:
            cell = QRectF(x, y, width * fraction, TB_ROW)
            p.setPen(pen(0.25))
            p.drawRect(cell)
            text(p, cell.left() + 1.0, cell.top() + 1.6, caption, TB_CAPTION)
            if value:
                room = cell.width() - 3.0
                size = min(TB_VALUE, TB_VALUE * room / text_width(p, value, TB_VALUE, bold=True))
                text(p, cell.left() + 1.5, cell.top() + 5.8, value, size, bold=True)
            x = cell.right()


def draw_page(p: QPainter, project: Project, placements: list[Placement],
              geometry: SheetGeometry, page: int = 1, pages: int = 1) -> None:
    frame = geometry.frame
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.setPen(pen(0.6))
    p.drawRect(frame)

    p.setPen(pen(0.25))
    for i in range(1, geometry.columns):
        x = frame.left() + i * geometry.column_width
        p.drawLine(QPointF(x, frame.top()), QPointF(x, frame.bottom()))

    _draw_title_block(p, project, frame, page, pages)

    for item in placements:
        p.save()
        p.translate(item.x, item.y)
        p.scale(item.scale, item.scale)
        draw_cable(p, item.cable, 0, 0)
        p.restore()
