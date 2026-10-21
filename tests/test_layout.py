import copy

import pytest

from wiresheet.demo import demo_cables, demo_project
from wiresheet.pdf_export import export_pdf
from wiresheet.render.cable_drawer import cable_size
from wiresheet.render.sheet_layout import layout_pages, sheet_geometry


def many_cables(n: int):
    base = demo_cables()
    cables = []
    for i in range(n):
        c = copy.deepcopy(base[i % len(base)])
        c.name = f"CABLE{i + 1}"
        cables.append(c)
    return cables


def rects(page):
    from PySide6.QtCore import QPointF, QRectF
    return [QRectF(QPointF(p.x, p.y), cable_size(p.cable) * p.scale) for p in page]


@pytest.mark.parametrize("page_size", ["A3", "A4"])
def test_no_overlap_and_inside_content(page_size):
    g = sheet_geometry(page_size)
    pages = layout_pages(many_cables(40), g)
    assert sum(len(p) for p in pages) == 40
    for page in pages:
        rs = rects(page)
        for r in rs:
            assert g.content.contains(r)
        for i, a in enumerate(rs):
            for b in rs[i + 1:]:
                assert not a.intersects(b)


def test_portrait_one_column_and_cables_fill_it():
    for page in ("A3", "A4"):
        g = sheet_geometry(page)
        assert g.height > g.width
        assert g.columns == 1
        placement = layout_pages(many_cables(1), g)[0][0]
        width = cable_size(placement.cable).width() * placement.scale
        assert width == pytest.approx(g.column_width - 20.0)  # 10 mm per lato
        assert placement.scale == g.scale
    assert sheet_geometry("A3").scale > 2.0           # A3 verticale: circa 2,2


def test_fifteen_cables_need_more_sheets():
    pages = layout_pages(many_cables(15), sheet_geometry("A3"))
    assert len(pages) >= 2
    assert all(pages)


def test_order_is_preserved():
    cables = many_cables(20)
    pages = layout_pages(cables, sheet_geometry("A3"))
    assert [p.cable.name for page in pages for p in page] == [c.name for c in cables]


def test_export_multi_page(app, tmp_path):
    project = demo_project()
    project.cables = many_cables(15)
    out = tmp_path / "many.pdf"
    assert export_pdf(project, out) >= 2
    assert out.stat().st_size > 0
