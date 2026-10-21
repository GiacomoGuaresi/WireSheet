"""Sezioni dei fili: mm² e AWG, con la tabella di equivalenza commerciale.

Un filo puo' avere la sezione in mm², in AWG o in entrambe. Se ne manca una, si
ricava dall'altra con la tabella (non con la formula: 0,25 mm² e' AWG24, anche se
l'area dell'AWG24 e' 0,205 mm²).
"""

import math
import re

# (mm², AWG) equivalenti, dal piu' sottile al piu' grosso. Fonte: Multi/Cable,
# "Cross reference AWG to mm2" (multicable_AWG-table-accessible.pdf)
EQUIVALENTS = [
    (0.05, 30), (0.08, 28), (0.14, 26), (0.25, 24), (0.34, 22), (0.38, 21), (0.5, 20),
    (0.75, 18), (1.0, 17), (1.5, 16), (2.5, 14), (4.0, 12), (6.0, 10), (10.0, 8),
]
MM2_SIZES = [mm2 for mm2, _ in EQUIVALENTS]
AWG_RANGE = range(8, 31)


def awg_area(awg: int) -> float:
    """Area reale in mm² di un AWG."""
    d = 0.127 * 92 ** ((36 - awg) / 39)
    return math.pi / 4 * d * d


def mm2_to_awg(mm2: float) -> int:
    for size, awg in EQUIVALENTS:
        if math.isclose(size, mm2):
            return awg
    return min(AWG_RANGE, key=lambda awg: abs(math.log(awg_area(awg) / mm2)))


def awg_to_mm2(awg: int) -> float:
    for size, a in EQUIVALENTS:
        if a == awg:
            return size
    area = awg_area(awg)
    return min(MM2_SIZES, key=lambda size: abs(math.log(size / area)))


def section_pair(mm2: float | None, awg: int | None) -> tuple[float, int] | None:
    """Entrambe le unita', ricavando quella mancante. None se il filo non ha sezione."""
    if mm2 is None and awg is None:
        return None
    return (mm2 if mm2 is not None else awg_to_mm2(awg),
            awg if awg is not None else mm2_to_awg(mm2))


def section_text(mm2: float | None, awg: int | None) -> str:
    """Testo completo per disegno e card, es. '0.25mm² (24AWG)'; vuoto se non c'e' sezione."""
    pair = section_pair(mm2, awg)
    return f"{pair[0]:g}mm² ({pair[1]}AWG)" if pair else ""


def section_cell(mm2: float | None, awg: int | None) -> str:
    """Testo per l'export in tabella: solo le unita' indicate, es. '0.25mm²', '24AWG'."""
    if mm2 is not None and awg is not None:
        return section_text(mm2, awg)
    if mm2 is not None:
        return f"{mm2:g}mm²"
    return f"{awg}AWG" if awg is not None else ""


def parse_section(text) -> tuple[float | None, int | None] | None:
    """Interpreta '0,25', '0.25 mm2', '0.25mm²', '24AWG', 'AWG 24', '0.25mm² (24AWG)'.
    Restituisce (mm², awg) con None per l'unita' non indicata; (None, None) se vuoto;
    None se non e' interpretabile."""
    if text is None or (isinstance(text, str) and not text.strip()):
        return None, None
    if isinstance(text, (int, float)):
        return (float(text), None) if text > 0 else None
    s = str(text).strip().lower().replace(",", ".")
    awg = None
    match = re.search(r"awg\s*#?(\d+)|(\d+)\s*awg", s)
    if match:
        awg = int(match.group(1) or match.group(2))
        if awg not in AWG_RANGE:
            return None
        s = s[:match.start()] + s[match.end():]
    s = s.replace("(", " ").replace(")", " ").strip()
    if not s:
        return None, awg
    match = re.fullmatch(r"(\d+(?:\.\d+)?)\s*(mm2|mm²|mmq|mm)?", s)
    if not match or float(match.group(1)) <= 0:
        return None
    return float(match.group(1)), awg
