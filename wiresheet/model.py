"""Modello dati: progetto -> cavi (ingresso P1 - fili - uno o piu' rami in uscita)."""

import re
from dataclasses import dataclass, field

from wiresheet.colors import COLORS
from wiresheet.gauges import AWG_RANGE
from wiresheet.components import (CONNECTOR_KINDS, GM_LAYOUTS, KIND_LABELS, POSITION_RANGES,
                                  EndKind, gm_variants, variant_positions)


@dataclass
class End:
    kind: EndKind
    positions: int = 0  # numero di pin, solo per i connettori
    variant: str = ""   # connettori GM: genere + disposizione, es. "S4", "P5A"

    @property
    def is_connector(self) -> bool:
        return self.kind in CONNECTOR_KINDS


def end_variants(kind: EndKind) -> list[End]:
    """Tutte le varianti selezionabili di un componente."""
    if kind in POSITION_RANGES:
        return [End(kind, n) for n in POSITION_RANGES[kind]]
    if kind in GM_LAYOUTS:
        return [End(kind, variant_positions(v), v) for v in gm_variants(kind)]
    return [End(kind)]


@dataclass
class Wire:
    color: str
    length_mm: float
    p1_pin: int | None = None
    p2_pin: int | None = None
    section_mm2: float | None = None  # sezione: in mm², in AWG o entrambe (vedi gauges.py)
    awg: int | None = None


@dataclass
class Branch:
    """Ramo in uscita: un'estremita' P2 con i suoi fili. Il nome distingue i rami
    (es. "Cooling fan"), anche quando hanno lo stesso connettore."""
    end: End
    wires: list[Wire] = field(default_factory=list)
    name: str = ""
    label: bool = True  # etichetta del ramo sul disegno (solo nei cavi a piu' rami)


def branch_letter(index: int) -> str:
    """Lettera del ramo nell'elenco: A, B, C..."""
    return chr(ord("A") + index)


def branch_title(name: str, index: int) -> str:
    """Come si chiama un ramo su disegno e card: 'A. Cooling fan' o 'Branch A'."""
    letter = branch_letter(index)
    return f"{letter}. {name}" if name else f"Branch {letter}"


@dataclass(init=False)
class Cable:
    """Un connettore in ingresso (P1) e uno o piu' rami in uscita.
    Cable(nome, p1, p2, fili) crea un cavo semplice con un solo ramo."""
    name: str
    p1: End
    branches: list[Branch]

    def __init__(self, name: str, p1: End, p2: End | None = None,
                 wires: list[Wire] | None = None, branches: list[Branch] | None = None):
        if branches is None:
            if p2 is None:
                raise ValueError("Serve P2 oppure l'elenco dei rami.")
            branches = [Branch(p2, list(wires or []))]
        self.name = name
        self.p1 = p1
        self.branches = branches

    @property
    def p2(self) -> End:
        """Estremita' del primo ramo (l'unica nei cavi semplici)."""
        return self.branches[0].end

    @property
    def wires(self) -> list[Wire]:
        """Tutti i fili, ramo per ramo (lista nuova: non modificarla per aggiungere fili)."""
        return [w for b in self.branches for w in b.wires]

    @property
    def is_branched(self) -> bool:
        return len(self.branches) > 1

    @property
    def length_mm(self) -> float:
        return max((w.length_mm for w in self.wires), default=0.0)

    def branch_label(self, index: int) -> str:
        if not self.is_branched:
            return "P2"
        name = self.branches[index].name
        return f"P2 ramo '{name}'" if name else f"P2 ramo {branch_letter(index)}"

    def validate(self) -> list[str]:
        """Restituisce l'elenco degli errori (vuoto se il cavo e' valido)."""
        errors = []
        if not self.wires:
            errors.append("Il cavo non ha fili.")
        for i, w in enumerate(self.wires, start=1):
            if w.color not in COLORS:
                errors.append(f"Filo {i}: colore '{w.color}' sconosciuto.")
            if w.length_mm <= 0:
                errors.append(f"Filo {i}: lunghezza non valida.")
            if w.section_mm2 is not None and w.section_mm2 <= 0:
                errors.append(f"Filo {i}: sezione non valida.")
            if w.awg is not None and w.awg not in AWG_RANGE:
                errors.append(f"Filo {i}: AWG {w.awg} non supportato "
                              f"({AWG_RANGE[0]}-{AWG_RANGE[-1]}).")
        errors += _validate_end("P1", self.p1, [w.p1_pin for w in self.wires])
        for i, branch in enumerate(self.branches):
            label = self.branch_label(i)
            if self.is_branched and not branch.wires:
                errors.append(f"{label}: ramo senza fili.")
            errors += _validate_end(label, branch.end, [w.p2_pin for w in branch.wires])
        return errors


@dataclass
class Project:
    """Progetto: i cavi e i campi del cartiglio stampato su ogni foglio."""
    title: str = ""
    company: str = ""
    machine: str = ""    # progetto / macchina a cui appartengono i cavi
    revision: int = 0    # sale di 1 a ogni salvataggio con modifiche (vedi MainWindow.save_to)
    date: str = ""       # testo libero, es. 2026-10-20
    drawn_by: str = ""
    cables: list[Cable] = field(default_factory=list)

    def next_cable_name(self) -> str:
        """CABLEn con n = numero piu' alto gia' usato + 1."""
        numbers = [int(m.group(1)) for c in self.cables
                   if (m := re.fullmatch(r"CABLE(\d+)", c.name))]
        return f"CABLE{max(numbers, default=0) + 1}"


def _validate_end(label: str, end: End, pins: list[int | None]) -> list[str]:
    if not end.is_connector:
        return []
    if end not in end_variants(end.kind):
        what = (f"a {end.positions} posizioni" if end.kind in POSITION_RANGES
                else f"variante '{end.variant}'")
        return [f"{label}: {KIND_LABELS[end.kind]} {what} non supportato."]
    errors = []
    if len(pins) > end.positions:
        errors.append(f"{label}: {len(pins)} fili su un connettore a {end.positions} posizioni.")
    for i, pin in enumerate(pins, start=1):
        if pin is None or not 1 <= pin <= end.positions:
            errors.append(f"{label}: filo {i} con pin non valido ({pin}).")
    used = [p for p in pins if p is not None]
    for pin in sorted({p for p in used if used.count(p) > 1}):
        errors.append(f"{label}: pin {pin} usato piu' volte.")
    return errors
