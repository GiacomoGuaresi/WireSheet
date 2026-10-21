"""Disegno di un cavo completo (coordinate in mm)."""

from dataclasses import dataclass

from PySide6.QtCore import QPointF, QRectF, QSizeF, Qt
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPolygonF

from wiresheet.colors import COLORS
from wiresheet.components import end_codes
from wiresheet.gauges import section_text
from wiresheet.model import Branch, Cable, End, Wire, branch_title
from wiresheet.render.symbols import (GM_FAN, INK, TERMINALS, WHITE, connector_height, contact_offsets,
                                     draw_connector, pen, text, text_width)

ROW = 3.0        # passo verticale tra i fili
SPAN = 80.0      # lunghezza disegnata dei fili (non in scala)
CROSS = 12.0     # tratto in cui i fili si incrociano, vicino a P2
SIDE = 22.0      # spazio laterale per simbolo e testi
CABLE_WIDTH = 2 * SIDE + SPAN
NAME_H = 6.0
LABEL_H = 9.0    # fascia sopra i fili per l'etichetta del cavo
CODES_H = 9.0
TABLE_ROW = 4.0
TABLE_FONT = 2.2      # WIRE LIST: si riduce fino a TABLE_MIN_FONT se le righe non ci stanno
TABLE_MIN_FONT = 1.4
CELL_PAD = 1.0        # margine a sinistra e a destra del testo in ogni cella
FONT = 2.2
CODE_LINE = 2.8
BRANCH_LABEL_H = 7.0  # riga con l'etichetta sopra ogni ramo
BRANCH_GAP = 3.0
NOT_CONNECTED = "nc"  # pin senza filo, scritto in corsivo
TAG_H = 3.6          # cartellino dell'etichetta, con il testo
SLEEVE_W = 2.5       # fascetta dell'etichetta attorno ai fili, con scritto LABEL in verticale
SLEEVE_TEXT = "LABEL"
SLEEVE_FONT = 1.2
TAG_OFFSET = 1.5     # il cartellino inizia poco prima della linea che lo collega
ARROW_L = 1.5        # freccia della linea tratteggiata, verso la fascetta
SLEEVE_INSET = 12.0  # distanza della fascetta dalla faccia dell'estremita'
WIRE_OUTLINE = 170     # contorno del filo: stesso colore, piu' scuro (QColor.darker, in %)
SPLIT = (0.3, 0.6)    # tratto (frazioni di SPAN) in cui i fili si spostano verso il loro ramo

_ALIGN_L = Qt.AlignmentFlag.AlignLeft
_ALIGN_R = Qt.AlignmentFlag.AlignRight
_ALIGN_C = Qt.AlignmentFlag.AlignHCenter


def _rows(cable: Cable) -> int:
    positions = [e.positions for e in (cable.p1, cable.p2) if e.is_connector]
    return max(positions) if positions else len(cable.wires)


def _pin_row(end: End, pin: int, outward: int = +1) -> int:
    """Riga (dall'alto) del pin di un connettore. A sinistra (P1) il pin 1 e' in basso;
    a destra (P2) il connettore e' ruotato di 180 gradi (non specchiato), quindi il pin 1
    e' in alto."""
    return end.positions - pin if outward < 0 else pin - 1


def _wire_rows(cable: Cable, index: int, wire: Wire) -> tuple[int, int]:
    """Righe del filo alle due estremita'. Un'estremita' senza connettore
    segue la riga del connettore opposto, cosi' il filo resta dritto."""
    r1 = _pin_row(cable.p1, wire.p1_pin, -1) if cable.p1.is_connector else None
    r2 = _pin_row(cable.p2, wire.p2_pin) if cable.p2.is_connector else None
    if r1 is None:
        r1 = r2 if r2 is not None else index
    if r2 is None:
        r2 = r1
    return r1, r2


def _body_pad(cable: Cable) -> float:
    """Spazio sopra e sotto le righe per i connettori piu' alti delle righe (GM)."""
    rows_h = _rows(cable) * ROW
    return max([0.0] + [(connector_height(e.kind, e.positions, ROW) - rows_h) / 2
                        for e in (cable.p1, cable.p2) if e.is_connector])


def _table_height(cable: Cable) -> float:
    return (2 + len(cable.wires)) * TABLE_ROW


def cable_size(cable: Cable) -> QSizeF:
    if cable.is_branched:
        return _branched_size(cable)
    height = NAME_H + LABEL_H + _rows(cable) * ROW + 2 * _body_pad(cable) + CODES_H + _table_height(cable)
    return QSizeF(CABLE_WIDTH, height)


def draw_cable(p: QPainter, cable: Cable, x: float, y: float) -> QRectF:
    """Disegna il cavo con l'angolo in alto a sinistra in (x, y)."""
    if cable.is_branched:
        return _draw_branched(p, cable, x, y)
    size = cable_size(cable)
    face1 = x + SIDE
    face2 = face1 + SPAN
    pad = _body_pad(cable)
    top = y + NAME_H + LABEL_H + pad
    bottom = top + _rows(cable) * ROW + pad

    text(p, x, y + NAME_H / 2, cable.name, 3.0, bold=True)

    paths = []
    for i, w in enumerate(cable.wires):
        r1, r2 = _wire_rows(cable, i, w)
        y1, y2 = top + (r1 + 0.5) * ROW, top + (r2 + 0.5) * ROW
        e1, e2 = _contact_y(cable.p1, top, r1, y1), _contact_y(cable.p2, top, r2, y2)
        paths.append(_wire_points(face1, y1, e1, face2, y2, e2))
        _draw_wire(p, paths[-1], w.color)
    _draw_label(p, face1 + SLEEVE_INSET, paths, y + NAME_H + 1.0, cable.name, +1)

    rows = [_wire_rows(cable, i, w) for i, w in enumerate(cable.wires)]
    _draw_end(p, cable.p1, cable.wires, [r[0] for r in rows], face1, top, -1)
    _draw_end(p, cable.p2, cable.wires, [r[1] for r in rows], face2, top, +1)

    for face, end, outward in ((face1, cable.p1, -1), (face2, cable.p2, +1)):
        cx = face + outward * SIDE / 2
        for k, line in enumerate(end_codes(end.kind, end.positions, end.variant)):
            text(p, cx, bottom + 2.5 + k * 2.8, line, FONT, _ALIGN_C)

    _draw_wire_list(p, cable, x, bottom + CODES_H, size.width())
    return QRectF(QPointF(x, y), size)


def _contact_y(end: End, top: float, row: int, y: float) -> float:
    """Quota a cui il filo tocca il connettore: per i GM i contatti sono piu' fitti
    delle righe, negli altri casi coincide con la riga."""
    if not end.is_connector:
        return y
    center = top + end.positions * ROW / 2
    return center + contact_offsets(end.kind, end.positions, ROW)[row]


def _wire_points(x1: float, y1: float, e1: float, x2: float, y2: float,
                 e2: float) -> list[QPointF]:
    """Percorso del filo: dritto sulla riga y1, incrocio verso y2 vicino a P2,
    convergenza sui contatti (e1, e2) alle estremita' che lo richiedono."""
    fan2 = GM_FAN if e2 != y2 else 0.0
    points = [QPointF(x1, e1)]
    if e1 != y1:
        points.append(QPointF(x1 + GM_FAN, y1))
    if y1 != y2:
        points += [QPointF(x2 - 4.0 - CROSS - fan2, y1), QPointF(x2 - 4.0 - fan2, y2)]
    if fan2:
        points.append(QPointF(x2 - GM_FAN, y2))
    points.append(QPointF(x2, e2))
    return points


def _draw_wire(p: QPainter, points: list[QPointF], code: str) -> None:
    path = QPainterPath(points[0])
    for point in points[1:]:
        path.lineTo(point)

    color = COLORS[code]
    p.setBrush(Qt.BrushStyle.NoBrush)
    fill = QColor(*color.rgb)
    p.setPen(pen(0.9, fill.darker(WIRE_OUTLINE)))
    p.drawPath(path)
    p.setPen(pen(0.55, fill))
    p.drawPath(path)
    if color.stripe:
        stripe = pen(0.55, QColor(*color.stripe))
        stripe.setDashPattern([3, 3])
        p.setPen(stripe)
        p.drawPath(path)


def _draw_end(p: QPainter, end: End, wires: list[Wire], rows: list[int], face: float,
              top: float, outward: int) -> None:
    """Disegna un'estremita'. `rows` e' la riga di ogni filo, usata dai terminali per filo."""
    align = _ALIGN_L if outward > 0 else _ALIGN_R
    pins = [w.p1_pin if outward < 0 else w.p2_pin for w in wires]

    if end.is_connector:
        outer = draw_connector(p, end.kind, face, top, end.positions, ROW, outward)
        colors = {pin: w.color for pin, w in zip(pins, wires)}
        for pin in range(1, end.positions + 1):
            y = top + (_pin_row(end, pin, outward) + 0.5) * ROW
            _pin_label(p, outer + outward * 1.0, y, pin, colors.get(pin), outward)
        return

    for w, row in zip(wires, rows):
        cy = top + (row + 0.5) * ROW
        tip = TERMINALS[end.kind](p, face, cy, outward)
        text(p, tip + outward * 1.0, cy, w.color, FONT, align)


def _pin_label(p: QPainter, x: float, y: float, pin: int, color: str | None, outward: int) -> None:
    """'1 RD' accanto al contatto; i pin senza filo diventano '2 nc', con nc in corsivo.
    x e' il bordo vicino al connettore: a destra (outward > 0) il testo parte da li',
    a sinistra finisce li'."""
    if color is not None:
        text(p, x, y, f"{pin} {color}", FONT, _ALIGN_L if outward > 0 else _ALIGN_R)
        return
    number = f"{pin} "
    if outward > 0:
        text(p, x, y, number, FONT, _ALIGN_L)
        text(p, x + text_width(p, number, FONT), y, NOT_CONNECTED, FONT, _ALIGN_L, italic=True)
    else:
        text(p, x, y, NOT_CONNECTED, FONT, _ALIGN_R, italic=True)
        text(p, x - text_width(p, NOT_CONNECTED, FONT, italic=True), y, number, FONT, _ALIGN_R)


def _y_at(points: list[QPointF], x: float) -> float | None:
    """Quota del filo (spezzata) in x, None se il filo non passa da li'."""
    for a, b in zip(points, points[1:]):
        if min(a.x(), b.x()) <= x <= max(a.x(), b.x()):
            t = 0.0 if a.x() == b.x() else (x - a.x()) / (b.x() - a.x())
            return a.y() + t * (b.y() - a.y())
    return None


def _draw_label(p: QPainter, x: float, paths: list[list[QPointF]], tag_top: float,
                label: str, direction: int) -> None:
    """Etichetta: fascetta attorno ai fili in x e, a quota tag_top, il cartellino con il
    testo collegato alla fascetta. Il cartellino parte da x verso `direction` (+1 destra)."""
    ys = [y for y in (_y_at(points, x) for points in paths) if y is not None]
    if not ys:
        return
    # alta quanto i fili, ma almeno quanto la scritta LABEL
    height = max(max(ys) - min(ys) + 2.0, text_width(p, SLEEVE_TEXT, SLEEVE_FONT) + 1.0)
    sleeve = QRectF(x - SLEEVE_W / 2, (min(ys) + max(ys) - height) / 2, SLEEVE_W, height)
    width = text_width(p, label, FONT, bold=True) + 2 * CELL_PAD
    left = x - TAG_OFFSET if direction > 0 else x + TAG_OFFSET - width
    tag = QRectF(left, tag_top, width, TAG_H)
    tip = sleeve.top()
    leader = pen(0.2)
    leader.setDashPattern([4, 3])  # in multipli dello spessore: tratti da 0,8 mm
    p.setPen(leader)
    p.drawLine(QPointF(x, tag.bottom()), QPointF(x, tip - ARROW_L))
    p.setPen(pen(0.2))
    p.setBrush(INK)
    p.drawPolygon(QPolygonF([QPointF(x, tip), QPointF(x - ARROW_L / 3, tip - ARROW_L),
                             QPointF(x + ARROW_L / 3, tip - ARROW_L)]))
    p.setBrush(WHITE)
    p.drawRect(sleeve)
    p.save()
    p.translate(sleeve.center())
    p.rotate(-90)  # si legge dal basso verso l'alto
    text(p, 0, 0, SLEEVE_TEXT, SLEEVE_FONT, _ALIGN_C)
    p.restore()
    p.drawRect(tag)
    text(p, tag.center().x(), tag.center().y(), label, FONT, _ALIGN_C, bold=True)


def _has_sections(cable: Cable) -> bool:
    return any(w.section_mm2 is not None or w.awg is not None for w in cable.wires)


def _end_text(end: End, pin: int | None) -> str:
    """Estremita' di un filo per la WIRE LIST, es. 'GM-1712/S-7P (pin 1)', 'FLAT CUT'."""
    code = end_codes(end.kind, end.positions, end.variant)[0]
    return f"{code} (pin {pin})" if end.is_connector and pin is not None else code


def _wire_list(cable: Cable) -> tuple[list[str], list[list[str]]]:
    """Intestazioni e righe: ogni riga dice da dove a dove va il filo e con cosa."""
    sections = _has_sections(cable)
    headers = ["FROM", "COLOR", "LENGTH"] + ["SECTION"] * sections
    headers += ["BRANCH"] * cable.is_branched + ["TO"]
    rows = []
    for index, branch in enumerate(cable.branches):
        for w in branch.wires:
            row = [_end_text(cable.p1, w.p1_pin), f"{w.color} ({COLORS[w.color].name_en})",
                   f"{w.length_mm:g}mm"]
            if sections:
                row.append(section_text(w.section_mm2, w.awg) or "-")
            if cable.is_branched:
                row.append(branch_title(branch.name, index))
            rows.append(row + [_end_text(branch.end, w.p2_pin)])
    return headers, rows


def _draw_wire_list(p: QPainter, cable: Cable, x0: float, y: float, width: float) -> None:
    """WIRE LIST larga quanto il cavo; colonne proporzionate al contenuto, font ridotto
    se le righe non ci stanno."""
    headers, rows = _wire_list(cable)
    height = (2 + len(rows)) * TABLE_ROW
    natural = [max([text_width(p, h, TABLE_FONT, bold=True)]
                   + [text_width(p, r[i], TABLE_FONT) for r in rows])
               for i, h in enumerate(headers)]
    pads = 2 * CELL_PAD * len(headers)
    font = TABLE_FONT
    if sum(natural) + pads > width:
        font = max(TABLE_MIN_FONT, TABLE_FONT * (width - pads) / sum(natural))
    widths = [n * font / TABLE_FONT + 2 * CELL_PAD for n in natural]
    widths = [w * width / sum(widths) for w in widths]  # lo spazio in piu' (o in meno) in proporzione

    p.setPen(pen(0.2))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawRect(QRectF(x0, y, width, height))
    text(p, x0 + width / 2, y + TABLE_ROW / 2, "WIRE LIST", FONT, _ALIGN_C, bold=True)
    for r, cells in enumerate([headers] + rows, start=1):
        ry = y + r * TABLE_ROW
        p.setPen(pen(0.2))
        p.drawLine(QPointF(x0, ry), QPointF(x0 + width, ry))
        cx = x0
        for col_w, cell in zip(widths, cells):
            text(p, cx + CELL_PAD, ry + TABLE_ROW / 2, cell, font, _ALIGN_L, bold=r == 1)
            cx += col_w
    p.setPen(pen(0.2))
    cx = x0
    for col_w in widths[:-1]:
        cx += col_w
        p.drawLine(QPointF(cx, y + TABLE_ROW), QPointF(cx, y + height))


# --- cavi con piu' rami ----------------------------------------------------------
# P1 a sinistra con l'etichetta del cavo; i rami sono impilati a destra, ognuno con il
# suo connettore, i suoi codici e la sua etichetta "A. nome" ("Branch A" senza nome). Le
# lettere seguono l'elenco dei rami (come nella card), anche se l'ordine di disegno e' un
# altro. I fili partono insieme da P1 e nel tratto SPLIT si spostano verso il ramo a cui vanno.

@dataclass
class _BranchBox:
    index: int       # posizione nell'elenco dei rami, da 0
    branch: Branch
    y0: float        # inizio del blocco, relativo alla cima della pila
    rows_top: float  # cima delle righe dei fili, relativa alla cima della pila
    height: float
    codes: list[str]

    @property
    def rows(self) -> int:
        return _end_rows(self.branch.end, len(self.branch.wires))


def _end_rows(end: End, wires: int) -> int:
    return end.positions if end.is_connector else wires


def _end_pad(end: End, rows: int) -> float:
    if not end.is_connector:
        return 0.0
    return max(0.0, (connector_height(end.kind, end.positions, ROW) - rows * ROW) / 2)


def _p1_rows(cable: Cable) -> list[int]:
    """Riga di P1 di ogni filo (nell'ordine di cable.wires)."""
    if cable.p1.is_connector:
        return [_pin_row(cable.p1, w.p1_pin, -1) for w in cable.wires]
    return list(range(len(cable.wires)))


def _branch_boxes(cable: Cable) -> list[_BranchBox]:
    """Rami nell'ordine di disegno: dall'alto, seguendo le righe dei loro fili su P1,
    cosi' i gruppi di fili non si incrociano."""
    p1_rows = iter(_p1_rows(cable))
    first_row = {id(b): min([next(p1_rows) for _ in b.wires], default=0) for b in cable.branches}
    indexes = {id(b): i for i, b in enumerate(cable.branches)}
    ordered = sorted(cable.branches, key=lambda b: first_row[id(b)])
    boxes, y = [], 0.0
    for branch in ordered:
        rows = _end_rows(branch.end, len(branch.wires))
        pad = _end_pad(branch.end, rows)
        codes = end_codes(branch.end.kind, branch.end.positions, branch.end.variant)
        height = BRANCH_LABEL_H + 2 * pad + rows * ROW + len(codes) * CODE_LINE + 1.0
        boxes.append(_BranchBox(indexes[id(branch)], branch, y, y + BRANCH_LABEL_H + pad,
                                height, codes))
        y += height + BRANCH_GAP
    return boxes


def _branch_rows(end: End, wires: list[Wire], p1_row: dict[int, int]) -> list[int]:
    """Riga di ogni filo nel ramo: il pin del connettore, oppure (terminali per filo)
    lo stesso ordine che i fili hanno su P1, cosi' non si incrociano."""
    if end.is_connector:
        return [_pin_row(end, w.p2_pin) for w in wires]
    order = sorted(range(len(wires)), key=lambda i: p1_row[id(wires[i])])
    return [order.index(i) for i in range(len(wires))]


def _branched_heights(cable: Cable, boxes: list[_BranchBox]) -> tuple[float, float, float]:
    """Altezze di: pila dei rami, blocco di P1 (righe + margini), corpo del cavo."""
    stack = sum(b.height for b in boxes) + BRANCH_GAP * (len(boxes) - 1)
    rows = _end_rows(cable.p1, len(cable.wires))
    p1 = rows * ROW + 2 * _end_pad(cable.p1, rows)
    return stack, p1, max(stack, p1)


def _branched_size(cable: Cable) -> QSizeF:
    body = _branched_heights(cable, _branch_boxes(cable))[2]
    return QSizeF(CABLE_WIDTH, NAME_H + LABEL_H + body + CODES_H + _table_height(cable))


def _draw_branched(p: QPainter, cable: Cable, x: float, y: float) -> QRectF:
    size = _branched_size(cable)
    boxes = _branch_boxes(cable)
    stack_h, p1_h, body_h = _branched_heights(cable, boxes)
    face1, face2 = x + SIDE, x + SIDE + SPAN
    split1, split2 = face1 + SPAN * SPLIT[0], face1 + SPAN * SPLIT[1]
    top = y + NAME_H + LABEL_H
    stack_top = top + (body_h - stack_h) / 2
    p1_rows_n = _end_rows(cable.p1, len(cable.wires))
    p1_top = top + (body_h - p1_h) / 2 + _end_pad(cable.p1, p1_rows_n)
    bottom = top + body_h

    text(p, x, y + NAME_H / 2, cable.name, 3.0, bold=True)

    p1_row = dict(zip(map(id, cable.wires), _p1_rows(cable)))
    all_paths = []
    for box in boxes:
        end, wires = box.branch.end, box.branch.wires
        rows_top = stack_top + box.rows_top

        paths = []
        rows2 = _branch_rows(end, wires, p1_row)
        for w, r2 in zip(wires, rows2):
            r1 = p1_row[id(w)]
            y1, y2 = p1_top + (r1 + 0.5) * ROW, rows_top + (r2 + 0.5) * ROW
            e1, e2 = _contact_y(cable.p1, p1_top, r1, y1), _contact_y(end, rows_top, r2, y2)
            points = [QPointF(face1, e1)]
            if e1 != y1:
                points.append(QPointF(face1 + GM_FAN, y1))
            if y1 != y2:
                points += [QPointF(split1, y1), QPointF(split2, y2)]
            if e2 != y2:
                points.append(QPointF(face2 - GM_FAN, y2))
            points.append(QPointF(face2, e2))
            _draw_wire(p, points, w.color)
            paths.append(points)
        all_paths += paths
        if box.branch.label:
            _draw_label(p, face2 - SLEEVE_INSET, paths, stack_top + box.y0,
                        branch_title(box.branch.name, box.index), -1)

        _draw_end(p, end, wires, rows2, face2, rows_top, +1)
        codes_top = rows_top + box.rows * ROW + _end_pad(end, box.rows)
        for k, line in enumerate(box.codes):
            text(p, face2 + SIDE / 2, codes_top + 2.0 + k * CODE_LINE, line, FONT, _ALIGN_C)

    _draw_label(p, face1 + SLEEVE_INSET, all_paths, y + NAME_H + 1.0, cable.name, +1)
    _draw_end(p, cable.p1, cable.wires, _p1_rows(cable), face1, p1_top, -1)
    for k, line in enumerate(end_codes(cable.p1.kind, cable.p1.positions, cable.p1.variant)):
        text(p, face1 - SIDE / 2, bottom + 2.5 + k * CODE_LINE, line, FONT, _ALIGN_C)

    _draw_wire_list(p, cable, x, bottom + CODES_H, size.width())
    return QRectF(QPointF(x, y), size)
