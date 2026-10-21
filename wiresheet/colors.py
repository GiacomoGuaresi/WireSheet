"""Colori dei fili (sigle IEC 60757)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class WireColor:
    code: str
    rgb: tuple[int, int, int]
    name_it: str
    name_en: str
    stripe: tuple[int, int, int] | None = None


_ALL = [
    WireColor("BK", (20, 20, 20), "Nero", "Black"),
    WireColor("BN", (130, 70, 20), "Marrone", "Brown"),
    WireColor("RD", (220, 30, 30), "Rosso", "Red"),
    WireColor("OR", (255, 140, 0), "Arancione", "Orange"),
    WireColor("YE", (255, 210, 0), "Giallo", "Yellow"),
    WireColor("GN", (0, 150, 60), "Verde", "Green"),
    WireColor("BU", (30, 90, 210), "Blu", "Blue"),
    WireColor("VT", (140, 40, 200), "Viola", "Violet"),
    WireColor("GY", (140, 140, 140), "Grigio", "Grey"),
    WireColor("WH", (255, 255, 255), "Bianco", "White"),
    WireColor("PK", (255, 130, 180), "Rosa", "Pink"),
    WireColor("YE/GN", (255, 210, 0), "Giallo/Verde", "Yellow/Green", stripe=(0, 150, 60)),
]

COLORS: dict[str, WireColor] = {c.code: c for c in _ALL}


def _key(text: str) -> str:
    return "".join(ch for ch in text.upper() if ch.isalnum())


_ALIASES = ({_key(c.code): c.code for c in _ALL} | {_key(c.name_it): c.code for c in _ALL}
            | {_key(c.name_en): c.code for c in _ALL})
_ALIASES[_key("GN/YE")] = "YE/GN"


def parse_color(text: str) -> str | None:
    """Sigla canonica da 'RD', 'rd', 'Rosso', 'giallo-verde'...; None se sconosciuto."""
    return _ALIASES.get(_key(text))
