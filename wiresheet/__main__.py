"""Avvio dell'applicazione: python -m wiresheet [progetto.wiresheet]

python -m wiresheet --self-test CARTELLA esegue lo smoke test usato dalla pipeline sugli eseguibili."""

import sys
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from wiresheet import __version__
from wiresheet.ui.main_window import MainWindow

ICON = Path(__file__).resolve().parent / "resources" / "icon.svg"


def self_test(folder: str | Path) -> None:
    """Controlla che nel pacchetto ci sia tutto: risorse, PDF (Qt, font) ed Excel (openpyxl).
    Serve una QApplication; solleva un'eccezione al primo problema."""
    from wiresheet.demo import demo_project
    from wiresheet.pdf_export import export_pdf
    from wiresheet.table_io import example_cables, import_table, write_table

    folder = Path(folder)
    folder.mkdir(parents=True, exist_ok=True)
    if QIcon(str(ICON)).isNull():
        raise RuntimeError(f"Icona non trovata: {ICON}")
    if export_pdf(demo_project(), folder / "demo.pdf") < 1:
        raise RuntimeError("Il PDF demo non ha pagine")
    write_table(folder / "template.xlsx", example_cables())
    result = import_table(folder / "template.xlsx")
    if result.errors or len(result.cables) != len(example_cables()):
        raise RuntimeError(f"Template Excel non reimportabile: {result.errors}")
    MainWindow().close()


def run_self_test(folder: str) -> int:
    app = QApplication(sys.argv[:1])  # noqa: F841
    try:
        self_test(folder)
    except Exception as e:  # noqa: BLE001 - qualsiasi errore fa fallire lo smoke test
        (Path(folder) / "self-test-error.txt").write_text(repr(e), encoding="utf-8")
        print(f"Self-test fallito: {e!r}", file=sys.stderr)
        return 1
    print(f"Self-test WireSheet {__version__} riuscito")
    return 0


def main() -> None:
    if len(sys.argv) == 3 and sys.argv[1] == "--self-test":
        sys.exit(run_self_test(sys.argv[2]))
    if sys.platform == "win32":
        # senza un AppUserModelID la barra delle applicazioni mostra l'icona di Python
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("WireSheet")
    app = QApplication(sys.argv)
    app.setApplicationName("WireSheet")
    app.setOrganizationName("WireSheet")  # chiave delle impostazioni (QSettings)
    app.setApplicationVersion(__version__)
    app.setWindowIcon(QIcon(str(ICON)))
    window = MainWindow()
    if len(sys.argv) > 1:
        window.open_path(sys.argv[1])
    window.show()
    if window.auto_update_enabled():
        QTimer.singleShot(1500, lambda: window.check_updates(silent=True))
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
