"""Genera un PDF con alcuni cavi di esempio: python -m wiresheet.demo [file.pdf]"""

import sys

from PySide6.QtGui import QGuiApplication

from wiresheet.components import EndKind
from wiresheet.model import Branch, Cable, End, Project, Wire
from wiresheet.pdf_export import export_pdf


def demo_cables(branched: bool = True) -> list[Cable]:
    """Cavi di esempio; branched=False esclude i cavi con piu' rami."""
    xh = lambda n: End(EndKind.JST_XH, n)
    cables = [
        Cable("CABLE A", xh(2), xh(2), [
            Wire("RD", 350, 1, 1), Wire("BK", 350, 2, 2)]),
        Cable("CABLE B", xh(3), xh(3), [
            Wire("RD", 350, 1, 2), Wire("BK", 350, 2, 1), Wire("WH", 350, 3, 3)]),
        Cable("CABLE C", xh(4), End(EndKind.FERRULE), [
            Wire("RD", 200, 1), Wire("BK", 200, 2), Wire("YE", 200, 3), Wire("GN", 200, 4)]),
        Cable("CABLE D", xh(2), End(EndKind.FORK), [
            Wire("RD", 650, 1), Wire("BK", 650, 2)]),
        Cable("CABLE E", xh(7), End(EndKind.FLAT_CUT), [
            Wire("BN", 500, 1), Wire("BU", 500, 3), Wire("YE/GN", 520, 5)]),
        Cable("CABLE F", End(EndKind.GM2112, 4, "S4"), End(EndKind.FERRULE), [
            Wire("GN", 600, 1), Wire("YE", 600, 2), Wire("RD", 600, 3), Wire("BU", 600, 4)]),
        Cable("CABLE G", End(EndKind.GM1712, 7, "S7"), xh(3), [
            Wire("BU", 500, 1, 2), Wire("WH", 500, 2, 3), Wire("RD", 500, 3, 1)]),
        Cable("CABLE H", End(EndKind.TERMINAL_BLOCK, 4), End(EndKind.FASTON_F), [
            Wire("BN", 400, 1), Wire("BU", 400, 2), Wire("BK", 400, 3)]),
        Cable("FANS, MAT SENSOR", End(EndKind.GM1712, 7, "S7"), branches=[
            Branch(xh(2), [Wire("RD", 800, 1, 1), Wire("BK", 800, 2, 2)], "Cooling fan"),
            Branch(End(EndKind.TERMINAL_BLOCK, 3), [
                Wire("WH", 300, 3, 1), Wire("BK", 300, 4, 2), Wire("RD", 300, 5, 3)],
                "Material sensor"),
            Branch(End(EndKind.FLAT_CUT), [Wire("RD", 1000, 6), Wire("BK", 1000, 7)],
                   "Extruder fan"),
        ]),
        Cable("TH EXT", End(EndKind.GM1712, 9, "S9"), branches=[
            Branch(xh(2), [Wire(a, 500, 2 * z - 1, 2), Wire("WH", 500, 2 * z, 1)],
                   f"Termistore zona {z}")
            for z, a in enumerate(("BU", "RD", "GN", "BK"), start=1)
        ]),
    ]
    return cables if branched else [c for c in cables if not c.is_branched]


def demo_project(branched: bool = True) -> Project:
    return Project(title="Cavi di esempio", company="ACME Srl", machine="DEMO", revision=1,
                   date="2026-10-20", drawn_by="WireSheet", cables=demo_cables(branched))


def main() -> None:
    out = sys.argv[1] if len(sys.argv) > 1 else "demo.pdf"
    app = QGuiApplication(sys.argv)  # noqa: F841 - necessario per font e QPdfWriter
    project = demo_project()
    for c in project.cables:
        if errors := c.validate():
            raise SystemExit(f"{c.name}: " + "; ".join(errors))
    sheets = export_pdf(project, out)
    print(f"Creato {out} ({sheets} {'foglio' if sheets == 1 else 'fogli'})")


if __name__ == "__main__":
    main()
