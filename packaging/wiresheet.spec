# Build: pyinstaller packaging/wiresheet.spec  ->  dist/WireSheet (.exe su Windows, .app su macOS)
import os
import sys
from pathlib import Path

ROOT = Path(SPECPATH).parent
RESOURCES = ROOT / "wiresheet" / "resources"
VERSION = os.environ.get("WIRESHEET_VERSION", "0.0.0").lstrip("v")  # impostata dalla pipeline di release


def mac_icon() -> str:
    """Rende icon.svg in un PNG 1024 px; PyInstaller (con Pillow) lo converte in .icns."""
    from PySide6.QtCore import QRectF, Qt
    from PySide6.QtGui import QGuiApplication, QImage, QPainter
    from PySide6.QtSvg import QSvgRenderer

    app = QGuiApplication.instance() or QGuiApplication([])  # noqa: F841
    image = QImage(1024, 1024, QImage.Format.Format_ARGB32)
    image.fill(Qt.GlobalColor.transparent)
    p = QPainter(image)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    QSvgRenderer(str(RESOURCES / "icon.svg")).render(p, QRectF(0, 0, 1024, 1024))
    p.end()
    out = Path(workpath) / "icon.png"
    out.parent.mkdir(parents=True, exist_ok=True)
    image.save(str(out))
    return str(out)


icon = mac_icon() if sys.platform == "darwin" else str(RESOURCES / "icon.ico")

a = Analysis(
    [str(ROOT / "packaging" / "launcher.py")],
    pathex=[str(ROOT)],
    datas=[(str(RESOURCES), "wiresheet/resources")],
    hiddenimports=["PySide6.QtSvg"],
    excludes=["tkinter", "pytest"],
)
pyz = PYZ(a.pure)

if sys.platform == "darwin":
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="WireSheet",
              console=False, icon=icon)
    coll = COLLECT(exe, a.binaries, a.datas, name="WireSheet")
    app = BUNDLE(coll, name="WireSheet.app", icon=icon, bundle_identifier="com.giacomoguaresi.wiresheet",
                 info_plist={"NSHighResolutionCapable": True,
                             "CFBundleShortVersionString": VERSION})
else:
    exe = EXE(pyz, a.scripts, a.binaries, a.datas, [], name="WireSheet",
              console=False, icon=icon)
