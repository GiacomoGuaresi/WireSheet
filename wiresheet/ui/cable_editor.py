"""Corpo della card di un cavo: ingresso P1, rami in uscita (P2) e tabella dei fili."""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (QCheckBox, QComboBox, QHBoxLayout, QHeaderView, QLabel, QLineEdit,
                               QPushButton, QToolButton, QVBoxLayout, QWidget)

from wiresheet.colors import COLORS
from wiresheet.gauges import EQUIVALENTS, section_text
from wiresheet.components import GM_GENDERS, KIND_LABELS, EndKind
from wiresheet.model import Branch, Cable, End, Wire, branch_letter, branch_title, end_variants
from wiresheet.ui.icons import color_swatch, icon
from wiresheet.ui.style import DANGER
from wiresheet.ui.widgets import (EndThumbnail, FixedHeightTable, NoWheelComboBox,
                                 NoWheelDoubleSpinBox)

COL_P1, COL_COLOR, COL_LENGTH, COL_SECTION, COL_BRANCH, COL_P2 = range(6)
HEADERS = {COL_P1: "Pin P1", COL_COLOR: "Colore", COL_LENGTH: "Lunghezza (mm)",
           COL_SECTION: "Sezione", COL_BRANCH: "Ramo", COL_P2: "Pin P2"}
DEFAULT_COLORS = ["RD", "BK", "YE", "GN", "WH", "BU", "BN"]
ROW_HEIGHT = 30


def end_short(end: End) -> str:
    if end.variant:
        return f"{KIND_LABELS[end.kind]}/{end.variant}"
    if end.kind is EndKind.TERMINAL_BLOCK:
        return f"TB-{end.positions}"
    return f"XH-{end.positions}" if end.is_connector else KIND_LABELS[end.kind]


def variant_label(end: End) -> str:
    if end.variant:
        return f"{end.variant} · {end.positions} pin {GM_GENDERS[end.variant[0]]}"
    if end.is_connector:
        return f"{end.positions} pin"
    return "Nessun terminale" if end.kind is EndKind.FLAT_CUT else "Un terminale per filo"


class EndEditor(QWidget):
    """Estremita' del cavo:

        P1
        [tipo di componente      v]
        [variante (pin) v] [miniatura]
    """

    changed = Signal()

    def __init__(self, title: str, outward: int, parent=None):
        super().__init__(parent)
        label = QLabel(title)
        label.setObjectName("endTitle")
        label.setVisible(bool(title))
        self.kind = NoWheelComboBox()
        for kind, text in KIND_LABELS.items():
            self.kind.addItem(text, kind)
        self.variant = NoWheelComboBox()
        self.thumbnail = EndThumbnail(outward)

        variant_row = QHBoxLayout()
        variant_row.addWidget(self.variant, 1)
        variant_row.addWidget(self.thumbnail)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addWidget(label)
        layout.addWidget(self.kind)
        layout.addLayout(variant_row)

        self._variants: list[End] = []
        self._fill_variants(None)
        self.kind.currentIndexChanged.connect(self._on_kind_changed)
        self.variant.currentIndexChanged.connect(self._on_change)

    def _fill_variants(self, previous: End | None) -> None:
        """Varianti del componente scelto (pin, genere...). Tiene la piu' simile a `previous`."""
        self._variants = end_variants(self.kind.currentData())
        self.variant.blockSignals(True)
        self.variant.clear()
        for end in self._variants:
            self.variant.addItem(variant_label(end))
        self.variant.setCurrentIndex(self._closest(previous))
        self.variant.setEnabled(len(self._variants) > 1)
        self.variant.blockSignals(False)

    def _closest(self, previous: End | None) -> int:
        if previous is None:
            return 0
        if previous in self._variants:
            return self._variants.index(previous)
        gender = previous.variant[:1] or "S"
        for match in (lambda e: e.positions == previous.positions and e.variant[:1] == gender,
                      lambda e: e.positions >= previous.positions and e.variant[:1] == gender,
                      lambda e: e.positions >= previous.positions):
            index = next((i for i, e in enumerate(self._variants) if match(e)), None)
            if index is not None:
                return index
        return 0

    def set_end(self, end: End) -> None:
        self.kind.blockSignals(True)
        self.kind.setCurrentIndex(self.kind.findData(end.kind))
        self.kind.blockSignals(False)
        self._fill_variants(end)
        self._update_thumbnail()

    def set_positions(self, positions: int) -> None:
        """Passa alla variante con almeno `positions` pin (stesso genere per i GM)."""
        current = self.end()
        index = self._closest(End(current.kind, positions, current.variant[:1]))
        if self._variants[index].positions >= positions:
            self.variant.setCurrentIndex(index)

    def end(self) -> End:
        return self._variants[max(self.variant.currentIndex(), 0)]

    def _update_thumbnail(self) -> None:
        end = self.end()
        self.thumbnail.set_end(end.kind, end.positions)

    def _on_kind_changed(self) -> None:
        self._fill_variants(self._variants[max(self.variant.currentIndex(), 0)])
        self._on_change()

    def _on_change(self) -> None:
        self._update_thumbnail()
        self.changed.emit()


class BranchRow(QWidget):
    """Un ramo in uscita: [Ramo n] [nome] [etichetta] [elimina] sopra l'EndEditor del suo
    connettore. Con un solo ramo la riga del nome e' nascosta e resta solo l'estremita' P2."""

    changed = Signal()           # componente o variante
    renamed = Signal()
    label_toggled = Signal()
    remove_requested = Signal()

    def __init__(self, name: str, end: End, label: bool = True, parent=None):
        super().__init__(parent)
        self.number = QLabel()
        self.number.setObjectName("endTitle")
        self.name = QLineEdit(name)
        self.name.setPlaceholderText("Nome del ramo (es. Cooling fan)")
        self.label = QCheckBox("Etichetta")
        self.label.setChecked(label)
        self.label.setToolTip("Disegna l'etichetta del ramo sul cavo")
        self.remove = QToolButton()
        self.remove.setObjectName("cardAction")
        self.remove.setIcon(icon("trash", DANGER))
        self.remove.setToolTip("Elimina il ramo (i suoi fili passano al primo ramo)")
        self.end_editor = EndEditor("", outward=+1)
        self.end_editor.set_end(end)

        head = QHBoxLayout()
        head.addWidget(self.number)
        head.addWidget(self.name, 1)
        head.addWidget(self.label)
        head.addWidget(self.remove)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        layout.addLayout(head)
        layout.addWidget(self.end_editor)

        self.end_editor.changed.connect(self.changed)
        self.name.textChanged.connect(self.renamed)
        self.label.toggled.connect(self.label_toggled)
        self.remove.clicked.connect(self.remove_requested)

    def set_number(self, index: int, multiple: bool) -> None:
        self.number.setText(f"Branch {branch_letter(index)}")
        for widget in (self.number, self.name, self.label, self.remove):
            widget.setVisible(multiple)


class CableEditor(QWidget):
    """Emette `changed` a ogni modifica fatta dall'utente (non durante load())."""

    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._loading = False

        self.p1 = EndEditor("P1 — ingresso", outward=-1)
        self.p2_title = QLabel()
        self.p2_title.setObjectName("endTitle")
        self.branch_rows: list[BranchRow] = []
        self.branch_layout = QVBoxLayout()
        self.branch_layout.setSpacing(12)
        add_branch = QPushButton(icon("plus"), "Ramo")
        add_branch.setToolTip("Aggiungi un ramo: i fili si dividono tra più estremità in uscita")
        add_branch.clicked.connect(self._add_branch)

        self.table = FixedHeightTable(0, len(HEADERS))
        self.table.setHorizontalHeaderLabels([HEADERS[c] for c in range(len(HEADERS))])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setDefaultSectionSize(ROW_HEIGHT)

        add = QPushButton(icon("plus"), "Filo")
        remove = QPushButton(icon("minus"), "Filo")
        add.setToolTip("Aggiungi un filo (nello stesso ramo dell'ultimo)")
        remove.setToolTip("Rimuovi il filo selezionato (o l'ultimo)")
        add.clicked.connect(self._add_wire)
        remove.clicked.connect(self._remove_wire)

        self.errors = QLabel()
        self.errors.setObjectName("errors")
        self.errors.setWordWrap(True)

        right = QVBoxLayout()
        right.setSpacing(4)
        right.addWidget(self.p2_title)
        right.addLayout(self.branch_layout)
        right.addWidget(add_branch, 0, Qt.AlignmentFlag.AlignLeft)
        left = QVBoxLayout()
        left.addWidget(self.p1)
        left.addStretch()
        ends = QHBoxLayout()
        ends.addLayout(left, 1)
        ends.addSpacing(24)
        ends.addLayout(right, 1)
        wire_buttons = QHBoxLayout()
        wire_buttons.addWidget(add)
        wire_buttons.addWidget(remove)
        wire_buttons.addStretch()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addLayout(ends)
        layout.addWidget(self.table)
        layout.addLayout(wire_buttons)
        layout.addWidget(self.errors)

        self.p1.changed.connect(self._on_ends_changed)
        self._set_branches([("", End(EndKind.JST_XH, 2), True)])
        self.table.fit_height()

    @property
    def p2(self) -> EndEditor:
        """Estremita' del primo ramo (l'unica nei cavi semplici)."""
        return self.branch_rows[0].end_editor

    # --- caricamento / lettura ------------------------------------------

    def load(self, cable: Cable) -> None:
        self._loading = True
        self.p1.set_end(cable.p1)
        self.table.setRowCount(0)
        self._set_branches([(b.name, b.end, b.label) for b in cable.branches])
        for index, branch in enumerate(cable.branches):
            for w in branch.wires:
                self._append_row(w, index)
        self.table.fit_height()
        self._loading = False
        self._update_errors()

    def cable(self, name: str) -> Cable:
        groups: list[list[Wire]] = [[] for _ in self.branch_rows]
        for row, wire in enumerate(self._wires()):
            groups[self._row_branch(row)].append(wire)
        branches = [Branch(r.end_editor.end(), wires, r.name.text().strip(), r.label.isChecked())
                    for r, wires in zip(self.branch_rows, groups)]
        return Cable(name, self.p1.end(), branches=branches)

    def _wires(self) -> list[Wire]:
        cell = self.table.cellWidget
        return [Wire(cell(row, COL_COLOR).currentData(), cell(row, COL_LENGTH).value(),
                     cell(row, COL_P1).currentData(), cell(row, COL_P2).currentData(),
                     *cell(row, COL_SECTION).currentData())
                for row in range(self.table.rowCount())]

    def _emit_changed(self) -> None:
        if self._loading:
            return
        self._update_errors()
        self.changed.emit()

    def _update_errors(self) -> None:
        errors = self.cable("").validate()
        self.errors.setText("\n".join(errors))
        self.errors.setVisible(bool(errors))

    # --- rami -------------------------------------------------------------

    def _set_branches(self, branches: list[tuple[str, End, bool]]) -> None:
        for row in self.branch_rows:
            row.setParent(None)
            row.deleteLater()
        self.branch_rows = []
        for name, end, label in branches:
            self._append_branch_row(name, end, label)
        self._update_branch_ui()

    def _append_branch_row(self, name: str, end: End, label: bool = True) -> None:
        row = BranchRow(name, end, label)
        row.changed.connect(self._on_ends_changed)
        row.label_toggled.connect(self._emit_changed)
        row.renamed.connect(self._on_branch_renamed)
        row.remove_requested.connect(lambda: self._remove_branch(row))
        self.branch_layout.addWidget(row)
        self.branch_rows.append(row)

    def _update_branch_ui(self, mapping: dict[int, int] | None = None) -> None:
        """Titoli, numeri dei rami, colonna Ramo e tendine; `mapping` rinumera i rami
        dei fili dopo l'eliminazione di un ramo."""
        multiple = len(self.branch_rows) > 1
        self.p2_title.setText("P2 — rami in uscita" if multiple else "P2 — estremità 2")
        for i, row in enumerate(self.branch_rows):
            row.set_number(i, multiple)
        self.table.setColumnHidden(COL_BRANCH, not multiple)
        for r in range(self.table.rowCount()):
            combo = self.table.cellWidget(r, COL_BRANCH)
            index = combo.currentData() or 0  # grezzo: prima della rinumerazione
            if mapping is not None:
                index = mapping.get(index, 0)
            self._fill_branches(combo, index)

    def _branch_label(self, index: int) -> str:
        return branch_title(self.branch_rows[index].name.text().strip(), index)

    def _fill_branches(self, combo: QComboBox, index: int) -> None:
        combo.blockSignals(True)
        combo.clear()
        for i in range(len(self.branch_rows)):
            combo.addItem(self._branch_label(i), i)
        combo.setCurrentIndex(min(max(index, 0), len(self.branch_rows) - 1))
        combo.blockSignals(False)

    def _row_branch(self, row: int) -> int:
        combo = self.table.cellWidget(row, COL_BRANCH)
        index = combo.currentData() if combo is not None else None
        return index if index is not None and index < len(self.branch_rows) else 0

    def _branch_end(self, row: int) -> End:
        return self.branch_rows[self._row_branch(row)].end_editor.end()

    def _add_branch(self) -> None:
        self._append_branch_row("", self.branch_rows[-1].end_editor.end())
        self._update_branch_ui()
        self.branch_rows[-1].name.setFocus()
        self._emit_changed()

    def _remove_branch(self, branch: BranchRow) -> None:
        if len(self.branch_rows) <= 1:
            return
        removed = self.branch_rows.index(branch)
        self.branch_rows.remove(branch)
        branch.setParent(None)
        branch.deleteLater()
        old = range(len(self.branch_rows) + 1)
        mapping = {i: 0 if i == removed else (i - 1 if i > removed else i) for i in old}
        self._update_branch_ui(mapping)
        self._on_ends_changed()

    def _on_branch_renamed(self) -> None:
        self._update_branch_ui()
        self._emit_changed()

    # --- tabella fili ---------------------------------------------------

    def _pin_combo(self, end: End, pin: int | None) -> QComboBox:
        combo = NoWheelComboBox()
        self._fill_pins(combo, end, pin)
        combo.currentIndexChanged.connect(self._emit_changed)
        return combo

    @staticmethod
    def _fill_pins(combo: QComboBox, end: End, pin: int | None) -> None:
        combo.blockSignals(True)
        combo.clear()
        if end.is_connector:
            for n in range(1, end.positions + 1):
                combo.addItem(str(n), n)
            combo.setCurrentIndex(max(combo.findData(pin), 0))
        else:
            combo.addItem("-", None)
        combo.setEnabled(end.is_connector)
        combo.blockSignals(False)

    def _append_row(self, wire: Wire, branch: int = 0) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)

        color = NoWheelComboBox()
        for code in COLORS:
            color.addItem(color_swatch(code), code, code)
        color.setCurrentIndex(color.findData(wire.color))
        color.currentIndexChanged.connect(self._emit_changed)

        length = NoWheelDoubleSpinBox()
        length.setRange(1, 100000)
        length.setDecimals(0)
        length.setValue(wire.length_mm)
        length.valueChanged.connect(self._emit_changed)

        branch_combo = NoWheelComboBox()
        self._fill_branches(branch_combo, branch)
        branch_combo.currentIndexChanged.connect(lambda: self._on_row_branch_changed(branch_combo))

        self.table.setCellWidget(row, COL_P1, self._pin_combo(self.p1.end(), wire.p1_pin))
        self.table.setCellWidget(row, COL_COLOR, color)
        self.table.setCellWidget(row, COL_BRANCH, branch_combo)
        self.table.setCellWidget(row, COL_P2, self._pin_combo(self._branch_end(row), wire.p2_pin))
        self.table.setCellWidget(row, COL_LENGTH, length)
        self.table.setCellWidget(row, COL_SECTION, self._section_combo(wire))

    def _section_combo(self, wire: Wire) -> QComboBox:
        """Misure comuni come '0.25mm² (24AWG)'; '—' = senza sezione. Un valore diverso
        (es. da import, o con una sola unita') resta com'e' e compare in fondo."""
        combo = NoWheelComboBox()
        combo.addItem("—", (None, None))
        value = (wire.section_mm2, wire.awg)
        values = list(EQUIVALENTS)
        if value != (None, None) and value not in values:
            values.append(value)
        for pair in values:
            combo.addItem(section_text(*pair), pair)
        combo.setCurrentIndex(max(combo.findData(value), 0))
        combo.currentIndexChanged.connect(self._emit_changed)
        return combo

    def _on_row_branch_changed(self, combo: QComboBox) -> None:
        """Filo spostato in un altro ramo: pin P2 = primo pin libero del nuovo ramo."""
        row = next(r for r in range(self.table.rowCount())
                   if self.table.cellWidget(r, COL_BRANCH) is combo)
        branch = self._row_branch(row)
        used = [w.p2_pin for r, w in enumerate(self._wires())
                if r != row and self._row_branch(r) == branch]
        end = self._branch_end(row)
        self._fill_pins(self.table.cellWidget(row, COL_P2), end, self._free_pin(end, used))
        self._emit_changed()

    def _add_wire(self) -> None:
        count = self.table.rowCount()
        branch = self._row_branch(count - 1) if count else 0
        in_branch = sum(1 for r in range(count) if self._row_branch(r) == branch)
        # connettore pieno: aggiunge una posizione
        for editor, n in ((self.p1, count), (self.branch_rows[branch].end_editor, in_branch)):
            end = editor.end()
            if end.is_connector and n >= end.positions:
                editor.set_positions(end.positions + 1)
        wires = self._wires()
        used_colors = {w.color for w in wires}
        color = next((c for c in DEFAULT_COLORS if c not in used_colors), "BK")
        last = wires[-1] if wires else Wire("BK", 300)  # lunghezza e sezione come l'ultimo
        p2_used = [w.p2_pin for r, w in enumerate(wires) if self._row_branch(r) == branch]
        self._append_row(Wire(color, last.length_mm,
                              self._free_pin(self.p1.end(), [w.p1_pin for w in wires]),
                              self._free_pin(self.branch_rows[branch].end_editor.end(), p2_used),
                              last.section_mm2, last.awg), branch)
        self.table.fit_height()
        self._emit_changed()

    @staticmethod
    def _free_pin(end: End, used: list[int | None]) -> int | None:
        if not end.is_connector:
            return None
        return next((n for n in range(1, end.positions + 1) if n not in used), end.positions)

    def _remove_wire(self) -> None:
        row = self.table.currentRow()
        if row < 0:
            row = self.table.rowCount() - 1
        if row >= 0:
            self.table.removeRow(row)
            self.table.fit_height()
            self._emit_changed()

    def _on_ends_changed(self) -> None:
        p1 = self.p1.end()
        in_branch = [0] * len(self.branch_rows)
        for row in range(self.table.rowCount()):
            branch = self._row_branch(row)
            in_branch[branch] += 1
            for col, end, fallback in ((COL_P1, p1, row + 1),
                                       (COL_P2, self._branch_end(row), in_branch[branch])):
                combo: QComboBox = self.table.cellWidget(row, col)
                pin = combo.currentData()
                if pin is None:  # l'estremita' prima non era un connettore
                    pin = fallback
                self._fill_pins(combo, end, pin)
        self._emit_changed()
