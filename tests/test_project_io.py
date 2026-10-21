import json

import pytest

from wiresheet.demo import demo_project
from wiresheet.model import Project
from wiresheet.project_io import load_project, project_from_dict, project_to_dict, save_project


def test_round_trip(tmp_path):
    project = demo_project()
    path = tmp_path / "p.wiresheet"
    save_project(project, path)
    assert load_project(path) == project


def test_file_is_readable_json(tmp_path):
    path = tmp_path / "p.wiresheet"
    save_project(demo_project(), path)
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["format"] == "wiresheet" and data["version"] == 2
    assert data["cables"][0]["p1"] == {"kind": "jst_xh", "positions": 2}


def test_non_ascii_title(tmp_path):
    path = tmp_path / "p.wiresheet"
    save_project(Project(title="Cablaggio stampante — è"), path)
    assert load_project(path).title == "Cablaggio stampante — è"


def test_title_block_fields_saved(tmp_path):
    path = tmp_path / "p.wiresheet"
    project = Project(title="T", company="Ginger Additive", machine="G1", revision=3,
                      date="2026-10-20", drawn_by="DM")
    save_project(project, path)
    assert load_project(path) == project
    assert "pn" not in project_to_dict(project)


def test_old_pn_is_ignored():
    data = {"format": "wiresheet", "version": 2, "pn": "1", "title": "Vecchio", "cables": []}
    project = project_from_dict(data)
    assert project.title == "Vecchio" and project.revision == 0
    data["revision"] = "A"  # revisioni a lettera dei primi file di prova
    assert project_from_dict(data).revision == 0


def test_legacy_cablegen_file_is_read(tmp_path):
    data = project_to_dict(demo_project())
    data["format"] = "cablegen"  # file salvati quando il programma si chiamava CableGen
    path = tmp_path / "vecchio.cablegen"
    path.write_text(json.dumps(data), encoding="utf-8")
    assert load_project(path) == demo_project()


def test_rejects_other_files():
    with pytest.raises(ValueError):
        project_from_dict({"cables": []})


def test_rejects_newer_version():
    data = project_to_dict(demo_project())
    data["version"] = 99
    with pytest.raises(ValueError):
        project_from_dict(data)


def test_reads_version_1_files():
    data = {"format": "wiresheet", "version": 1, "pn": "1", "title": "", "cables": [{
        "name": "C1", "p1": {"kind": "jst_xh", "positions": 2},
        "p2": {"kind": "ferrule", "positions": 0},
        "wires": [{"color": "RD", "length_mm": 300, "p1_pin": 1, "p2_pin": None}]}]}
    cable = project_from_dict(data).cables[0]
    assert not cable.is_branched and cable.p2.kind.value == "ferrule"
    assert cable.wires[0].length_mm == 300


def test_branches_saved_with_names(tmp_path):
    data = project_to_dict(demo_project())
    fans = next(c for c in data["cables"] if c["name"] == "FANS, MAT SENSOR")
    assert [b["name"] for b in fans["branches"]] == ["Cooling fan", "Material sensor", "Extruder fan"]
    assert "p2" not in fans and "wires" not in fans


def test_branch_label_flag_saved(tmp_path):
    project = demo_project()
    fans = next(c for c in project.cables if c.name == "FANS, MAT SENSOR")
    fans.branches[0].label = False
    path = tmp_path / "p.wiresheet"
    save_project(project, path)
    loaded = next(c for c in load_project(path).cables if c.name == "FANS, MAT SENSOR")
    assert [b.label for b in loaded.branches] == [False, True, True]
