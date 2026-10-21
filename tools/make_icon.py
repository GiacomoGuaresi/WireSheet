"""Genera wiresheet/resources/icon.ico (16-256 px) da icon.svg: python tools/make_icon.py

Il file .ico contiene un PNG per ogni dimensione (formato accettato da Windows Vista in poi)."""

import struct
import sys
from pathlib import Path

from PySide6.QtCore import QBuffer, QByteArray, QIODevice, QRectF, Qt
from PySide6.QtGui import QGuiApplication, QImage, QPainter
from PySide6.QtSvg import QSvgRenderer

RESOURCES = Path(__file__).resolve().parent.parent / "wiresheet" / "resources"
SIZES = (16, 24, 32, 48, 64, 128, 256)


def png_bytes(renderer: QSvgRenderer, size: int) -> bytes:
    image = QImage(size, size, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    p = QPainter(image)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    renderer.render(p, QRectF(0, 0, size, size))
    p.end()
    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.OpenModeFlag.WriteOnly)
    image.save(buffer, "PNG")
    return bytes(data)


def main() -> None:
    app = QGuiApplication(sys.argv)  # noqa: F841 - serve a QSvgRenderer
    renderer = QSvgRenderer(str(RESOURCES / "icon.svg"))
    images = [png_bytes(renderer, s) for s in SIZES]
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = len(header) + 16 * len(images)
    entries = b""
    for size, data in zip(SIZES, images):
        side = 0 if size == 256 else size  # 0 = 256 nel formato ICO
        entries += struct.pack("<BBBBHHII", side, side, 0, 0, 1, 32, len(data), offset)
        offset += len(data)
    (RESOURCES / "icon.ico").write_bytes(header + entries + b"".join(images))
    print(f"Creato {RESOURCES / 'icon.ico'} ({', '.join(map(str, SIZES))} px)")


if __name__ == "__main__":
    main()
