"""Export del progetto in PDF: un foglio verticale per pagina."""

from pathlib import Path

from PySide6.QtCore import QMarginsF
from PySide6.QtGui import QPageLayout, QPageSize, QPainter, QPdfWriter

from wiresheet.model import Project
from wiresheet.render.sheet_layout import draw_page, layout_pages, sheet_geometry

_PAGE_IDS = {"A3": QPageSize.PageSizeId.A3, "A4": QPageSize.PageSizeId.A4}


def export_pdf(project: Project, path: str | Path, page: str = "A3") -> int:
    """Scrive il PDF e restituisce il numero di fogli."""
    geometry = sheet_geometry(page)
    pages = layout_pages(project.cables, geometry)

    writer = QPdfWriter(str(path))
    writer.setPageSize(QPageSize(_PAGE_IDS[page]))
    writer.setPageOrientation(QPageLayout.Orientation.Portrait)
    writer.setPageMargins(QMarginsF(0, 0, 0, 0))
    writer.setResolution(1200)
    writer.setTitle(project.title)

    p = QPainter(writer)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.scale(writer.resolution() / 25.4, writer.resolution() / 25.4)
    for i, placements in enumerate(pages):
        if i:
            writer.newPage()
        draw_page(p, project, placements, geometry, i + 1, len(pages))
    p.end()
    return len(pages)
