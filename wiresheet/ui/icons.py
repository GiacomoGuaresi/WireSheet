"""Icone vettoriali in stile Lucide (https://lucide.dev, licenza ISC).

Ogni icona e' un frammento SVG 24x24 a tratto; il colore si sceglie al momento
del rendering, cosi' la stessa icona funziona su sfondo chiaro e su sfondo accent.
"""

from functools import lru_cache

from PySide6.QtCore import QByteArray, QRectF, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from wiresheet.colors import COLORS

DEFAULT_COLOR = "#3b4250"

_PATHS = {
    "plus": '<path d="M5 12h14"/><path d="M12 5v14"/>',
    "minus": '<path d="M5 12h14"/>',
    "x": '<path d="M18 6 6 18"/><path d="m6 6 12 12"/>',
    "chevron-down": '<path d="m6 9 6 6 6-6"/>',
    "chevron-right": '<path d="m9 18 6-6-6-6"/>',
    "chevron-left": '<path d="m15 18-6-6 6-6"/>',
    "arrow-up": '<path d="m5 12 7-7 7 7"/><path d="M12 19V5"/>',
    "arrow-down": '<path d="M12 5v14"/><path d="m19 12-7 7-7-7"/>',
    "copy": '<rect width="14" height="14" x="8" y="8" rx="2" ry="2"/>'
            '<path d="M4 16c-1.1 0-2-.9-2-2V4c0-1.1.9-2 2-2h10c1.1 0 2 .9 2 2"/>',
    "trash": '<path d="M3 6h18"/><path d="M19 6v14c0 1-1 2-2 2H7c-1 0-2-1-2-2V6"/>'
             '<path d="M8 6V4c0-1 1-2 2-2h4c1 0 2 1 2 2v2"/>'
             '<path d="M10 11v6"/><path d="M14 11v6"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/>'
             '<path d="M12 9v4"/><path d="M12 17h.01"/>',
    "zoom-in": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>'
               '<path d="M11 8v6"/><path d="M8 11h6"/>',
    "zoom-out": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/><path d="M8 11h6"/>',
    "fit": '<path d="M8 3H5a2 2 0 0 0-2 2v3"/><path d="M21 8V5a2 2 0 0 0-2-2h-3"/>'
           '<path d="M3 16v3a2 2 0 0 0 2 2h3"/><path d="M16 21h3a2 2 0 0 0 2-2v-3"/>',
    "file-plus": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/>'
                 '<path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M9 15h6"/><path d="M12 18v-6"/>',
    "file-down": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/>'
                 '<path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M12 18v-6"/><path d="m9 15 3 3 3-3"/>',
    "file-text": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/>'
                 '<path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/>'
                 '<path d="M16 13H8"/><path d="M16 17H8"/>',
    "file-up": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/>'
               '<path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M12 12v6"/><path d="m15 15-3-3-3 3"/>',
    "sheet": '<rect width="18" height="18" x="3" y="3" rx="2" ry="2"/><path d="M3 9h18"/>'
             '<path d="M3 15h18"/><path d="M9 9v12"/><path d="M15 9v12"/>',
    "folder-open": '<path d="m6 14 1.5-2.9A2 2 0 0 1 9.24 10H20a2 2 0 0 1 1.94 2.5l-1.54 6'
                   'a2 2 0 0 1-1.95 1.5H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h3.9a2 2 0 0 1 1.69.9'
                   'l.81 1.2a2 2 0 0 0 1.67.9H18a2 2 0 0 1 2 2v2"/>',
    "save": '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>'
            '<path d="M17 21v-8H7v8"/><path d="M7 3v5h8"/>',
    "plug": '<path d="M12 22v-5"/><path d="M9 8V2"/><path d="M15 8V2"/>'
            '<path d="M18 8v5a4 4 0 0 1-4 4h-4a4 4 0 0 1-4-4V8Z"/>',
    "eye": '<path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/>',
    "list-plus": '<path d="M11 12H3"/><path d="M16 6H3"/><path d="M16 18H3"/>'
                 '<path d="M18 9v6"/><path d="M21 12h-6"/>',
}

ICON_NAMES = tuple(_PATHS)


def _svg(name: str, color: str) -> bytes:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" '
            f'fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" '
            f'stroke-linejoin="round">{_PATHS[name]}</svg>').encode()


@lru_cache(maxsize=None)
def icon(name: str, color: str = DEFAULT_COLOR) -> QIcon:
    renderer = QSvgRenderer(QByteArray(_svg(name, color)))
    result = QIcon()
    for size in (16, 24, 32, 48):
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.GlobalColor.transparent)
        p = QPainter(pixmap)
        renderer.render(p, QRectF(0, 0, size, size))
        p.end()
        result.addPixmap(pixmap)
    return result


@lru_cache(maxsize=None)
def toggle_icon(name: str, off: str = DEFAULT_COLOR, on: str = "#ffffff") -> QIcon:
    """Icona per pulsanti checkable: colore `on` quando il pulsante e' attivo."""
    result = QIcon()
    for state, color in ((QIcon.State.Off, off), (QIcon.State.On, on)):
        for size in (16, 24, 32):
            result.addPixmap(icon(name, color).pixmap(size, size), QIcon.Mode.Normal, state)
    return result


@lru_cache(maxsize=None)
def color_swatch(code: str, size: int = 14) -> QIcon:
    """Quadratino del colore del filo (con la riga per i bicolore, es. YE/GN)."""
    color = COLORS[code]
    pixmap = QPixmap(size * 2, size * 2)  # 2x per schermi ad alta densita'
    pixmap.fill(Qt.GlobalColor.transparent)
    p = QPainter(pixmap)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    rect = QRectF(1, 1, size * 2 - 2, size * 2 - 2)
    p.setPen(Qt.PenStyle.NoPen)
    p.setBrush(QColor(*color.rgb))
    p.drawRoundedRect(rect, 4, 4)
    if color.stripe:
        p.setBrush(QColor(*color.stripe))
        p.save()
        p.setClipRect(rect)
        p.drawRect(QRectF(rect.left(), rect.center().y() - size * 0.3, rect.width(), size * 0.6))
        p.restore()
    p.setPen(QColor(120, 125, 135))
    p.setBrush(Qt.BrushStyle.NoBrush)
    p.drawRoundedRect(rect, 4, 4)
    p.end()
    return QIcon(pixmap)
