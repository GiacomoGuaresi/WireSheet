import copy

import pytest
from PySide6.QtWidgets import QApplication, QToolBar

from wiresheet.components import EndKind
from wiresheet.demo import demo_cables, demo_project
from wiresheet.model import End
from wiresheet.project_io import load_project
from wiresheet.colors import COLORS
from wiresheet.ui.cable_editor import COL_COLOR, COL_LENGTH, COL_P1, COL_P2
from wiresheet.ui.icons import ICON_NAMES, icon
from wiresheet.ui.main_window import COLLAPSE_ABOVE, MODE_SHEET, MainWindow


@pytest.fixture
def window(app):
    w = MainWindow()
    yield w
    w._dirty = False  # evita la domanda "salvare?" alla chiusura
    w.close()


def names(window):
    return [c.name for c in window.project.cables]


def layout_order(window):
    return [window.stack_layout.indexOf(card) - 1 for card in window.cards]  # 0 = cartiglio


# --- editor dentro la card ---------------------------------------------------

def test_default_cable_is_valid(window):
    card = window.cards[0]
    assert card.cable().validate() == []
    assert len(card.cable().wires) == 2
    assert not card.has_errors


def test_add_wire_picks_free_pins(window):
    ed = window.cards[0].editor
    ed.p1.set_positions(3)
    ed.p2.set_positions(3)
    ed._add_wire()
    wire = ed.cable("C").wires[-1]
    assert (wire.p1_pin, wire.p2_pin) == (3, 3)


def test_add_wire_grows_full_connector(window):
    ed = window.cards[0].editor  # XH-2 con 2 fili
    ed._add_wire()
    assert ed.p1.end().positions == 3 and ed.p2.end().positions == 3
    assert window.project.cables[0].validate() == []


def test_table_grows_with_rows(window):
    table = window.cards[0].editor.table
    before = table.height()
    window.cards[0].editor._add_wire()
    assert table.height() > before


def test_switch_p2_to_ferrules_clears_pins(window):
    ed = window.cards[0].editor
    ed.p2.kind.setCurrentIndex(ed.p2.kind.findData(EndKind.FERRULE))
    assert all(w.p2_pin is None for w in window.project.cables[0].wires)
    assert not ed.table.cellWidget(0, COL_P2).isEnabled()
    assert not ed.p2.variant.isEnabled()


def test_errors_shown_in_header(window):
    ed = window.cards[0].editor
    ed._add_wire()
    ed.p1.set_positions(2)  # 3 fili su XH-2
    assert window.cards[0].has_errors
    assert window.cards[0].status.text() == "2 errori"  # troppi fili + pin 3 non valido
    assert not ed.errors.isHidden()


# --- pila di card -------------------------------------------------------------

def test_edits_update_project(window):
    window.cards[0].name.setText("POW 55V")
    assert names(window) == ["POW 55V"]
    assert window._dirty
    assert window.windowTitle().endswith("*")


def test_add_inserts_below_active(window):
    window.add_cable()           # CABLE1, CABLE2
    window.set_active(0)
    window.add_cable()           # CABLE1, CABLE3, CABLE2
    assert names(window) == ["CABLE1", "CABLE3", "CABLE2"]
    assert window._active == 1
    assert layout_order(window) == [0, 1, 2]


def test_duplicate_copies_data_independently(window):
    window.cards[0].editor.p1.set_positions(4)
    window.duplicate_card(window.cards[0])
    assert names(window) == ["CABLE1", "CABLE2"]
    assert window.project.cables[1].p1.positions == 4
    window.cards[1].name.setText("CHANGED")
    assert names(window) == ["CABLE1", "CHANGED"]


def test_move_updates_project_and_layout(window):
    window.add_cable()
    window.add_cable()           # CABLE1, CABLE2, CABLE3
    window.move_card(window.cards[2], -1)
    assert names(window) == ["CABLE1", "CABLE3", "CABLE2"]
    assert [c.cable().name for c in window.cards] == names(window)
    assert layout_order(window) == [0, 1, 2]
    window.move_card(window.cards[0], -1)  # gia' in cima: nessun effetto
    assert names(window) == ["CABLE1", "CABLE3", "CABLE2"]


def test_delete(window):
    window.add_cable()
    window.delete_card(window.cards[1], confirm=False)
    assert names(window) == ["CABLE1"]
    assert not window.cards[0].delete_button.isEnabled()
    window.delete_card(window.cards[0], confirm=False)  # l'ultimo resta
    assert names(window) == ["CABLE1"]


def test_active_card_follows_edits(window):
    window.add_cable()
    window.set_active(0)
    window.cards[1].name.setText("X")
    assert window._active == 1
    assert window.cards[1].property("active") and not window.cards[0].property("active")


def test_collapse_and_expand(window):
    card = window.cards[0]
    card.set_expanded(False)
    assert card.editor.isHidden()
    window.set_all_expanded(True)
    assert not card.editor.isHidden()


def test_large_project_opens_collapsed(window):
    project = demo_project()
    project.cables = [copy.deepcopy(c) for c in demo_cables() * 2]
    assert len(project.cables) > COLLAPSE_ABOVE
    window.set_project(project, None)
    assert all(c.editor.isHidden() for c in window.cards)


# --- anteprima ----------------------------------------------------------------

def test_preview_hidden_by_default_and_toggles(window):
    assert window.preview_panel.isHidden()
    window.act_preview.setChecked(True)
    assert not window.preview_panel.isHidden()
    assert window.preview._cable == window.project.cables[0]
    window.act_preview.setChecked(False)
    assert window.preview_panel.isHidden()


def test_preview_follows_active_card(window):
    window.act_preview.setChecked(True)
    window.add_cable()
    assert window.preview._cable.name == "CABLE2"
    window.set_active(0)
    assert window.preview._cable.name == "CABLE1"


def test_sheet_preview_finds_page(window):
    project = demo_project()
    project.cables = []
    for i in range(15):
        c = copy.deepcopy(demo_cables()[i % 5])
        c.name = f"CABLE{i + 1}"
        project.cables.append(c)
    window.set_project(project, None)
    window.act_preview.setChecked(True)
    window.set_preview_mode(MODE_SHEET)
    window.set_active(14)
    from wiresheet.render.sheet_layout import layout_pages, sheet_geometry
    n = len(layout_pages(project.cables, sheet_geometry()))
    assert n >= 2
    assert window.page_label.text().strip() == f"Foglio {n} di {n}"
    _, placements, _, page, pages = window.preview._page
    assert (page, pages) == (n, n)
    assert any(p.cable is window.project.cables[14] for p in placements)


def test_invalid_cable_preview_shows_message(window):
    window.act_preview.setChecked(True)
    ed = window.cards[0].editor
    ed._add_wire()
    ed.p1.set_positions(2)
    assert window.preview._cable is None and window.preview._page is None


# --- file -----------------------------------------------------------------------

def test_save_and_open(window, tmp_path):
    window.title_edit.setText("Stampante")
    window.project.drawn_by = "DM"
    window.add_cable()
    path = tmp_path / "pn2.wiresheet"
    assert window.save_to(path)
    assert not window._dirty
    assert load_project(path) == window.project

    other = MainWindow()
    other.open_path(path)
    assert other.project == window.project
    assert other.title_edit.text() == "Stampante"
    assert other.project.drawn_by == "DM"
    assert other.project.revision == 1   # primo salvataggio
    assert len(other.cards) == 2
    assert not other._dirty
    other.close()


def test_open_invalid_file_keeps_project(window, tmp_path, monkeypatch):
    bad = tmp_path / "bad.wiresheet"
    bad.write_text("not json", encoding="utf-8")
    monkeypatch.setattr("wiresheet.ui.main_window.QMessageBox.critical", lambda *a: None)
    before = window.project
    window.open_path(bad)
    assert window.project is before


def test_set_project_rebuilds_cards(window):
    window.set_project(demo_project(), None)
    assert len(window.cards) == len(demo_cables())
    assert [c.cable() for c in window.cards] == window.project.cables
    assert window.title_edit.text() == "Cavi di esempio"


# --- nuova UI: linguetta, varianti, colonne, colori, icone ---------------------

def test_side_tab_toggles_preview(window):
    window.preview_tab.click()
    assert not window.preview_panel.isHidden() and window.act_preview.isChecked()
    window.preview_tab.click()
    assert window.preview_panel.isHidden() and not window.preview_tab.isChecked()
    window.act_preview.setChecked(True)  # F2 / menu Vista
    assert window.preview_tab.isChecked()


def test_variant_lists_pin_counts(window):
    p1 = window.cards[0].editor.p1
    assert [p1.variant.itemText(i) for i in range(p1.variant.count())] ==         [f"{n} pin" for n in range(2, 8)]
    p1.set_positions(5)
    assert window.project.cables[0].p1.positions == 5
    assert p1.thumbnail._positions == 5


def test_gm_variants_and_kind_switch(window):
    p1 = window.cards[0].editor.p1
    p1.set_positions(4)
    p1.kind.setCurrentIndex(p1.kind.findData(EndKind.GM2112))
    assert window.project.cables[0].p1 == End(EndKind.GM2112, 4, "S4")  # tiene i pin
    texts = [p1.variant.itemText(i) for i in range(p1.variant.count())]
    assert "S5A · 5 pin femmina" in texts and "P12 · 12 pin maschio" in texts
    p1.set_positions(10)  # non esiste: passa alla prima variante piu' grande, stesso genere
    assert p1.end() == End(EndKind.GM2112, 12, "S12")


def test_add_wire_grows_gm_connector(window):
    ed = window.cards[0].editor
    ed.p1.set_end(End(EndKind.GM1312, 7, "P7"))
    ed._on_ends_changed()
    while ed.table.rowCount() < 8:
        ed._add_wire()
    assert ed.p1.end() == End(EndKind.GM1312, 9, "P9")


def test_thumbnail_follows_kind(window):
    p2 = window.cards[0].editor.p2
    p2.kind.setCurrentIndex(p2.kind.findData(EndKind.FORK))
    assert p2.thumbnail._kind is EndKind.FORK


def test_back_to_connector_keeps_valid_pins(window):
    p2 = window.cards[0].editor.p2
    p2.kind.setCurrentIndex(p2.kind.findData(EndKind.FLAT_CUT))
    p2.kind.setCurrentIndex(p2.kind.findData(EndKind.JST_XH))
    assert window.project.cables[0].validate() == []


def test_column_order(window):
    table = window.cards[0].editor.table
    headers = [table.horizontalHeaderItem(c).text() for c in range(6)]
    assert headers == ["Pin P1", "Colore", "Lunghezza (mm)", "Sezione", "Ramo", "Pin P2"]
    assert (COL_P1, COL_COLOR, COL_LENGTH, COL_P2) == (0, 1, 2, 5)


def test_section_kept_and_copied_to_new_wire(window):
    from wiresheet.model import Cable, End, Wire
    from wiresheet.components import EndKind
    ed = window.cards[0].editor
    ed.load(Cable("C", End(EndKind.JST_XH, 2), End(EndKind.FERRULE),
                  [Wire("RD", 300, 1, None, 0.3, None), Wire("BK", 300, 2, None, None, 22)]))
    wires = ed.cable("C").wires
    assert [(w.section_mm2, w.awg) for w in wires] == [(0.3, None), (None, 22)]  # restano cosi'
    from wiresheet.ui.cable_editor import COL_SECTION
    combo = ed.table.cellWidget(0, COL_SECTION)
    assert combo.currentText() == "0.3mm² (22AWG)"
    assert combo.itemText(4) == "0.25mm² (24AWG)"
    combo.setCurrentIndex(4)
    assert (ed.cable("C").wires[0].section_mm2, ed.cable("C").wires[0].awg) == (0.25, 24)
    ed._add_wire()
    assert ed.cable("C").wires[-1].awg == 22


def test_color_combo_has_swatches(window):
    combo = window.cards[0].editor.table.cellWidget(0, COL_COLOR)
    assert combo.count() == len(COLORS)
    assert all(not combo.itemIcon(i).isNull() for i in range(combo.count()))
    assert combo.currentText() == "RD"


@pytest.mark.parametrize("name", ICON_NAMES)
def test_icons_render(app, name):
    assert not icon(name).pixmap(24, 24).toImage().isNull()
    assert not icon(name).isNull()


# --- import da Excel/CSV --------------------------------------------------------

def test_apply_import_append(window):
    window.apply_import(demo_cables(), replace=False)
    assert len(window.cards) == 1 + len(demo_cables())
    assert window.project.cables[1:] == demo_cables()
    assert window._active == 1
    assert window._dirty


def test_apply_import_replace(window):
    window.apply_import(demo_cables(), replace=True)
    assert window.project.cables == demo_cables()
    assert [c.cable() for c in window.cards] == demo_cables()



# --- rami ----------------------------------------------------------------------

def _fans(window):
    from wiresheet.demo import demo_cables
    fans = next(c for c in demo_cables() if c.name == "FANS, MAT SENSOR")
    window.apply_import([fans], replace=True)
    return fans, window.cards[0]


def test_branched_cable_round_trips_through_card(window):
    from wiresheet.ui.cable_editor import COL_BRANCH
    fans, card = _fans(window)
    assert card.cable() == fans
    assert not card.has_errors
    ed = card.editor
    assert len(ed.branch_rows) == 3 and not ed.table.isColumnHidden(COL_BRANCH)
    assert ed.p2_title.text() == "P2 — rami in uscita"
    assert "→ XH-2, TB-3, Taglio netto" in card.summary.text()


def test_simple_cable_hides_branch_ui(window):
    from wiresheet.ui.cable_editor import COL_BRANCH
    ed = window.cards[0].editor
    assert len(ed.branch_rows) == 1
    assert ed.table.isColumnHidden(COL_BRANCH)
    assert ed.branch_rows[0].name.isHidden() and ed.branch_rows[0].remove.isHidden()


def test_add_branch_and_move_wire(window):
    from wiresheet.components import EndKind
    from wiresheet.ui.cable_editor import COL_BRANCH
    ed = window.cards[0].editor                       # XH-2 -> XH-2, 2 fili
    ed._add_branch()
    assert len(ed.branch_rows) == 2
    assert "P2 ramo B: ramo senza fili." in ed.cable("C").validate()
    assert ed.branch_rows[1].number.text() == "Branch B"
    assert ed.table.cellWidget(0, COL_BRANCH).itemText(1) == "Branch B"
    branch = ed.branch_rows[1]
    branch.name.setText("Fan")
    branch.end_editor.kind.setCurrentIndex(branch.end_editor.kind.findData(EndKind.FLAT_CUT))
    ed.table.cellWidget(1, COL_BRANCH).setCurrentIndex(1)  # secondo filo nel ramo "Fan"
    cable = window.project.cables[0]
    assert [(b.name, b.end.kind, len(b.wires)) for b in cable.branches] == [
        ("", EndKind.JST_XH, 1), ("Fan", EndKind.FLAT_CUT, 1)]
    assert cable.branches[1].wires[0].p2_pin is None
    assert cable.validate() == []
    assert ed.table.cellWidget(0, COL_BRANCH).itemText(1) == "B. Fan"


def test_new_wire_goes_to_last_branch(window):
    fans, card = _fans(window)
    card.editor._add_wire()
    cable = window.project.cables[0]
    assert [len(b.wires) for b in cable.branches] == [2, 3, 3]   # aggiunto a Extruder fan
    assert cable.p1.positions == 9                                 # GM S7 pieno -> S9


def test_remove_branch_moves_wires_to_first(window):
    fans, card = _fans(window)
    ed = card.editor
    ed._remove_branch(ed.branch_rows[1])              # Material sensor
    cable = window.project.cables[0]
    assert [b.name for b in cable.branches] == ["Cooling fan", "Extruder fan"]
    assert [len(b.wires) for b in cable.branches] == [5, 2]
    ed._remove_branch(ed.branch_rows[1])
    assert not window.project.cables[0].is_branched
    assert ed.branch_rows[0].name.isHidden()


def test_title_block_fields(window):
    window.set_preview_mode(MODE_SHEET)
    window.apply_title_block({"title": "Pannello", "company": "ACME Srl", "revision": 4})
    assert window.project.title == "Pannello" and window.project.revision == 4
    assert window.title_edit.text() == "Pannello"
    assert window._dirty


def test_title_block_card_edits_project(window):
    card = window.title_card
    assert window.stack_layout.indexOf(card) == 0     # in cima, prima dei cavi
    assert window.stack_layout.indexOf(window.cards[0]) == 1
    card.edits["drawn_by"].setText("DM")
    card.revision.setValue(7)
    assert window.project.drawn_by == "DM" and window.project.revision == 7
    assert window._dirty
    assert set(card.values()) == {"title", "company", "machine", "revision", "date", "drawn_by"}


def test_revision_shown_after_save(window, tmp_path):
    window.save_to(tmp_path / "rev.wiresheet")
    assert window.title_card.revision.value() == 1


def test_menus_hold_the_actions(window):
    menus = {m.title().replace("&", ""): [a.text() for a in m.actions() if a.text()]
             for m in (a.menu() for a in window.menuBar().actions())}
    assert list(menus) == ["File", "Importa/Esporta", "Ordina", "Vista", "Aiuto"]
    assert "Nuovo cavo" in menus["File"]
    assert menus["Importa/Esporta"][0] == "Esporta PDF…"
    assert "Importa cavi da Excel/CSV…" in menus["Importa/Esporta"]
    assert menus["Ordina"][0] == "Nome (A → Z)"
    assert menus["Aiuto"] == ["Controlla aggiornamenti…", "Controlla aggiornamenti all'avvio",
                              "Informazioni su WireSheet"]
    assert not window.findChildren(QToolBar)


def test_revision_bumps_only_on_saves_with_changes(window, tmp_path):
    path = tmp_path / "rev.wiresheet"
    assert window.project.revision == 0
    window.save_to(path)
    assert window.project.revision == 1          # primo salvataggio
    window.save_to(path)
    window.save_to(path)
    assert window.project.revision == 1          # Ctrl+S ripetuto senza modifiche
    window.title_edit.setText("Modificato")
    window.save_to(path)
    assert window.project.revision == 2
    assert load_project(path).revision == 2


def test_manual_revision_is_kept(window, tmp_path):
    path = tmp_path / "rev.wiresheet"
    window.save_to(path)
    window.apply_title_block({"revision": 10})
    window.save_to(path)
    assert window.project.revision == 10         # cambiata a mano: non sale
    window.title_edit.setText("Altro")
    window.save_to(path)
    assert window.project.revision == 11


def test_export_asks_to_save_first(window, tmp_path, monkeypatch):
    from PySide6.QtWidgets import QMessageBox
    asked = []
    monkeypatch.setattr("wiresheet.ui.main_window.QMessageBox.question",
                        lambda *a: asked.append(a[2]) or QMessageBox.StandardButton.Cancel)
    monkeypatch.setattr("wiresheet.ui.main_window.QFileDialog.getSaveFileName",
                        lambda *a: pytest.fail("export senza salvare"))
    window.export()
    assert asked and "revisione 1" in asked[0]
    window.save_to(tmp_path / "rev.wiresheet")
    asked.clear()
    monkeypatch.setattr("wiresheet.ui.main_window.QFileDialog.getSaveFileName", lambda *a: ("", ""))
    window.export()
    assert not asked                             # salvato: nessuna domanda


def test_branch_label_checkbox(window):
    window.set_project(demo_project(), None)
    index = next(i for i, c in enumerate(window.project.cables) if c.name == "FANS, MAT SENSOR")
    editor = window.cards[index].editor
    assert editor.branch_rows[0].label.isChecked()
    editor.branch_rows[0].label.setChecked(False)
    assert window.project.cables[index].branches[0].label is False
    assert window._dirty


def test_sort_cables(window):
    from wiresheet.ui.main_window import SORT_OPTIONS, natural_key
    assert natural_key("CABLE2") < natural_key("cable10")
    project = demo_project()
    window.set_project(project, None)
    window.set_active(2)
    active = window.cards[2]
    by = {label: (key, rev) for label, key, rev in SORT_OPTIONS}
    window.sort_cables(*by["Nome (Z → A)"])
    names = [c.name for c in window.project.cables]
    assert names == sorted(names, key=natural_key, reverse=True)
    assert [c.cable().name for c in window.cards] == names          # card nello stesso ordine
    assert layout_order(window) == list(range(len(names)))
    assert window.cards[window._active] is active and window._dirty
    window.sort_cables(*by["Numero di fili (dal più grande)"])
    counts = [len(c.wires) for c in window.project.cables]
    assert counts == sorted(counts, reverse=True)



def test_hover_activates_card(window):
    from PySide6.QtCore import QPointF
    from PySide6.QtGui import QEnterEvent
    window.add_cable()
    window.set_active(0)
    card = window.cards[1]
    QApplication.sendEvent(card, QEnterEvent(QPointF(5, 5), QPointF(5, 5), QPointF(5, 5)))
    assert window._active == 1


def test_app_icon_files():
    from PySide6.QtGui import QIcon
    from wiresheet.__main__ import ICON
    assert not QIcon(str(ICON)).isNull()
    assert QIcon(str(ICON.with_suffix(".ico"))).availableSizes()
