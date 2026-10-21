"""Card di un cavo: intestazione (nome, riepilogo, stato, azioni) + corpo (editor)."""

from PySide6.QtCore import QSize, Signal
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QToolButton, QVBoxLayout

from wiresheet.model import Cable
from wiresheet.ui.cable_editor import CableEditor, end_short
from wiresheet.ui.icons import icon
from wiresheet.ui.style import DANGER, OK


class CableCard(QFrame):
    changed = Signal()
    activated = Signal()
    duplicate_requested = Signal()
    delete_requested = Signal()
    move_requested = Signal(int)

    def __init__(self, cable: Cable, parent=None):
        super().__init__(parent)
        self.setObjectName("CableCard")
        self.setProperty("active", False)

        self.toggle = QToolButton()
        self.toggle.setObjectName("cardAction")
        self.toggle.setIconSize(QSize(18, 18))
        self.toggle.setToolTip("Comprimi / espandi")
        self.toggle.clicked.connect(lambda: self.set_expanded(not self.is_expanded()))

        self.name = QLineEdit()
        self.name.setObjectName("cardName")
        self.name.setMinimumWidth(140)
        self.name.setMaximumWidth(220)
        self.summary = QLabel()
        self.summary.setObjectName("summary")
        self.status_icon = QLabel()
        self.status = QLabel()
        self.has_errors = False

        header = QHBoxLayout()
        header.addWidget(self.toggle)
        header.addWidget(self.name)
        header.addWidget(self.summary, 1)
        header.addWidget(self.status_icon)
        header.addWidget(self.status)
        header.addSpacing(8)
        for name, color, tip, slot in (
            ("copy", None, "Duplica il cavo", self.duplicate_requested.emit),
            ("arrow-up", None, "Sposta su", lambda: self.move_requested.emit(-1)),
            ("arrow-down", None, "Sposta giù", lambda: self.move_requested.emit(+1)),
            ("trash", DANGER, "Elimina il cavo", self.delete_requested.emit),
        ):
            b = QToolButton()
            b.setObjectName("cardAction")
            b.setIcon(icon(name, color) if color else icon(name))
            b.setIconSize(QSize(18, 18))
            b.setToolTip(tip)
            b.clicked.connect(slot)
            header.addWidget(b)
        self.delete_button = b  # ultimo pulsante: Elimina

        self.editor = CableEditor()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 10)
        layout.addLayout(header)
        layout.addWidget(self.editor)

        self.load(cable)
        self.set_expanded(True)
        self.name.textChanged.connect(self._on_changed)
        self.editor.changed.connect(self._on_changed)

    def load(self, cable: Cable) -> None:
        self.name.blockSignals(True)
        self.name.setText(cable.name)
        self.name.blockSignals(False)
        self.editor.load(cable)
        self._update_header()

    def cable(self) -> Cable:
        return self.editor.cable(self.name.text().strip() or "CABLE")

    def is_expanded(self) -> bool:
        return not self.editor.isHidden()

    def set_expanded(self, expanded: bool) -> None:
        self.editor.setVisible(expanded)
        self.toggle.setIcon(icon("chevron-down" if expanded else "chevron-right"))

    def set_active(self, active: bool) -> None:
        if self.property("active") == active:
            return
        self.setProperty("active", active)
        self.style().unpolish(self)
        self.style().polish(self)

    def _on_changed(self) -> None:
        self._update_header()
        self.changed.emit()

    def _update_header(self) -> None:
        cable = self.cable()
        n = len(cable.wires)
        outputs = ", ".join(end_short(b.end) for b in cable.branches)
        self.summary.setText(f"{end_short(cable.p1)} → {outputs}  ·  "
                             f"{n} {'filo' if n == 1 else 'fili'}  ·  {cable.length_mm:g} mm")
        errors = cable.validate()
        if errors:
            self.status_icon.setPixmap(icon("alert", DANGER).pixmap(16, 16))
            self.status.setText(f"{len(errors)} {'errore' if len(errors) == 1 else 'errori'}")
            self.status.setObjectName("statusError")
            tip = "\n".join(errors)
        else:
            self.status_icon.setPixmap(icon("check", OK).pixmap(16, 16))
            self.status.setText("")
            self.status.setObjectName("statusOk")
            tip = "Cavo valido"
        self.status.setToolTip(tip)
        self.status_icon.setToolTip(tip)
        self.has_errors = bool(errors)
        self.status.style().unpolish(self.status)
        self.status.style().polish(self.status)

    def mousePressEvent(self, event) -> None:
        self.activated.emit()
        super().mousePressEvent(event)

    def enterEvent(self, event) -> None:
        """Passando con il mouse la card diventa attiva (e l'anteprima la mostra)."""
        self.activated.emit()
        super().enterEvent(event)
