"""Salvataggio e apertura dei progetti (.wiresheet, JSON)."""

import json
from dataclasses import asdict
from pathlib import Path

from wiresheet.components import EndKind
from wiresheet.model import Branch, Cable, End, Project, Wire

FILE_EXTENSION = ".wiresheet"
LEGACY_EXTENSION = ".cablegen"  # progetti salvati quando il programma si chiamava CableGen
FORMAT_VERSION = 2  # 2: cavi con i rami ("branches") al posto di p2 + wires
TEXT_FIELDS = ("title", "company", "machine", "date", "drawn_by")  # campi testo del cartiglio


def project_to_dict(project: Project) -> dict:
    return {
        "format": "wiresheet",
        "version": FORMAT_VERSION,
        **{name: getattr(project, name) for name in TEXT_FIELDS},
        "revision": project.revision,
        "cables": [
            {
                "name": c.name,
                "p1": _end_to_dict(c.p1),
                "branches": [
                    {"name": b.name, "label": b.label, "end": _end_to_dict(b.end),
                     "wires": [asdict(w) for w in b.wires]}
                    for b in c.branches
                ],
            }
            for c in project.cables
        ],
    }


def project_from_dict(data: dict) -> Project:
    if data.get("format") not in ("wiresheet", "cablegen"):
        raise ValueError("Il file non è un progetto WireSheet.")
    if data.get("version", 0) > FORMAT_VERSION:
        raise ValueError("Il progetto è stato creato con una versione più recente di WireSheet.")
    # il vecchio campo "pn" (riquadro P/N) non esiste piu' e viene ignorato
    return Project(
        **{name: str(data.get(name, "")) for name in TEXT_FIELDS},
        revision=_revision(data.get("revision", 0)),
        cables=[_cable_from_dict(c) for c in data.get("cables", [])],
    )


def _revision(value) -> int:
    """Revisione come numero; valori non numerici (es. "A") ripartono da 0."""
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _cable_from_dict(c: dict) -> Cable:
    if "branches" not in c:  # versione 1: un solo ramo
        c = {**c, "branches": [{"name": "", "end": c["p2"], "wires": c["wires"]}]}
    branches = [Branch(_end_from_dict(b["end"]), [Wire(**w) for w in b["wires"]], b.get("name", ""),
                       bool(b.get("label", True)))
                for b in c["branches"]]
    return Cable(c["name"], _end_from_dict(c["p1"]), branches=branches)


def save_project(project: Project, path: str | Path) -> None:
    Path(path).write_text(json.dumps(project_to_dict(project), indent=2, ensure_ascii=False),
                          encoding="utf-8")


def load_project(path: str | Path) -> Project:
    return project_from_dict(json.loads(Path(path).read_text(encoding="utf-8")))


def _end_to_dict(end: End) -> dict:
    data = {"kind": end.kind.value, "positions": end.positions}
    if end.variant:
        data["variant"] = end.variant
    return data


def _end_from_dict(data: dict) -> End:
    return End(EndKind(data["kind"]), data.get("positions", 0), data.get("variant", ""))
