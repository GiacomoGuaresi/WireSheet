"""Card del cartiglio, fissa in cima alla pila: titolo, azienda, progetto, autore, data, revisione."""

from datetime import date

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from wiresheet.model import Project
from wiresheet.ui.icons import icon
from wiresheet.ui.widgets import NoWheelSpinBox

# campi testo: attributo di Project -> (etichetta, riga, colonna, colonne occupate dal campo)
FIELDS = {
    "title": ("Titolo", 0, 0, 6),
    "company": ("Azienda", 1, 0, 1),
    "machine": ("Progetto / macchina", 1, 2, 5),
    "drawn_by": ("Disegnato da", 2, 0, 1),
    "date": ("Data", 2, 2, 1),
}


class TitleBlockCard(QFrame):
    """Non si comprime: i campi sono sempre visibili. `changed` parte per ogni modifica
    ai campi, non per load()."""
    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBlockCard")

        header = QHBoxLayout()
        badge = QLabel()
        badge.setPixmap(icon("file-text").pixmap(QSize(18, 18)))
        title = QLabel("Cartiglio")
        title.setObjectName("cardTitle")
        header.addWidget(badge)
        header.addWidget(title)
        header.addStretch()

        grid = QGridLayout()
        grid.setHorizontalSpacing(8)
        grid.setColumnStretch(1, 1)
        grid.setColumnStretch(3, 1)
        self.edits: dict[str, QLineEdit] = {}
        for name, (label, row, col, span) in FIELDS.items():
            edit = QLineEdit()
            edit.textChanged.connect(lambda _text: self.changed.emit())
            self.edits[name] = edit
            grid.addWidget(QLabel(label), row, col)
            grid.addWidget(edit, row, col + 1, 1, span)
        self.edits["date"].setPlaceholderText("es. 2026-10-20")
        today = QPushButton("Oggi")
        today.clicked.connect(self._set_today)
        grid.addWidget(today, 2, 4)

        self.revision = NoWheelSpinBox()
        self.revision.setRange(0, 9999)
        self.revision.setToolTip("Sale da sola a ogni salvataggio con modifiche; "
                                 "se la cambi qui, al salvataggio resta questo numero")
        self.revision.valueChanged.connect(lambda _value: self.changed.emit())
        grid.addWidget(QLabel("Revisione"), 2, 5)
        grid.addWidget(self.revision, 2, 6)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 10)
        layout.addLayout(header)
        layout.addLayout(grid)

    def _set_today(self) -> None:
        self.edits["date"].setText(date.today().isoformat())

    def load(self, project: Project) -> None:
        for name, edit in self.edits.items():
            value = getattr(project, name)
            if edit.text().strip() != value:  # non sposta il cursore mentre si scrive
                edit.blockSignals(True)
                edit.setText(value)
                edit.blockSignals(False)
        self.revision.blockSignals(True)
        self.revision.setValue(project.revision)
        self.revision.blockSignals(False)

    def values(self) -> dict[str, str | int]:
        values: dict[str, str | int] = {name: e.text().strip() for name, e in self.edits.items()}
        values["revision"] = self.revision.value()
        return values
