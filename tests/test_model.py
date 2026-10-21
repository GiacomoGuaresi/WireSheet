from wiresheet.components import EndKind
from wiresheet.model import Branch, Cable, End, Project, Wire


def xh(n: int) -> End:
    return End(EndKind.JST_XH, n)


def test_valid_point_to_point():
    c = Cable("C", xh(2), xh(2), [Wire("RD", 350, 1, 2), Wire("BK", 350, 2, 1)])
    assert c.validate() == []


def test_valid_connector_to_ferrules_ignores_p2_pins():
    c = Cable("C", xh(3), End(EndKind.FERRULE), [Wire("RD", 200, 1), Wire("BK", 200, 2)])
    assert c.validate() == []


def test_length_is_longest_wire():
    c = Cable("C", xh(2), End(EndKind.FLAT_CUT), [Wire("RD", 200, 1), Wire("BK", 250, 2)])
    assert c.length_mm == 250


def test_pin_out_of_range():
    c = Cable("C", xh(2), xh(2), [Wire("RD", 350, 3, 1)])
    assert any("pin non valido" in e for e in c.validate())


def test_missing_pin_on_connector():
    c = Cable("C", xh(2), xh(2), [Wire("RD", 350, 1, None)])
    assert any("P2" in e for e in c.validate())


def test_duplicate_pin():
    c = Cable("C", xh(3), xh(3), [Wire("RD", 350, 1, 1), Wire("BK", 350, 1, 2)])
    assert any("usato piu' volte" in e for e in c.validate())


def test_too_many_wires():
    wires = [Wire("RD", 100, i, i) for i in range(1, 4)]
    assert any("3 fili" in e for e in Cable("C", xh(2), xh(2), wires).validate())


def test_unsupported_positions():
    c = Cable("C", xh(8), End(EndKind.FORK), [Wire("RD", 100, 1)])
    assert any("non supportato" in e for e in c.validate())


def test_unknown_color_and_bad_length():
    errors = Cable("C", xh(2), xh(2), [Wire("XX", 0, 1, 1)]).validate()
    assert len(errors) == 2


def test_no_wires():
    assert Cable("C", xh(2), xh(2), []).validate() == ["Il cavo non ha fili."]


def test_next_cable_name():
    p = Project(cables=[Cable("CABLE3", xh(2), xh(2)), Cable("SPECIAL", xh(2), xh(2)),
                        Cable("CABLE10", xh(2), xh(2))])
    assert p.next_cable_name() == "CABLE11"
    assert Project().next_cable_name() == "CABLE1"


def test_gm_connector():
    gm = End(EndKind.GM2112, 4, "S4")
    assert gm.is_connector
    assert Cable("C", gm, End(EndKind.FERRULE), [Wire("RD", 300, 4)]).validate() == []
    assert any("pin non valido" in e for e in
               Cable("C", gm, End(EndKind.FERRULE), [Wire("RD", 300, 5)]).validate())


def test_gm_unknown_variant():
    bad = End(EndKind.GM1712, 6, "S6")  # il 6 pin esiste solo nella serie 13
    errors = Cable("C", bad, End(EndKind.FORK), [Wire("RD", 100, 1)]).validate()
    assert any("non supportato" in e for e in errors)


def test_terminal_block_positions():
    ok = Cable("C", End(EndKind.TERMINAL_BLOCK, 8), End(EndKind.FASTON_F), [Wire("RD", 100, 8)])
    assert ok.validate() == []
    bad = Cable("C", End(EndKind.TERMINAL_BLOCK, 9), End(EndKind.FORK), [Wire("RD", 100, 1)])
    assert any("non supportato" in e for e in bad.validate())


def _fans() -> Cable:
    return Cable("FANS", End(EndKind.GM1712, 7, "S7"), branches=[
        Branch(xh(2), [Wire("RD", 800, 1, 1), Wire("BK", 800, 2, 2)], "Cooling fan"),
        Branch(End(EndKind.FLAT_CUT), [Wire("RD", 1000, 6), Wire("BK", 1000, 7)], "Extruder fan"),
    ])


def test_simple_cable_has_one_branch():
    c = Cable("C", xh(2), End(EndKind.FERRULE), [Wire("RD", 100, 1)])
    assert len(c.branches) == 1 and not c.is_branched
    assert c.p2 == End(EndKind.FERRULE) and c.wires == c.branches[0].wires


def test_branched_cable_is_valid_and_flattens_wires():
    c = _fans()
    assert c.is_branched and c.validate() == []
    assert [w.p1_pin for w in c.wires] == [1, 2, 6, 7]
    assert c.length_mm == 1000


def test_p1_pins_checked_across_branches():
    c = _fans()
    c.branches[1].wires[0].p1_pin = 1
    assert any("P1: pin 1 usato" in e for e in c.validate())


def test_branch_titles():
    from wiresheet.model import branch_title
    assert branch_title("Cooling fan", 0) == "A. Cooling fan"
    assert branch_title("", 1) == "Branch B"


def test_branch_errors_name_the_branch():
    c = _fans()
    c.branches[0].wires[0].p2_pin = 5
    c.branches[1].wires.clear()
    errors = c.validate()
    assert any(e.startswith("P2 ramo 'Cooling fan': filo 1") for e in errors)
    assert "P2 ramo 'Extruder fan': ramo senza fili." in errors


def test_section_validation():
    ok = Cable("C", xh(2), End(EndKind.FERRULE), [Wire("RD", 100, 1, None, 0.25, 24)])
    assert ok.validate() == []
    bad = Cable("C", xh(2), End(EndKind.FERRULE), [Wire("RD", 100, 1, None, -1, 99)])
    assert bad.validate() == ["Filo 1: sezione non valida.", "Filo 1: AWG 99 non supportato (8-30)."]
