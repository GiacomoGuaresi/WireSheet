import pytest

from wiresheet.gauges import awg_to_mm2, mm2_to_awg, parse_section, section_text


@pytest.mark.parametrize("mm2,awg", [(0.14, 26), (0.25, 24), (0.34, 22), (0.38, 21), (0.5, 20),
                                     (0.75, 18), (1.0, 17), (1.5, 16), (2.5, 14), (4.0, 12)])
def test_commercial_equivalents(mm2, awg):
    assert mm2_to_awg(mm2) == awg


def test_awg_to_mm2_uses_table_then_nearest():
    assert awg_to_mm2(18) == 0.75
    assert awg_to_mm2(17) == 1.0
    assert awg_to_mm2(19) in (0.5, 0.75)   # non in tabella: la misura metrica piu' vicina
    assert mm2_to_awg(0.3) == 22


def test_section_text_shows_both_units():
    assert section_text(0.25, None) == "0.25mm² (24AWG)"
    assert section_text(None, 20) == "0.5mm² (20AWG)"
    assert section_text(1.5, 15) == "1.5mm² (15AWG)"   # entrambe indicate: restano cosi'
    assert section_text(None, None) == ""


def test_section_cell_keeps_only_given_units():
    from wiresheet.gauges import section_cell
    assert section_cell(0.25, None) == "0.25mm²"
    assert section_cell(None, 24) == "24AWG"
    assert section_cell(0.25, 24) == "0.25mm² (24AWG)"
    assert section_cell(None, None) == ""


@pytest.mark.parametrize("text,expected", [
    ("0,25", (0.25, None)), ("0.5 mm²", (0.5, None)), ("AWG24", (None, 24)), ("24 awg", (None, 24)),
    ("0.25mm² (24AWG)", (0.25, 24)), ("1,5 mm2 (15 AWG)", (1.5, 15)),
    ("", (None, None)), (None, (None, None)), (0.75, (0.75, None)), ("boh", None), ("AWG3", None),
])
def test_parse_section(text, expected):
    assert parse_section(text) == expected
