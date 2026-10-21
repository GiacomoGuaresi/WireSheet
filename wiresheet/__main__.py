"""Avvio dell'applicazione: python -m wiresheet [progetto.wiresheet]"""

import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from wiresheet.ui.main_window import MainWindow

ICON = Path(__file__).resolve().parent / "resources" / "icon.svg"


def main() -> None:
    if sys.platform == "win32":
        # senza un AppUserModelID la barra delle applicazioni mostra l'icona di Python
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("WireSheet")
    app = QApplication(sys.argv)
    app.setApplicationName("WireSheet")
    app.setWindowIcon(QIcon(str(ICON)))
    window = MainWindow()
    if len(sys.argv) > 1:
        window.open_path(sys.argv[1])
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
