"""Primitive di disegno e simboli delle estremita'.

Tutte le coordinate sono in mm. `outward` vale -1 se il simbolo si sviluppa
verso sinistra (estremita' P1) e +1 se verso destra (estremita' P2).

La geometria dei simboli e' quella dei disegni in drawings/ (gen_*.py): ogni
simbolo e' descritto in coordinate locali, con la faccia di accoppiamento (o la
punta del terminale) in x = 0 e il lato filo in x = L, poi scalato e ribaltato
da `_local()` cosi' che il lato filo cada su `face_x`.
"""

from contextlib import contextmanager

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QFont, QFontMetricsF, QPainter, QPainterPath, QPen, QPolygonF

from wiresheet.components import EndKind

INK = QColor(0, 0, 0)
WHITE = QColor(255, 255, 255)
HOUSING_FILL = QColor(245, 245, 245)
SHADE_FILL = QColor(220, 220, 220)
METAL_FILL = QColor(230, 230, 230)

TERMINAL_H = 2.5  # altezza massima dei terminali per filo (puntalino, forcella, faston)
STRIP_LEN, STRIP_H = 4.0, 0.6  # taglio netto: conduttore esposto (il filo isolato e' alto 0.9)

# JST XH: housing XHP, passo 2.5, lunghezza 6.9 + collarino 0.85 sul lato fili
XH_PITCH, XH_LEN, XH_FLANGE = 2.5, 6.9, 0.85
# morsettiera a innesto passo 5.08: innesto 7.3 + corpo con viti 7.6
TB_PITCH, TB_NOSE, TB_BODY = 5.08, 7.3, 7.6
# GM a pannello: (d flangia, sporgenza davanti al pannello, lunghezza totale, d filetto)
GM_DIMS = {
    EndKind.GM1312: (19.5, 10.0, 23.0, 13.0),
    EndKind.GM1712: (25.0, 12.2, 27.0, 17.0),
    EndKind.GM2112: (29.0, 13.3, 27.0, 21.0),
}
GM_SCALE = 0.55   # i GM non seguono il passo delle righe: scala fissa
GM_FAN = 6.0      # tratto in cui i fili convergono sui contatti a saldare


def pen(width: float = 0.25, color: QColor = INK) -> QPen:
    p = QPen(color)
    p.setWidthF(width)
    p.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
    p.setCapStyle(Qt.PenCapStyle.FlatCap)
    return p


def set_font(p: QPainter, size_mm: float, bold: bool = False, italic: bool = False) -> None:
    """Imposta un font alto circa `size_mm` nel sistema di coordinate in mm."""
    f = QFont("Arial")
    f.setPointSizeF(size_mm * 72.0 / p.device().logicalDpiY())
    f.setBold(bold)
    f.setItalic(italic)
    f.setHintingPreference(QFont.HintingPreference.PreferNoHinting)
    p.setFont(f)


def text_width(p: QPainter, s: str, size: float, bold: bool = False, italic: bool = False) -> float:
    """Larghezza in mm di `s` scritto con text()."""
    set_font(p, size, bold, italic)
    return QFontMetricsF(p.font(), p.device()).horizontalAdvance(s)


def text(p: QPainter, x: float, y: float, s: str, size: float,
         align: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft, bold: bool = False,
         italic: bool = False) -> None:
    """Scrive `s` centrato verticalmente su y; x e' il bordo indicato da `align`."""
    set_font(p, size, bold, italic)
    box = 200.0
    if align & Qt.AlignmentFlag.AlignRight:
        rect = QRectF(x - box, y - size, box, 2 * size)
    elif align & Qt.AlignmentFlag.AlignHCenter:
        rect = QRectF(x - box / 2, y - size, box, 2 * size)
    else:
        rect = QRectF(x, y - size, box, 2 * size)
    p.setPen(pen())
    p.drawText(rect, align | Qt.AlignmentFlag.AlignVCenter, s)


def _span_rect(x: float, length: float, outward: int, cy: float, height: float) -> QRectF:
    """Rettangolo che parte da x e si estende di `length` nella direzione `outward`."""
    x0 = x if outward > 0 else x - length
    return QRectF(x0, cy - height / 2, length, height)


# --- disegno in coordinate locali -----------------------------------------------------

class _Local:
    """Primitive con spessori in mm reali dentro un sistema scalato di `k`."""

    def __init__(self, p: QPainter, k: float):
        self.p, self.k = p, k

    def _style(self, fill, width):
        self.p.setPen(pen(width / self.k))
        self.p.setBrush(fill if fill is not None else Qt.BrushStyle.NoBrush)

    def rect(self, x, y, w, h, fill=HOUSING_FILL, width=0.2, radius=0.0):
        self._style(fill, width)
        if radius:
            self.p.drawRoundedRect(QRectF(x, y, w, h), radius, radius)
        else:
            self.p.drawRect(QRectF(x, y, w, h))

    def line(self, x1, y1, x2, y2, width=0.12):
        self._style(None, width)
        self.p.drawLine(QPointF(x1, y1), QPointF(x2, y2))

    def circle(self, cx, cy, r, fill, width=0.15):
        self._style(fill, width)
        self.p.drawEllipse(QPointF(cx, cy), r, r)

    def poly(self, pts, fill, width=0.2):
        self._style(fill, width)
        self.p.drawPolygon(QPolygonF([QPointF(x, y) for x, y in pts]))

    def path(self, path: QPainterPath, fill, width=0.2):
        self._style(fill, width)
        self.p.drawPath(path)


@contextmanager
def _local(p: QPainter, face_x: float, y0: float, length: float, k: float, outward: int):
    """Sistema locale: x = 0 lato esterno, x = `length` lato filo (su face_x), y verso il basso."""
    p.save()
    p.translate(face_x, y0)
    p.scale(-outward * k, k)
    p.translate(-length, 0)
    try:
        yield _Local(p, k)
    finally:
        p.restore()


def _sleeve(d: _Local, x0: float, x1: float, r0: float, r1: float, rim: float) -> None:
    """Isolante a manicotto con imbocco svasato (forcella, faston)."""
    k = x0 + (x1 - x0) * 0.55
    path = QPainterPath(QPointF(x0, -r0))
    path.lineTo(k, -r0)
    path.quadTo(x1 - rim, -r0, x1 - rim, -r1)
    path.lineTo(x1, -r1)
    path.lineTo(x1, r1)
    path.lineTo(x1 - rim, r1)
    path.quadTo(x1 - rim, r0, k, r0)
    path.lineTo(x0, r0)
    path.closeSubpath()
    d.path(path, HOUSING_FILL)
    d.line(x1 - rim, -r1, x1 - rim, r1, 0.1)


# --- connettori -------------------------------------------------------------------------

def _xh_scale(row: float) -> float:
    return row / XH_PITCH


def draw_jst_xh(p: QPainter, face_x: float, top: float, positions: int,
                row: float, outward: int) -> float:
    """JST XHP visto dal lato aggancio: finestre dei contatti verso l'esterno,
    collarino sul lato fili. Restituisce la x del lato esterno."""
    k = _xh_scale(row)
    b = XH_PITCH * (positions - 1) + 4.8
    off = 2.4  # dal bordo del housing al centro del primo alloggiamento
    length = XH_LEN + XH_FLANGE
    with _local(p, face_x, top + row / 2 - k * off, length, k, outward) as d:
        d.rect(0, 0.3, XH_LEN, b - 0.6, HOUSING_FILL)
        d.line(0, 1.0, XH_LEN, 1.0)
        d.line(0, b - 1.0, XH_LEN, b - 1.0)
        for j in range(positions):
            cy = off + j * XH_PITCH
            d.rect(0.5, cy - 0.6, 2.2, 1.2, WHITE, 0.12)
            d.poly([(2.7, cy - 0.6), (1.7, cy), (2.7, cy + 0.6)], SHADE_FILL, 0.08)
        d.rect(XH_LEN, 0, XH_FLANGE, b, SHADE_FILL)
    return face_x + outward * length * k


def draw_terminal_block(p: QPainter, face_x: float, top: float, positions: int,
                        row: float, outward: int) -> float:
    """Morsettiera a innesto vista dal lato viti: innesto verso l'esterno, corpo con
    viti e fori di sblocco sul lato fili. Restituisce la x del lato esterno."""
    k = row / TB_PITCH
    w = positions * TB_PITCH
    length = TB_NOSE + TB_BODY
    with _local(p, face_x, top, length, k, outward) as d:
        d.rect(0, 0, TB_NOSE, w, SHADE_FILL)
        d.rect(TB_NOSE, 0, TB_BODY, w, HOUSING_FILL)
        for j in range(positions):
            cy = (j + 0.5) * TB_PITCH
            d.rect(0, cy - 2.0, TB_NOSE - 0.6, 4.0, HOUSING_FILL, 0.12, 0.8)
            sx = TB_NOSE + 3.0
            d.circle(sx, cy, 1.8, WHITE)
            d.circle(sx, cy, 1.3, METAL_FILL, 0.1)
            d.line(sx + 0.65, cy - 1.126, sx - 0.65, cy + 1.126, 0.25)  # taglio a 30 gradi
            d.rect(TB_NOSE + 5.8, cy - 0.75, 0.75, 1.5, WHITE, 0.12)
    return face_x + outward * length * k


def gm_contact_offsets(kind: EndKind, positions: int, row: float) -> list[float]:
    """Quota dei contatti a saldare di un GM rispetto al centro delle righe, dalla
    riga in alto a quella in basso: i fili convergono qui."""
    flange = GM_DIMS[kind][0]
    span = 0.52 * flange * GM_SCALE  # altezza utile dell'isolante posteriore
    step = row if positions < 2 else min(row, span / (positions - 1))
    return [(j - (positions - 1) / 2) * step for j in range(positions)]


def draw_gm_panel(p: QPainter, kind: EndKind, face_x: float, top: float, positions: int,
                  row: float, outward: int) -> float:
    """Presa GM a pannello con dado posteriore, vista di lato: filetto di accoppiamento
    verso l'esterno, flangia, dado, isolante e contatti a saldare sul lato fili.
    Restituisce la x del lato esterno."""
    F, a, T, M = GM_DIMS[kind]
    k = GM_SCALE
    r = T - a
    offsets = gm_contact_offsets(kind, positions, row)
    cup_h = min(0.9, (abs(offsets[1] - offsets[0]) if positions > 1 else row) * 0.7) / k
    with _local(p, face_x, top + positions * row / 2, T, k, outward) as d:
        def band(u0, u1, dia, fill=HOUSING_FILL):
            d.rect(u0, -dia / 2, u1 - u0, dia, fill)

        band(0.0, 0.42 * a, 0.74 * F)                                   # filetto anteriore
        for i in range(1, 6):
            u = 0.42 * a * i / 6
            d.line(u, -0.37 * F, u, 0.37 * F, 0.08)
        band(0.42 * a, 0.85 * a, 0.80 * F)                              # corpo
        d.rect(0.5 * a, -0.40 * F - 0.6, 0.3 * a, 0.6, SHADE_FILL, 0.12)   # chiave
        band(0.85 * a, a, F, SHADE_FILL)                                # flangia
        band(a, a + 0.55 * r, M)                                        # filetto posteriore
        for i in range(1, 8):
            u = a + 0.55 * r * i / 8
            d.line(u, -M / 2, u, M / 2, 0.08)
        band(a + 0.18 * r, a + 0.40 * r, 0.95 * F)                      # dado esagonale
        for v in (-0.25, 0.25):
            d.line(a + 0.18 * r, v * F, a + 0.40 * r, v * F, 0.1)
        x1, x2, h = a + 0.55 * r, a + 0.78 * r, 0.30 * F                # isolante posteriore
        path = QPainterPath(QPointF(x1, -h))
        path.lineTo(x2 - 1.0, -h)
        path.quadTo(x2, -h, x2, -h + 1.0)
        path.lineTo(x2, h - 1.0)
        path.quadTo(x2, h, x2 - 1.0, h)
        path.lineTo(x1, h)
        path.closeSubpath()
        d.path(path, HOUSING_FILL)
        for off in offsets:                                             # contatti a saldare
            d.rect(x2, off / k - cup_h / 2, T - x2, cup_h, METAL_FILL, 0.1)
    return face_x + outward * T * k


def connector_body(kind: EndKind, row: float = 3.0) -> float:
    """Larghezza del corpo del connettore, in mm."""
    if kind is EndKind.JST_XH:
        return (XH_LEN + XH_FLANGE) * _xh_scale(row)
    if kind is EndKind.TERMINAL_BLOCK:
        return (TB_NOSE + TB_BODY) * row / TB_PITCH
    return GM_DIMS[kind][2] * GM_SCALE


def connector_height(kind: EndKind, positions: int, row: float = 3.0) -> float:
    """Altezza del corpo del connettore, in mm (centrato sulle righe dei pin)."""
    if kind is EndKind.JST_XH:
        return (XH_PITCH * (positions - 1) + 4.8) * _xh_scale(row)
    if kind is EndKind.TERMINAL_BLOCK:
        return positions * row
    return GM_DIMS[kind][0] * GM_SCALE


def contact_offsets(kind: EndKind, positions: int, row: float) -> list[float]:
    """Quota del punto in cui arriva ogni filo, rispetto al centro delle righe."""
    if kind in GM_DIMS:
        return gm_contact_offsets(kind, positions, row)
    return [(j + 0.5 - positions / 2) * row for j in range(positions)]


def draw_connector(p: QPainter, kind: EndKind, face_x: float, top: float, positions: int,
                   row: float, outward: int) -> float:
    """Corpo di un connettore. Restituisce la x del lato esterno."""
    if kind is EndKind.JST_XH:
        return draw_jst_xh(p, face_x, top, positions, row, outward)
    if kind is EndKind.TERMINAL_BLOCK:
        return draw_terminal_block(p, face_x, top, positions, row, outward)
    return draw_gm_panel(p, kind, face_x, top, positions, row, outward)


# --- terminali per filo -----------------------------------------------------------------

def draw_ferrule(p: QPainter, face_x: float, cy: float, outward: int) -> float:
    """Puntalino: tubetto metallico + collare isolante. Restituisce la x della punta."""
    length, k = 15.0, TERMINAL_H / 3.5
    with _local(p, face_x, cy, length, k, outward) as d:
        d.rect(0, -0.65, 8.0, 1.3, METAL_FILL)
        d.poly([(8, -0.65), (9, -1.5), (14.2, -1.5), (14.4, -1.75), (15, -1.75), (15, 1.75),
                (14.4, 1.75), (14.2, 1.5), (9, 1.5), (8, 0.65)], HOUSING_FILL)
        d.line(14.4, -1.75, 14.4, 1.75, 0.1)
    return face_x + outward * length * k


def draw_fork(p: QPainter, face_x: float, cy: float, outward: int) -> float:
    """Forcella isolata: linguetta con fessura + isolante. Restituisce la x della punta."""
    length, k = 21.0, TERMINAL_H / 6.4
    hw, sw, tip, slot_end, neck = 3.2, 1.85, 0.8, 6.0, 9.5
    with _local(p, face_x, cy, length, k, outward) as d:
        path = QPainterPath(QPointF(tip, -hw))
        for x, y in ((neck, -hw), (11, -1.0), (11, 1.0), (neck, hw), (tip, hw),
                     (0, hw - tip), (0, sw), (slot_end - sw, sw)):
            path.lineTo(x, y)
        path.quadTo(slot_end, sw, slot_end, 0)
        path.quadTo(slot_end, -sw, slot_end - sw, -sw)
        path.lineTo(0, -sw)
        path.lineTo(0, -hw + tip)
        path.closeSubpath()
        d.path(path, METAL_FILL)
        _sleeve(d, 11, 21, 1.5, 1.75, 0.6)
    return face_x + outward * length * k


def draw_faston_f(p: QPainter, face_x: float, cy: float, outward: int) -> float:
    """Faston femmina 6.3 isolato: bordi arrotolati, collo, isolante. Restituisce la x della punta."""
    length, k = 20.0, TERMINAL_H / 7.6
    hw, roll, body = 3.8, 2.0, 10.0
    with _local(p, face_x, cy, length, k, outward) as d:
        d.rect(0.4, -hw + roll, body - 0.4, 2 * (hw - roll), SHADE_FILL, 0.12)
        d.line(4.0, -0.6, 6.0, -0.6, 0.1)
        d.line(4.0, 0.6, 6.0, 0.6, 0.1)
        d.line(6.0, -0.6, 6.0, 0.6, 0.1)
        for y in (-hw, hw - roll):
            path = QPainterPath(QPointF(roll / 2, y))
            path.lineTo(body, y)
            path.lineTo(body, y + roll)
            path.lineTo(roll / 2, y + roll)
            path.quadTo(0, y + roll, 0, y + roll / 2)
            path.quadTo(0, y, roll / 2, y)
            d.path(path, METAL_FILL)
        d.poly([(body, -hw), (11.5, -1.2), (11.5, 1.2), (body, hw)], METAL_FILL)
        _sleeve(d, 11.5, 20, 1.9, 2.1, 0.6)
        d.line(12.0, -1.9, 12.0, 1.9, 0.1)
    return face_x + outward * length * k


def draw_flat_cut(p: QPainter, face_x: float, cy: float, outward: int) -> float:
    """Taglio netto: il conduttore esposto oltre l'isolante, piu' sottile del filo.
    Restituisce la x della punta."""
    p.setPen(pen(0.12))
    p.setBrush(METAL_FILL)
    p.drawRect(_span_rect(face_x, STRIP_LEN, outward, cy, STRIP_H))
    return face_x + outward * STRIP_LEN


TERMINALS = {
    EndKind.FERRULE: draw_ferrule,
    EndKind.FORK: draw_fork,
    EndKind.FASTON_F: draw_faston_f,
    EndKind.FLAT_CUT: draw_flat_cut,
}
