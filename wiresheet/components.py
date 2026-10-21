"""Catalogo dei componenti di estremita' supportati."""

import re
from enum import Enum


class EndKind(Enum):
    JST_XH = "jst_xh"
    GM1312 = "gm1312"
    GM1712 = "gm1712"
    GM2112 = "gm2112"
    TERMINAL_BLOCK = "terminal_block"
    FERRULE = "ferrule"
    FORK = "fork"
    FASTON_F = "faston_f"
    FLAT_CUT = "flat_cut"


JST_XH_POSITIONS = range(2, 8)
JST_XH_TERMINAL = "SXH-001T-P0.6"
TERMINAL_BLOCK_POSITIONS = range(2, 9)  # morsettiera a innesto passo 5.08 (tipo Phoenix MSTB)

# connettori la cui variante e' solo il numero di posizioni
POSITION_RANGES = {EndKind.JST_XH: JST_XH_POSITIONS, EndKind.TERMINAL_BLOCK: TERMINAL_BLOCK_POSITIONS}

KIND_LABELS = {
    EndKind.JST_XH: "JST XH",
    EndKind.GM1312: "GM1312",
    EndKind.GM1712: "GM1712",
    EndKind.GM2112: "GM2112",
    EndKind.TERMINAL_BLOCK: "Morsettiera 5.08",
    EndKind.FERRULE: "Puntalini",
    EndKind.FORK: "Forcelle",
    EndKind.FASTON_F: "Faston F",
    EndKind.FLAT_CUT: "Taglio netto",
}

# --- connettori circolari GM a pannello (Hengzhan, fissaggio posteriore) ------------
#
# Disposizione dei contatti come nel catalogo: vista frontale del connettore
# MASCHIO, chiave in alto. Ogni pin e' (x, y, diametro) in frazioni del raggio
# della faccia, x verso destra e y verso il basso; l'ordine e' quello dei pin 1..n.
# La vista lato saldatura della femmina (/S) coincide con questa; quella del
# maschio (/P) e' speculare.

PinLayout = tuple[tuple[float, float, float], ...]

_S13_17: dict[str, PinLayout] = {
    "2": ((0.40, 0.0, 0.31), (-0.40, 0.0, 0.31)),
    "3": ((0.37, -0.19, 0.28), (-0.37, -0.19, 0.28), (0.0, 0.44, 0.28)),
    "4": ((0.31, -0.37, 0.19), (-0.31, -0.37, 0.19), (-0.31, 0.28, 0.19), (0.31, 0.28, 0.19)),
    "5": ((-0.29, -0.44, 0.19), (-0.47, 0.12, 0.19), (0.0, 0.47, 0.19), (0.47, 0.12, 0.19),
          (0.29, -0.44, 0.19)),
    "6": ((0.0, -0.59, 0.19), (-0.45, -0.28, 0.19), (-0.50, 0.27, 0.19), (0.0, 0.55, 0.19),
          (0.50, 0.27, 0.19), (0.45, -0.28, 0.19)),
    "7": ((-0.29, -0.51, 0.19), (-0.58, -0.03, 0.19), (-0.29, 0.47, 0.19), (0.30, 0.47, 0.19),
          (0.58, -0.03, 0.19), (0.30, -0.51, 0.19), (0.0, -0.03, 0.19)),
    "9": ((-0.22, -0.52, 0.15), (-0.52, -0.22, 0.15), (-0.52, 0.22, 0.15), (-0.22, 0.53, 0.15),
          (0.22, 0.53, 0.15), (0.53, 0.22, 0.15), (0.53, -0.22, 0.15), (0.22, -0.52, 0.15),
          (0.0, 0.0, 0.15)),
}

_S21: dict[str, PinLayout] = {
    "2": ((0.0, -0.41, 0.33), (0.0, 0.41, 0.33)),
    "3": ((0.35, -0.19, 0.33), (-0.35, -0.19, 0.33), (0.0, 0.41, 0.33)),
    "4": ((0.0, -0.40, 0.33), (0.40, 0.0, 0.33), (-0.40, 0.0, 0.33), (0.0, 0.40, 0.33)),
    "5A": ((0.25, -0.32, 0.33), (-0.25, -0.32, 0.33), (0.40, 0.13, 0.33), (-0.40, 0.13, 0.33),
           (0.0, 0.39, 0.33)),
    "5B": ((0.35, -0.29, 0.33), (-0.35, -0.29, 0.33), (0.42, 0.31, 0.13), (-0.42, 0.31, 0.13),
           (0.0, 0.53, 0.13)),
    "5C": ((0.32, -0.42, 0.25), (-0.32, -0.42, 0.25), (0.53, 0.18, 0.25), (-0.53, 0.18, 0.25),
           (0.0, 0.59, 0.25)),
    "7": ((0.24, -0.38, 0.25), (-0.24, -0.38, 0.25), (0.47, 0.02, 0.25), (0.0, 0.02, 0.25),
          (-0.47, 0.02, 0.25), (0.24, 0.42, 0.25), (-0.24, 0.42, 0.25)),
    "9": ((0.24, -0.52, 0.13), (-0.22, -0.52, 0.13), (0.56, -0.20, 0.13), (-0.55, -0.20, 0.13),
          (0.0, 0.03, 0.13), (0.56, 0.25, 0.13), (-0.55, 0.25, 0.13), (0.24, 0.58, 0.13),
          (-0.22, 0.58, 0.13)),
    "12": ((0.20, -0.52, 0.13), (-0.20, -0.52, 0.13), (0.51, -0.27, 0.13), (0.0, -0.20, 0.13),
           (-0.51, -0.26, 0.13), (0.58, 0.13, 0.13), (0.21, 0.14, 0.13), (-0.20, 0.14, 0.13),
           (-0.59, 0.13, 0.13), (0.38, 0.46, 0.13), (0.0, 0.61, 0.13), (-0.37, 0.46, 0.13)),
}

GM_LAYOUTS: dict[EndKind, dict[str, PinLayout]] = {
    EndKind.GM1312: dict(_S13_17),
    EndKind.GM1712: {k: v for k, v in _S13_17.items() if k != "6"},
    EndKind.GM2112: _S21,
}
GM_GENDERS = {"S": "femmina", "P": "maschio"}

CONNECTOR_KINDS = {*POSITION_RANGES, *GM_LAYOUTS}


def gm_variants(kind: EndKind) -> list[str]:
    """Varianti del connettore GM: genere + disposizione, es. 'S4', 'P5A'."""
    return [g + layout for g in GM_GENDERS for layout in GM_LAYOUTS[kind]]


def variant_positions(variant: str) -> int:
    """Numero di pin di una variante GM ('S5A' -> 5)."""
    match = re.search(r"\d+", variant)
    return int(match.group()) if match else 0


def gm_layout(kind: EndKind, variant: str) -> PinLayout | None:
    """Disposizione dei pin vista dal lato saldatura; None se la variante non esiste."""
    layout = GM_LAYOUTS.get(kind, {}).get(variant[1:])
    if layout is None or variant[:1] not in GM_GENDERS:
        return None
    if variant[0] == "P":  # maschio: speculare rispetto alla vista del catalogo
        layout = tuple((-x, y, d) for x, y, d in layout)
    return layout


def parse_gm_variant(kind: EndKind, text: str) -> str | None:
    """'S4', 's-4p', 'P 5a' -> variante canonica; None se non valida."""
    match = re.fullmatch(r"([SP])(\d+)([ABC]?)P?", re.sub(r"[^A-Z0-9]", "", str(text).upper()))
    if not match:
        return None
    variant = "".join(match.groups())
    return variant if variant in gm_variants(kind) else None


def _key(text: str) -> str:
    return "".join(ch for ch in text.lower() if ch.isalnum())


_KIND_ALIASES = {
    **{_key(label): kind for kind, label in KIND_LABELS.items()},
    **{_key(kind.value): kind for kind in EndKind},
    _key("XH"): EndKind.JST_XH,
    _key("Puntalino"): EndKind.FERRULE,
    _key("Forcella"): EndKind.FORK,
    _key("Morsettiera"): EndKind.TERMINAL_BLOCK,
    _key("Terminal block"): EndKind.TERMINAL_BLOCK,
    _key("Faston"): EndKind.FASTON_F,
    _key("Faston femmina"): EndKind.FASTON_F,
    _key("Flat cut"): EndKind.FLAT_CUT,
    _key("Taglio"): EndKind.FLAT_CUT,
}


def parse_kind(text: str) -> EndKind | None:
    """Tipo di estremita' da 'JST XH', 'puntalini', 'GM-2112', 'taglio netto'...; None se sconosciuto."""
    return _KIND_ALIASES.get(_key(text))


def end_codes(kind: EndKind, positions: int = 0, variant: str = "") -> list[str]:
    """Righe di testo che descrivono il componente sotto l'estremita'."""
    if kind is EndKind.JST_XH:
        return [f"JST:XHP-{positions}", JST_XH_TERMINAL]
    if kind in GM_LAYOUTS:
        return [gm_code(kind, variant), "PANEL, REAR MOUNT"]
    if kind is EndKind.TERMINAL_BLOCK:
        return [f"TB 5.08-{positions}P", "PLUGGABLE, SCREW"]
    if kind is EndKind.FERRULE:
        return ["FERRULE"]
    if kind is EndKind.FORK:
        return ["FORK"]
    if kind is EndKind.FASTON_F:
        return ["FASTON F 6.3"]
    return ["FLAT CUT"]


def gm_code(kind: EndKind, variant: str) -> str:
    """Codice del fornitore: GM2112 + 'S5A' -> 'GM-2112/S-5P-A'."""
    match = re.fullmatch(r"([SP])(\d+)([ABC]?)", variant)
    if not match:
        return f"{KIND_LABELS[kind]}/{variant}"
    gender, pins, letter = match.groups()
    return f"GM-{kind.value[2:]}/{gender}-{pins}P" + (f"-{letter}" if letter else "")
