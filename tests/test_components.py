import math

import pytest

from wiresheet.components import (GM_LAYOUTS, EndKind, end_codes, gm_code, gm_layout, gm_variants,
                                 parse_gm_variant,
                                 parse_kind, variant_positions)


@pytest.mark.parametrize("kind", list(GM_LAYOUTS))
def test_layouts_have_one_point_per_pin(kind):
    for key, layout in GM_LAYOUTS[kind].items():
        assert len(layout) == variant_positions(key)
        for x, y, _ in layout:
            assert math.hypot(x, y) < 0.75  # dentro la faccia del connettore


@pytest.mark.parametrize("kind", list(GM_LAYOUTS))
def test_pins_do_not_overlap(kind):
    for layout in GM_LAYOUTS[kind].values():
        for i, (x1, y1, _) in enumerate(layout):
            for x2, y2, _ in layout[i + 1:]:
                assert math.hypot(x1 - x2, y1 - y2) > 0.3


def test_male_is_mirrored():
    female = gm_layout(EndKind.GM1312, "S2")
    male = gm_layout(EndKind.GM1312, "P2")
    assert male == tuple((-x, y, d) for x, y, d in female)


def test_variants():
    assert gm_variants(EndKind.GM1712)[:3] == ["S2", "S3", "S4"]
    assert "S6" not in gm_variants(EndKind.GM1712)
    assert {"S5A", "S5B", "S5C", "S12"} <= set(gm_variants(EndKind.GM2112))
    assert variant_positions("P5A") == 5


@pytest.mark.parametrize("text, expected", [
    ("S4", "S4"), ("s-4p", "S4"), ("P 5a", "P5A"), ("S5", None), ("4", None), ("X4", None),
])
def test_parse_gm_variant(text, expected):
    assert parse_gm_variant(EndKind.GM2112, text) == expected


def test_parse_gm_kind():
    assert parse_kind("GM-2112") is EndKind.GM2112
    assert parse_kind("gm1312") is EndKind.GM1312


@pytest.mark.parametrize("kind, variant, code", [
    (EndKind.GM1312, "S2", "GM-1312/S-2P"),
    (EndKind.GM2112, "S5A", "GM-2112/S-5P-A"),
    (EndKind.GM1712, "P9", "GM-1712/P-9P"),
])
def test_gm_code(kind, variant, code):
    assert gm_code(kind, variant) == code
    assert end_codes(kind, 0, variant)[0] == code


def test_new_kinds():
    assert parse_kind("Morsettiera") is EndKind.TERMINAL_BLOCK
    assert parse_kind("terminal block") is EndKind.TERMINAL_BLOCK
    assert parse_kind("Faston F") is EndKind.FASTON_F
    assert parse_kind("faston") is EndKind.FASTON_F
    assert end_codes(EndKind.TERMINAL_BLOCK, 8) == ["TB 5.08-8P", "PLUGGABLE, SCREW"]
    assert end_codes(EndKind.FASTON_F) == ["FASTON F 6.3"]
