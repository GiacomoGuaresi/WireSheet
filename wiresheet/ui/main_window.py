"""Finestra principale: menu | pila di card (cartiglio + una per cavo) | anteprima apribile."""

import copy
import re
from datetime import date
from pathlib import Path

from PySide6.QtCore import QSettings, QSize, Qt, QTimer, QUrl
from PySide6.QtGui import QAction, QCloseEvent, QDesktopServices, QKeySequence
from PySide6.QtWidgets import (QApplication, QButtonGroup, QFileDialog, QHBoxLayout, QLabel,
                               QLineEdit, QMainWindow, QMessageBox, QPushButton, QScrollArea,
                               QSizePolicy, QSplitter, QToolButton, QVBoxLayout,
                               QWidget)

from wiresheet import RELEASES_URL, __version__
from wiresheet.components import KIND_LABELS, EndKind
from wiresheet.model import Cable, End, Project, Wire
from wiresheet.pdf_export import export_pdf
from wiresheet.project_io import FILE_EXTENSION, LEGACY_EXTENSION, load_project, save_project
from wiresheet.render.sheet_layout import layout_pages, sheet_geometry
from wiresheet.table_io import example_cables, import_table, write_table
from wiresheet.ui.cable_card import CableCard
from wiresheet.ui.preview import CablePreview
from wiresheet.ui.title_block_card import TitleBlockCard
from wiresheet.ui.update_check import UpdateChecker
from wiresheet.ui.icons import icon, toggle_icon
from wiresheet.ui.style import ACCENT, STYLE
from wiresheet.ui.widgets import SideTab

FILE_FILTER = f"Progetto WireSheet (*{FILE_EXTENSION})"
OPEN_FILTER = f"Progetto WireSheet (*{FILE_EXTENSION} *{LEGACY_EXTENSION})"
TABLE_FILTER = "Excel (*.xlsx);;CSV (*.csv)"
COLLAPSE_ABOVE = 5  # all'apertura, card compresse se i cavi sono piu' di cosi'
MODE_CABLE, MODE_SHEET = "cable", "sheet"
CARDS_MIN_WIDTH = 680
FIRST_CARD = 1  # nella pila il cartiglio occupa il posto 0, i cavi seguono
AUTO_UPDATE_KEY = "updates/check_on_startup"


def natural_key(text: str) -> list:
    """Ordine 'naturale': CABLE2 prima di CABLE10, senza distinguere maiuscole."""
    return [int(part) if part.isdigit() else part for part in re.split(r"(\d+)", text.casefold())]


# menu Cavi > Ordina: (voce, chiave, decrescente)
SORT_OPTIONS = [
    ("Nome (A → Z)", lambda c: natural_key(c.name), False),
    ("Nome (Z → A)", lambda c: natural_key(c.name), True),
    ("Componente P1", lambda c: (KIND_LABELS[c.p1.kind], c.p1.positions, c.p1.variant,
                                 natural_key(c.name)), False),
    ("Numero di fili (dal più grande)", lambda c: len(c.wires), True),
    ("Lunghezza (dal più lungo)", lambda c: c.length_mm, True),
]


def default_cable(name: str) -> Cable:
    return Cable(name, End(EndKind.JST_XH, 2), End(EndKind.JST_XH, 2),
                 [Wire("RD", 300, 1, 1), Wire("BK", 300, 2, 2)])


def new_project() -> Project:
    return Project(date=date.today().isoformat(), cables=[default_cable("CABLE1")])


def file_stem(project: Project) -> str:
    """Nome proposto per i file: il titolo senza i caratteri vietati, oppure 'progetto'."""
    stem = re.sub(r'[<>:"/\\|?*]', "", project.title).strip()
    return stem or "progetto"


class MainWindow(QMainWindow):
    def __init__(self, project: Project | None = None):
        super().__init__()
        self.resize(1300, 800)
        self.setStyleSheet(STYLE)
        self.project = project or new_project()
        self.cards: list[CableCard] = []
        self._active = -1
        self._path: Path | None = None
        self._dirty = False
        self._saved_revision = self.project.revision  # revisione dell'ultimo salvataggio
        self._preview_mode = MODE_CABLE
        self._settings = QSettings()
        self._updates = UpdateChecker(self)
        self._updates.found.connect(self._on_update_found)
        self._updates.up_to_date.connect(self._on_up_to_date)
        self._updates.failed.connect(self._on_update_failed)
        self._silent_check = False

        self._build_actions()
        self._build_menu()

        # --- pila di card ---
        self.stack = QWidget()
        self.stack.setObjectName("stack")
        self.stack_layout = QVBoxLayout(self.stack)
        self.stack_layout.setContentsMargins(16, 16, 16, 16)
        self.stack_layout.setSpacing(12)
        self.title_card = TitleBlockCard()
        self.title_card.changed.connect(lambda: self.apply_title_block(self.title_card.values()))
        self.title_edit = self.title_card.edits["title"]
        self.stack_layout.addWidget(self.title_card)
        self.add_button = QPushButton(icon("plus", ACCENT), "Aggiungi cavo")
        self.add_button.setObjectName("addCable")
        self.add_button.clicked.connect(self.add_cable)
        self.stack_layout.addWidget(self.add_button)
        self.stack_layout.addStretch()

        self.card_scroll = QScrollArea()
        self.card_scroll.setObjectName("cardScroll")
        self.card_scroll.setWidgetResizable(True)
        self.card_scroll.setWidget(self.stack)
        self.card_scroll.setMinimumWidth(CARDS_MIN_WIDTH)

        # linguetta verticale, centrata sul bordo destro dell'area card
        self.preview_tab = SideTab("Anteprima")
        self.preview_tab.toggled.connect(self.act_preview.setChecked)
        self.act_preview.toggled.connect(self.preview_tab.setChecked)
        tab_column = QVBoxLayout()
        tab_column.setContentsMargins(0, 0, 0, 0)
        tab_column.addStretch()
        tab_column.addWidget(self.preview_tab)
        tab_column.addStretch()

        cards_area = QWidget()
        cards_area.setObjectName("stack")
        cards_row = QHBoxLayout(cards_area)
        cards_row.setContentsMargins(0, 0, 0, 0)
        cards_row.setSpacing(0)
        cards_row.addWidget(self.card_scroll, 1)
        cards_row.addLayout(tab_column)

        self.preview_panel = self._build_preview_panel()
        self.preview_panel.hide()

        self.splitter = QSplitter()
        self.splitter.setChildrenCollapsible(False)
        self.splitter.addWidget(cards_area)
        self.splitter.addWidget(self.preview_panel)
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 2)
        self.setCentralWidget(self.splitter)

        QApplication.instance().focusChanged.connect(self._on_focus_changed)

        self._show_project()

    # --- costruzione UI ----------------------------------------------------

    def _action(self, label: str, slot, shortcut=None, checkable: bool = False,
                icon_name: str | None = None) -> QAction:
        action = QAction(label, self)
        if icon_name:
            action.setIcon(icon(icon_name))
        if shortcut is not None:
            action.setShortcut(shortcut)
        action.setCheckable(checkable)
        (action.toggled if checkable else action.triggered).connect(slot)
        return action

    def _build_actions(self) -> None:
        self.act_new = self._action("Nuovo progetto", self.new, QKeySequence.StandardKey.New,
                                    icon_name="file-plus")
        self.act_open = self._action("Apri…", self.open, QKeySequence.StandardKey.Open,
                                     icon_name="folder-open")
        self.act_save = self._action("Salva", self.save, QKeySequence.StandardKey.Save,
                                     icon_name="save")
        self.act_save_as = self._action("Salva con nome…", self.save_as,
                                        QKeySequence.StandardKey.SaveAs)
        self.act_export = self._action("Esporta PDF…", self.export, QKeySequence("Ctrl+E"),
                                       icon_name="file-down")
        self.act_import = self._action("Importa cavi da Excel/CSV…", self.import_cables,
                                       QKeySequence("Ctrl+I"), icon_name="file-up")
        self.act_template = self._action("Esporta template Excel/CSV…", self.export_template,
                                         icon_name="sheet")
        self.act_export_table = self._action("Esporta cavi in Excel/CSV…", self.export_table)
        self.act_quit = self._action("Esci", self.close, QKeySequence.StandardKey.Quit)
        self.act_add = self._action("Nuovo cavo", self.add_cable, QKeySequence("Ctrl+T"),
                                    icon_name="plus")
        self.act_expand = self._action("Espandi tutto", lambda: self.set_all_expanded(True),
                                       icon_name="chevron-down")
        self.act_collapse = self._action("Comprimi tutto", lambda: self.set_all_expanded(False),
                                         icon_name="chevron-right")
        self.act_preview = self._action("Anteprima", self.set_preview_visible,
                                        QKeySequence("F2"), checkable=True, icon_name="eye")
        self.act_check_updates = self._action("Controlla aggiornamenti…",
                                              lambda: self.check_updates(silent=False))
        self.act_auto_update = QAction("Controlla aggiornamenti all'avvio", self, checkable=True)
        self.act_auto_update.setChecked(self.auto_update_enabled())
        self.act_auto_update.toggled.connect(
            lambda on: self._settings.setValue(AUTO_UPDATE_KEY, on))
        self.act_about = self._action("Informazioni su WireSheet", self.about)
        self.act_about.setMenuRole(QAction.MenuRole.AboutRole)  # su macOS va nel menu dell'app

    def _build_menu(self) -> None:
        menus = [
            ("&File", (self.act_new, self.act_open, self.act_save, self.act_save_as, None,
                       self.act_add, None, self.act_quit)),
            ("&Importa/Esporta", (self.act_export, None, self.act_import, self.act_export_table,
                                  self.act_template)),
        ]
        for title, actions in menus:
            menu = self.menuBar().addMenu(title)
            for a in actions:
                menu.addSeparator() if a is None else menu.addAction(a)
        sort_menu = self.menuBar().addMenu("&Ordina")
        for label, key, reverse in SORT_OPTIONS:
            sort_menu.addAction(label).triggered.connect(
                lambda _=False, k=key, r=reverse: self.sort_cables(k, r))
        view_menu = self.menuBar().addMenu("&Vista")
        for a in (self.act_preview, None, self.act_expand, self.act_collapse):
            view_menu.addSeparator() if a is None else view_menu.addAction(a)
        help_menu = self.menuBar().addMenu("&Aiuto")
        for a in (self.act_check_updates, self.act_auto_update, None, self.act_about):
            help_menu.addSeparator() if a is None else help_menu.addAction(a)

    def _build_preview_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("previewPanel")

        self.mode_group = QButtonGroup(self)
        mode_bar = QHBoxLayout()
        for mode, label, icon_name in ((MODE_CABLE, "Cavo", "plug"),
                                       (MODE_SHEET, "Foglio", "file-text")):
            b = QPushButton(toggle_icon(icon_name), label)
            b.setCheckable(True)
            b.setChecked(mode == MODE_CABLE)
            b.clicked.connect(lambda _=False, m=mode: self.set_preview_mode(m))
            self.mode_group.addButton(b)
            mode_bar.addWidget(b)
        self.page_label = QLabel()
        mode_bar.addWidget(self.page_label)
        mode_bar.addStretch()
        for icon_name, tip, action in (
            ("zoom-out", "Riduci", lambda: self.preview.set_zoom(self.preview.zoom / 1.25)),
            ("zoom-in", "Ingrandisci", lambda: self.preview.set_zoom(self.preview.zoom * 1.25)),
            ("fit", "Adatta alla finestra", self._fit_preview),
        ):
            b = QToolButton()
            b.setIcon(icon(icon_name))
            b.setIconSize(QSize(18, 18))
            b.setToolTip(tip)
            b.clicked.connect(action)
            mode_bar.addWidget(b)
        close = QToolButton()
        close.setIcon(icon("x"))
        close.setIconSize(QSize(18, 18))
        close.setToolTip("Chiudi anteprima (F2)")
        close.clicked.connect(lambda: self.act_preview.setChecked(False))
        mode_bar.addWidget(close)

        self.preview = CablePreview()
        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidget(self.preview)
        self.preview_scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_scroll.setStyleSheet("QScrollArea { background: #e3e6ea; }")

        layout = QVBoxLayout(panel)
        layout.addLayout(mode_bar)
        layout.addWidget(self.preview_scroll, 1)
        layout.addWidget(QLabel("Ctrl + rotella per lo zoom"))
        return panel

    # --- card ----------------------------------------------------------------

    def _make_card(self, cable: Cable) -> CableCard:
        card = CableCard(cable)
        card.changed.connect(lambda c=card: self._on_card_changed(c))
        card.activated.connect(lambda c=card: self.set_active(self.cards.index(c)))
        card.duplicate_requested.connect(lambda c=card: self.duplicate_card(c))
        card.delete_requested.connect(lambda c=card: self.delete_card(c))
        card.move_requested.connect(lambda d, c=card: self.move_card(c, d))
        return card

    def _show_title(self) -> None:
        self.title_card.load(self.project)

    def _show_project(self) -> None:
        self._show_title()

        for card in self.cards:
            self.stack_layout.removeWidget(card)
            card.deleteLater()
        self.cards = []
        expanded = len(self.project.cables) <= COLLAPSE_ABOVE
        for i, cable in enumerate(self.project.cables):
            card = self._make_card(cable)
            card.set_expanded(expanded)
            self.stack_layout.insertWidget(FIRST_CARD + i, card)
            self.cards.append(card)
        self._active = -1
        self.set_active(0)
        self._update_card_buttons()
        self._update_title()

    def _insert_card(self, index: int, cable: Cable) -> None:
        self.project.cables.insert(index, cable)
        card = self._make_card(cable)
        self.cards.insert(index, card)
        self.stack_layout.insertWidget(FIRST_CARD + index, card)
        self._active = -1
        self.set_active(index)
        self._update_card_buttons()
        self._set_dirty()
        QTimer.singleShot(0, lambda: self.card_scroll.ensureWidgetVisible(card, 0, 40))

    def _update_card_buttons(self) -> None:
        for card in self.cards:  # l'ultimo cavo rimasto non si puo' eliminare
            card.delete_button.setEnabled(len(self.cards) > 1)

    def set_active(self, index: int) -> None:
        if index == self._active or not 0 <= index < len(self.cards):
            return
        self._active = index
        for i, card in enumerate(self.cards):
            card.set_active(i == index)
        self._refresh_preview()

    def _on_focus_changed(self, _old, new) -> None:
        w = new
        while w is not None and not isinstance(w, CableCard):
            w = w.parentWidget()
        if w is not None and w in self.cards:
            self.set_active(self.cards.index(w))

    def _on_card_changed(self, card: CableCard) -> None:
        index = self.cards.index(card)
        self.project.cables[index] = card.cable()
        self._set_dirty()
        if index == self._active:
            self._refresh_preview()
        else:
            self.set_active(index)

    def add_cable(self) -> None:
        self._insert_card(self._active + 1, default_cable(self.project.next_cable_name()))

    def duplicate_card(self, card: CableCard) -> None:
        cable = copy.deepcopy(card.cable())
        cable.name = self.project.next_cable_name()
        self._insert_card(self.cards.index(card) + 1, cable)

    def delete_card(self, card: CableCard, confirm: bool = True) -> None:
        if len(self.cards) <= 1:
            return
        if confirm:
            answer = QMessageBox.question(self, "WireSheet", f"Eliminare {card.cable().name}?")
            if answer != QMessageBox.StandardButton.Yes:
                return
        index = self.cards.index(card)
        del self.project.cables[index]
        del self.cards[index]
        self.stack_layout.removeWidget(card)
        card.deleteLater()
        self._active = -1
        self.set_active(max(index - 1, 0))
        self._update_card_buttons()
        self._set_dirty()

    def move_card(self, card: CableCard, delta: int) -> None:
        index = self.cards.index(card)
        target = index + delta
        if not 0 <= target < len(self.cards):
            return
        cables, cards = self.project.cables, self.cards
        cables[index], cables[target] = cables[target], cables[index]
        cards[index], cards[target] = cards[target], cards[index]
        self.stack_layout.removeWidget(card)
        self.stack_layout.insertWidget(FIRST_CARD + target, card)
        self._active = -1
        self.set_active(target)
        self._set_dirty()
        QTimer.singleShot(0, lambda: self.card_scroll.ensureWidgetVisible(card, 0, 40))

    def sort_cables(self, key, reverse: bool = False) -> None:
        """Riordina cavi e card; a parita' di chiave resta l'ordine attuale. La card attiva
        resta attiva."""
        active = self.cards[self._active] if 0 <= self._active < len(self.cards) else None
        pairs = sorted(zip(self.project.cables, self.cards), key=lambda pair: key(pair[0]),
                       reverse=reverse)
        cards = [card for _, card in pairs]
        if cards == self.cards:
            return
        self.project.cables = [cable for cable, _ in pairs]
        self.cards = cards
        for i, card in enumerate(cards):
            self.stack_layout.removeWidget(card)
            self.stack_layout.insertWidget(FIRST_CARD + i, card)
        self._active = -1
        self.set_active(cards.index(active) if active is not None else 0)
        self._set_dirty()
        if active is not None:
            QTimer.singleShot(0, lambda: self.card_scroll.ensureWidgetVisible(active, 0, 40))

    def set_all_expanded(self, expanded: bool) -> None:
        for card in self.cards:
            card.set_expanded(expanded)

    # --- anteprima -------------------------------------------------------------

    def set_preview_visible(self, visible: bool) -> None:
        if self.act_preview.isChecked() != visible:
            self.act_preview.setChecked(visible)  # richiama questo metodo via toggled
            return
        self.preview_panel.setVisible(visible)
        if visible:
            total = self.splitter.width()
            cards = max(CARDS_MIN_WIDTH, int(total * 0.55))
            self.splitter.setSizes([cards, total - cards])
            self._refresh_preview()
            QTimer.singleShot(0, self._fit_preview)

    def set_preview_mode(self, mode: str) -> None:
        self._preview_mode = mode
        for b in self.mode_group.buttons():
            b.setChecked(b.text() == ("Cavo" if mode == MODE_CABLE else "Foglio"))
        self._refresh_preview()
        QTimer.singleShot(0, self._fit_preview)

    def _refresh_preview(self) -> None:
        if self.preview_panel.isHidden() or not 0 <= self._active < len(self.project.cables):
            return
        cable = self.project.cables[self._active]
        self.page_label.setText("")
        if cable.validate():
            self.preview.set_cable(None, f"{cable.name}: correggi gli errori per vedere l'anteprima.")
            return
        if self._preview_mode == MODE_CABLE:
            self.preview.set_cable(cable)
            return
        valid = [c for c in self.project.cables if not c.validate()]
        geometry = sheet_geometry()
        pages = layout_pages(valid, geometry)
        page_index = next(i for i, page in enumerate(pages)
                          if any(p.cable is cable for p in page))
        self.page_label.setText(f"  Foglio {page_index + 1} di {len(pages)}")
        self.preview.set_page(self.project, pages[page_index], geometry, page_index + 1, len(pages))

    def _fit_preview(self) -> None:
        area = self.preview_scroll.viewport().size()
        self.preview.fit_to(area.width() - 20, area.height() - 20)

    # --- stato del progetto ------------------------------------------------------

    def _set_dirty(self, dirty: bool = True) -> None:
        self._dirty = dirty
        self._update_title()

    def _update_title(self) -> None:
        name = self._path.name if self._path else "Senza titolo"
        self.setWindowTitle(f"WireSheet — {name} (rev {self.project.revision})"
                            f"{' *' if self._dirty else ''}")
        self.title_card.load(self.project)  # la revisione sale salvando

    def apply_title_block(self, values: dict[str, str]) -> None:
        current = {name: getattr(self.project, name) for name in values}
        if values == current:
            return
        for name, value in values.items():
            setattr(self.project, name, value)
        self._show_title()
        self._set_dirty()
        if self._preview_mode == MODE_SHEET:
            self._refresh_preview()

    # --- versione e aggiornamenti ------------------------------------------------

    def about(self) -> None:
        QMessageBox.about(
            self, "Informazioni su WireSheet",
            f"<h3>WireSheet {__version__}</h3>"
            "<p>Tavole di cablaggio in PDF: estremità 1 → fili → estremità 2.</p>"
            f'<p><a href="{RELEASES_URL}">{RELEASES_URL}</a></p>'
            "<p>Licenza MIT © Giacomo Guaresi</p>")

    def auto_update_enabled(self) -> bool:
        return self._settings.value(AUTO_UPDATE_KEY, True, type=bool)

    def check_updates(self, silent: bool) -> None:
        """silent=True (all'avvio): avvisa solo se c'e' una versione nuova, niente errori."""
        self._silent_check = silent
        self._updates.check()

    def _on_update_found(self, version: str, url: str) -> None:
        answer = QMessageBox.question(
            self, "Aggiornamento disponibile",
            f"È disponibile WireSheet {version} (in uso: {__version__}).\n\n"
            "Aprire la pagina di download?")
        if answer == QMessageBox.StandardButton.Yes:
            QDesktopServices.openUrl(QUrl(url))

    def _on_up_to_date(self) -> None:
        if not self._silent_check:
            QMessageBox.information(self, "WireSheet",
                                    f"Stai usando l'ultima versione ({__version__}).")

    def _on_update_failed(self, message: str) -> None:
        if not self._silent_check:
            QMessageBox.warning(self, "WireSheet",
                                f"Impossibile controllare gli aggiornamenti:\n{message}")

    # --- file ----------------------------------------------------------------------

    def _maybe_save(self) -> bool:
        """True se si puo' proseguire (salvato, scartato o nulla da salvare)."""
        if not self._dirty:
            return True
        answer = QMessageBox.question(
            self, "WireSheet", "Salvare le modifiche al progetto?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard
            | QMessageBox.StandardButton.Cancel)
        if answer == QMessageBox.StandardButton.Save:
            return self.save()
        return answer == QMessageBox.StandardButton.Discard

    def new(self) -> None:
        if self._maybe_save():
            self.set_project(new_project(), None)

    def open(self) -> None:
        if not self._maybe_save():
            return
        path, _ = QFileDialog.getOpenFileName(self, "Apri progetto", "", OPEN_FILTER)
        if path:
            self.open_path(path)

    def open_path(self, path: str | Path) -> None:
        try:
            project = load_project(path)
        except (OSError, ValueError, KeyError, TypeError) as e:
            QMessageBox.critical(self, "WireSheet", f"Impossibile aprire il progetto:\n{e}")
            return
        if not project.cables:
            project.cables.append(default_cable("CABLE1"))
        self.set_project(project, Path(path))

    def set_project(self, project: Project, path: Path | None) -> None:
        self.project = project
        self._path = path
        self._dirty = False
        self._saved_revision = project.revision
        self._show_project()

    def save(self) -> bool:
        if self._path is None:
            return self.save_as()
        return self.save_to(self._path)

    def save_as(self) -> bool:
        suggested = str(self._path or f"{file_stem(self.project)}{FILE_EXTENSION}")
        path, _ = QFileDialog.getSaveFileName(self, "Salva progetto", suggested, FILE_FILTER)
        if not path:
            return False
        path = Path(path)
        if path.suffix != FILE_EXTENSION:
            path = path.with_suffix(FILE_EXTENSION)
        return self.save_to(path)

    def _bumps_revision(self) -> bool:
        """Il prossimo salvataggio alza la revisione: ci sono modifiche (o il progetto non e'
        mai stato salvato) e la revisione non e' gia' stata cambiata a mano."""
        return ((self._dirty or self._path is None)
                and self.project.revision == self._saved_revision)

    def save_to(self, path: Path) -> bool:
        previous = self.project.revision
        if self._bumps_revision():
            self.project.revision += 1
        try:
            save_project(self.project, path)
        except OSError as e:
            self.project.revision = previous
            QMessageBox.critical(self, "WireSheet", f"Impossibile salvare il progetto:\n{e}")
            return False
        self._path = path
        self._saved_revision = self.project.revision
        self._set_dirty(False)
        if self._preview_mode == MODE_SHEET:
            self._refresh_preview()
        return True

    def export(self) -> None:
        invalid = [c for c in self.project.cables if c.validate()]
        if invalid:
            details = "\n".join(f"• {c.name}: {c.validate()[0]}" for c in invalid)
            QMessageBox.warning(self, "WireSheet", f"Correggi prima questi cavi:\n{details}")
            return
        if not self._save_before_export():
            return
        suggested = str((self._path.parent if self._path else Path.cwd())
                        / f"{file_stem(self.project)}.pdf")
        path, _ = QFileDialog.getSaveFileName(self, "Esporta PDF", suggested, "PDF (*.pdf)")
        if not path:
            return
        try:
            sheets = export_pdf(self.project, path)
        except OSError as e:
            QMessageBox.critical(self, "WireSheet", f"Impossibile esportare il PDF:\n{e}")
            return
        QMessageBox.information(self, "WireSheet",
                                f"PDF salvato ({sheets} {'foglio' if sheets == 1 else 'fogli'}):\n{path}")

    def _save_before_export(self) -> bool:
        """Il PDF riporta la revisione del file salvato: con modifiche in sospeso chiede di salvare."""
        if not (self._dirty or self._path is None):
            return True
        revision = self.project.revision + self._bumps_revision()
        answer = QMessageBox.question(
            self, "WireSheet",
            f"Prima di esportare il progetto va salvato (revisione {revision}). Salvare?",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Cancel)
        return answer == QMessageBox.StandardButton.Save and self.save()

    # --- Excel / CSV ------------------------------------------------------------

    def _default_dir(self) -> Path:
        return self._path.parent if self._path else Path.cwd()

    def _ask_table_path(self, title: str, name: str) -> Path | None:
        path, selected = QFileDialog.getSaveFileName(
            self, title, str(self._default_dir() / f"{name}.xlsx"), TABLE_FILTER)
        if not path:
            return None
        path = Path(path)
        if path.suffix.lower() not in (".xlsx", ".csv"):
            path = path.with_suffix(".csv" if "csv" in selected.lower() else ".xlsx")
        return path

    def _write_table(self, path: Path, cables: list[Cable]) -> bool:
        try:
            write_table(path, cables)
        except OSError as e:
            QMessageBox.critical(self, "WireSheet", f"Impossibile salvare il file:\n{e}")
            return False
        return True

    def export_template(self) -> None:
        path = self._ask_table_path("Esporta template", "template_cavi")
        if path and self._write_table(path, example_cables()):
            QMessageBox.information(
                self, "WireSheet",
                f"Template salvato:\n{path}\n\nCompila una riga per filo (gli esempi si "
                "possono sovrascrivere), poi usa File → Importa cavi da Excel/CSV.")

    def export_table(self) -> None:
        path = self._ask_table_path("Esporta cavi", f"{file_stem(self.project)}_cavi")
        if path and self._write_table(path, self.project.cables):
            QMessageBox.information(self, "WireSheet", f"Cavi esportati:\n{path}")

    def import_cables(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Importa cavi", str(self._default_dir()),
                                              f"Excel o CSV (*.xlsx *.csv);;{TABLE_FILTER}")
        if not path:
            return
        try:
            result = import_table(path)
        except Exception as e:  # file danneggiato, formato non riconosciuto, permessi...
            QMessageBox.critical(self, "WireSheet", f"Impossibile leggere il file:\n{e}")
            return
        if result.errors:
            shown = result.errors[:15]
            more = len(result.errors) - len(shown)
            details = "\n".join(f"• {e}" for e in shown) + (f"\n… e altri {more}" if more else "")
            QMessageBox.warning(self, "WireSheet",
                                f"Nessun cavo importato: correggi il file.\n\n{details}")
            return
        if not result.cables:
            QMessageBox.information(self, "WireSheet", "Il file non contiene cavi.")
            return

        box = QMessageBox(self)
        box.setWindowTitle("WireSheet")
        box.setText(f"Trovati {len(result.cables)} cavi nel file.")
        box.setInformativeText("Vuoi aggiungerli al progetto o sostituire i cavi attuali?")
        add = box.addButton("Aggiungi in fondo", QMessageBox.ButtonRole.AcceptRole)
        replace = box.addButton("Sostituisci", QMessageBox.ButtonRole.DestructiveRole)
        box.addButton("Annulla", QMessageBox.ButtonRole.RejectRole)
        box.setDefaultButton(add)
        box.exec()
        if box.clickedButton() not in (add, replace):
            return
        self.apply_import(result.cables, replace=box.clickedButton() is replace)

        invalid = sum(1 for c in result.cables if c.validate())
        if invalid:
            QMessageBox.information(self, "WireSheet",
                                    f"{invalid} cavi importati hanno errori: sono segnati con ⚠.")

    def apply_import(self, cables: list[Cable], replace: bool) -> None:
        first_new = 0 if replace else len(self.project.cables)
        if replace:
            self.project.cables = list(cables)
        else:
            self.project.cables.extend(cables)
        self._show_project()
        self._active = -1
        self.set_active(first_new)
        self._set_dirty()
        card = self.cards[first_new]
        QTimer.singleShot(0, lambda: self.card_scroll.ensureWidgetVisible(card, 0, 40))

    def closeEvent(self, event: QCloseEvent) -> None:
        if self._maybe_save():
            QApplication.instance().focusChanged.disconnect(self._on_focus_changed)
            event.accept()
        else:
            event.ignore()
