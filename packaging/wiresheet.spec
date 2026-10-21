# Build: pyinstaller packaging/wiresheet.spec  ->  dist/WireSheet/WireSheet.exe (Windows), dist/WireSheet.app (macOS)
import sys
from pathlib import Path

ROOT = Path(SPECPATH).parent
RESOURCES = ROOT / "wiresheet" / "resources"
sys.path.insert(0, str(ROOT))
from wiresheet import __version__ as VERSION  # noqa: E402


def windows_version_file() -> str:
    """Proprieta' del file .exe (Dettagli → Versione) da __version__."""
    from PyInstaller.utils.win32.versioninfo import (FixedFileInfo, StringFileInfo, StringStruct,
                                                     StringTable, VarFileInfo, VarStruct,
                                                     VSVersionInfo)
    numbers = tuple(int(n) for n in VERSION.split(".")) + (0,)
    strings = {"CompanyName": "Giacomo Guaresi", "FileDescription": "WireSheet",
               "FileVersion": VERSION, "ProductName": "WireSheet", "ProductVersion": VERSION,
               "OriginalFilename": "WireSheet.exe", "LegalCopyright": "MIT License"}
    info = VSVersionInfo(
        ffi=FixedFileInfo(filevers=numbers, prodvers=numbers),
        kids=[StringFileInfo([StringTable("040904B0", [StringStruct(k, v) for k, v in strings.items()])]),
              VarFileInfo([VarStruct("Translation", [0x0409, 1200])])])
    out = Path(workpath) / "version_info.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(str(info), encoding="utf-8")
    return str(out)


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

# cartella dist/WireSheet (exe + _internal): parte subito, a differenza dell'exe singolo
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name="WireSheet", console=False, icon=icon,
          version=None if sys.platform == "darwin" else windows_version_file())
coll = COLLECT(exe, a.binaries, a.datas, name="WireSheet")

if sys.platform == "darwin":
    app = BUNDLE(coll, name="WireSheet.app", icon=icon, bundle_identifier="com.giacomoguaresi.wiresheet",
                 info_plist={"NSHighResolutionCapable": True,
                             "CFBundleShortVersionString": VERSION,
                             "CFBundleVersion": VERSION})
