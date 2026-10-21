from wiresheet.components import EndKind
from wiresheet.demo import demo_project
from wiresheet.model import Cable, End, Wire
from wiresheet.pdf_export import export_pdf
from wiresheet.render.cable_drawer import _body_pad, _rows, _wire_points, _wire_rows
from wiresheet.render.symbols import connector_height, contact_offsets


def test_per_wire_end_follows_connector_rows():
    c = Cable("C", End(EndKind.JST_XH, 7), End(EndKind.FLAT_CUT),
              [Wire("BN", 500, 1), Wire("BU", 500, 3)])
    assert _wire_rows(c, 1, c.wires[1]) == (4, 4)  # pin 3 di 7 su P1, contando dal basso
    assert _rows(c) == 7


def test_crossed_pins():
    c = Cable("C", End(EndKind.JST_XH, 3), End(EndKind.JST_XH, 3), [Wire("RD", 350, 1, 2)])
    assert _wire_rows(c, 0, c.wires[0]) == (2, 1)  # P1: pin 1 in basso; P2 ruotato: pin 2 al centro


def test_no_connectors_uses_wire_index():
    c = Cable("C", End(EndKind.FORK), End(EndKind.FERRULE), [Wire("RD", 100), Wire("BK", 100)])
    assert _wire_rows(c, 1, c.wires[1]) == (1, 1)
    assert _rows(c) == 2


def test_export_pdf(app, tmp_path):
    out = tmp_path / "demo.pdf"
    assert export_pdf(demo_project(), out) >= 2
    assert out.read_bytes().startswith(b"%PDF")


def test_gm_wires_converge_on_solder_cups():
    offsets = contact_offsets(EndKind.GM2112, 12, 3.0)
    assert len(offsets) == 12
    assert offsets == sorted(offsets)
    assert offsets[-1] - offsets[0] < 12 * 3.0       # piu' fitti delle righe
    assert contact_offsets(EndKind.JST_XH, 3, 3.0) == [-3.0, 0.0, 3.0]


def test_wire_points_fan_only_where_needed():
    straight = _wire_points(0, 10, 10, 80, 10, 10)
    assert [(q.x(), q.y()) for q in straight] == [(0, 10), (80, 10)]
    fanned = _wire_points(0, 10, 12, 80, 10, 10)
    assert (fanned[0].y(), fanned[1].y()) == (12, 10)


def test_tall_connector_gets_padding():
    gm = Cable("C", End(EndKind.GM2112, 2, "S2"), End(EndKind.FLAT_CUT), [Wire("RD", 100, 1)])
    assert _body_pad(gm) == (connector_height(EndKind.GM2112, 2) - 2 * 3.0) / 2
    xh = Cable("C", End(EndKind.JST_XH, 2), End(EndKind.FLAT_CUT), [Wire("RD", 100, 1)])
    assert _body_pad(xh) < 2.0


def test_every_end_kind_renders(app, tmp_path):
    from wiresheet.model import Project, end_variants
    cables = []
    for kind in EndKind:
        for end in end_variants(kind):
            n = end.positions or 2
            wires = [Wire("RD", 100, i if end.is_connector else None, None) for i in range(1, n + 1)]
            cables.append(Cable(f"{kind.value}-{end.variant or end.positions}", end,
                                End(EndKind.FLAT_CUT), wires))
    for c in cables:
        assert c.validate() == [], c.name
    assert export_pdf(Project(cables=cables), tmp_path / "all.pdf") >= 1


def test_branched_layout_follows_p1_rows(app):
    from wiresheet.render.cable_drawer import _branch_boxes, _branch_rows, _p1_rows, cable_size
    c = next(c for c in demo_project().cables if c.name == "FANS, MAT SENSOR")
    boxes = _branch_boxes(c)
    # P1 col pin 1 in basso: il ramo con i pin piu' alti va in cima
    # le lettere restano quelle dell'elenco dei rami (indice 0 = A)
    assert [(b.index, b.branch.name) for b in boxes] == [
        (2, "Extruder fan"), (1, "Material sensor"), (0, "Cooling fan")]
    assert all(a.y0 + a.height < b.y0 for a, b in zip(boxes, boxes[1:]))
    p1_row = dict(zip(map(id, c.wires), _p1_rows(c)))
    assert p1_row[id(c.wires[0])] == 6  # pin 1 di P1 (GM a 7 pin) sull'ultima riga in basso
    flat = boxes[0].branch  # taglio netto: stesso ordine di P1, nessun incrocio
    assert _branch_rows(flat.end, flat.wires, p1_row) == [1, 0]
    assert cable_size(c).height() > sum(b.height for b in boxes)



def test_wire_list_rows_are_self_explanatory():
    from wiresheet.render.cable_drawer import _wire_list
    from wiresheet.model import Branch
    c = Cable("FANS", End(EndKind.GM1712, 7, "S7"), branches=[
        Branch(End(EndKind.JST_XH, 2), [Wire("RD", 800, 1, 1, 0.5)], "Cooling fan"),
        Branch(End(EndKind.FLAT_CUT), [Wire("YE/GN", 1000, 6)]),
    ])
    headers, rows = _wire_list(c)
    assert headers == ["FROM", "COLOR", "LENGTH", "SECTION", "BRANCH", "TO"]
    assert rows == [
        ["GM-1712/S-7P (pin 1)", "RD (Red)", "800mm", "0.5mm² (20AWG)", "A. Cooling fan", "JST:XHP-2 (pin 1)"],
        ["GM-1712/S-7P (pin 6)", "YE/GN (Yellow/Green)", "1000mm", "-", "Branch B", "FLAT CUT"],
    ]
    simple = Cable("C", End(EndKind.FORK), End(EndKind.FERRULE), [Wire("BK", 50)])
    assert _wire_list(simple) == (["FROM", "COLOR", "LENGTH", "TO"],
                                  [["FORK", "BK (Black)", "50mm", "FERRULE"]])


def test_long_wire_list_fits_cable_width(app, tmp_path):
    from wiresheet.model import Project
    c = next(c for c in demo_project().cables if c.name == "TH EXT")
    c.branches[0].name = "Termistore zona 1 estrusore (lato sinistro)"
    assert export_pdf(Project(cables=[c]), tmp_path / "long.pdf") == 1


def test_p2_is_rotated_not_mirrored():
    # FEED RUNOUT: XH-2 pin 1 -> XH-3 pin 2, XH-2 pin 2 -> XH-3 pin 3
    c = Cable("C", End(EndKind.JST_XH, 2), End(EndKind.JST_XH, 3),
              [Wire("WH", 500, 1, 2), Wire("BU", 500, 2, 3)])
    rows = [_wire_rows(c, i, w) for i, w in enumerate(c.wires)]
    assert [r[0] for r in rows] == [1, 0]   # P1: WH in basso, BU sopra
    assert [r[1] for r in rows] == [1, 2]   # P2: pin 1 in alto, WH al centro, BU in basso


def test_label_sleeve_follows_wires():
    from PySide6.QtCore import QPointF
    from wiresheet.render.cable_drawer import _y_at
    wire = [QPointF(0, 10), QPointF(50, 10), QPointF(60, 20), QPointF(80, 20)]
    assert _y_at(wire, 20) == 10
    assert _y_at(wire, 55) == 15      # nel tratto in cui il filo si incrocia
    assert _y_at(wire, 90) is None    # fuori dal filo: la fascetta lo ignora


def test_branch_label_can_be_hidden(app, monkeypatch):
    from PySide6.QtGui import QImage, QPainter
    import wiresheet.render.cable_drawer as drawer
    c = next(c for c in demo_project().cables if c.name == "FANS, MAT SENSOR")
    c.branches[1].label = False
    drawn = []
    monkeypatch.setattr(drawer, "_draw_label", lambda p, x, paths, top, label, d: drawn.append(label))
    img = QImage(10, 10, QImage.Format.Format_RGB32)
    p = QPainter(img)
    drawer.draw_cable(p, c, 0, 0)
    p.end()
    assert "B. Material sensor" not in drawn
    assert {"FANS, MAT SENSOR", "A. Cooling fan", "C. Extruder fan"} <= set(drawn)
