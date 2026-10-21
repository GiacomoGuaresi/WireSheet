# Architettura

```
WireSheet/
  requirements.txt
  .github/workflows/
    ci.yml               # test su Windows e macOS a ogni push / pull request
    release.yml          # tag v* → test, build PyInstaller, GitHub Release
  packaging/
    wiresheet.spec       # build PyInstaller: WireSheet.exe (Windows) / WireSheet.app (macOS)
    launcher.py          # punto di ingresso dell'eseguibile
  wiresheet/
    __init__.py          # __version__ (unica fonte della versione) e indirizzo del repository
    components.py        # EndKind + codici dei componenti (JST XH, puntalino, forcella, taglio netto)
    colors.py            # sigle colore IEC 60757 → RGB
    model.py             # dataclass Project / Cable / End / Wire + validazione
    project_io.py        # salvataggio/apertura .wiresheet (JSON)
    table_io.py          # import/export Excel e CSV (una riga per filo), template
    render/
      symbols.py         # primitive (pen, font, testo) e simboli delle estremità
      cable_drawer.py    # layout e disegno di un cavo completo
      sheet_layout.py    # impaginazione su fogli verticali: cornice, cartiglio
    pdf_export.py        # export PDF del progetto (QPdfWriter, A3 verticale)
    demo.py              # script con cavi di esempio
    __main__.py          # avvio dell'applicazione (python -m wiresheet [file]), icona della finestra
    resources/
      icon.svg           # icona dell'app (connettore + tre fili con puntalini)
      icon.ico           # stessa icona 16-256 px per Windows / PyInstaller, generata da tools/make_icon.py
    ui/
      main_window.py     # finestra: menu File/Importa-Esporta/Ordina/Vista/Aiuto, pila di card, pannello anteprima
      update_check.py    # controllo aggiornamenti: ultima release su GitHub vs __version__
      cable_card.py      # CableCard: intestazione (nome, riepilogo, stato, azioni) + CableEditor
      cable_editor.py    # corpo della card: EndEditor P1/P2, tabella fili, errori
      preview.py         # CablePreview: cavo (draw_cable) o foglio (draw_page), con zoom
      title_block_card.py  # card del Cartiglio in cima alla pila: titolo, azienda, progetto, autore, data, revisione
      widgets.py         # combo/spinbox senza rotella, tabella ad altezza fissa,
                         # SideTab (linguetta verticale), EndThumbnail (miniatura componente)
      icons.py           # icone in stile Lucide (SVG inline) + campioni colore dei fili
      style.py           # foglio di stile e colori (ACCENT, DANGER, OK)
  tools/
    make_icon.py         # rigenera icon.ico da icon.svg
  tests/
    conftest.py          # fixture QApplication condivisa (piattaforma offscreen)
    test_model.py        # validazione del modello, nomi automatici
    test_render.py       # logica delle righe + smoke test dell'export PDF
    test_layout.py       # impaginazione: niente sovrapposizioni, ordine, multipagina
    test_project_io.py   # round-trip JSON, file non validi
    test_ui.py           # editor, lista cavi, salva/apri
  docs/
```

## Principi

- **Un solo motore di disegno.** `draw_cable()` disegna con un `QPainter` in coordinate **millimetri**. Anteprima a schermo (Step 2) e PDF useranno la stessa funzione, così il risultato è identico.
- **Modello separato dal disegno.** `model.py` non dipende da Qt e si può testare senza interfaccia grafica.
- **Layout prima del disegno.** `cable_size()` calcola l'ingombro di un cavo senza disegnarlo. Serve all'impaginazione, per decidere quando passare a una nuova pagina.

## Flusso

```
Project ──save_project()/load_project()──▶ file .wiresheet
   │
   ├─ Cable.validate() ──▶ errori (lista ⚠, editor, export bloccato)
   │
   ▼
layout_pages(cables) ── usa cable_size() ──▶ fogli di Placement(cable, x, y)
   │
   ▼
draw_page() ── chiama draw_cable() ──▶ QPdfWriter (PDF)
                draw_cable() ─────────▶ CablePreview (anteprima del cavo selezionato)
```

## Finestra

- `MainWindow` è proprietaria del `Project`. `self.cards[i]` corrisponde sempre a `project.cables[i]`: aggiunte, eliminazioni e spostamenti aggiornano le due liste e il layout insieme, spostando i widget senza ricostruirli.
- `CableCard` / `CableEditor` non tengono una copia del cavo: `cable()` lo ricostruisce ogni volta dai widget.
- A ogni modifica la card emette `changed`. La finestra allora:
  1. sostituisce `project.cables[i]`;
  2. rende attiva quella card;
  3. aggiorna l'anteprima;
  4. segna il progetto come modificato (`*` nel titolo).
- `load()` non emette `changed`.
- La **card attiva** (bordo blu) è quella cliccata, modificata o che contiene il widget con il focus (`QApplication.focusChanged`). L'anteprima mostra sempre la card attiva.
- Il **pannello anteprima** è nascosto di default. Lo apre l'azione checkable `act_preview`, che resta sincronizzata con la linguetta `SideTab` (F2, menu Vista, linguetta).
  - In modalità *Foglio* impagina solo i cavi validi con `layout_pages()` e mostra il foglio che contiene il cavo attivo.
  - Se il pannello è nascosto, l'anteprima non viene ricalcolata.
- **Rotella:** dentro la pila di card combo e spinbox reagiscono alla rotella solo se hanno il focus (`ui/widgets.py`). La tabella dei fili è alta quanto le sue righe. In questo modo la rotella scorre sempre la pagina.

## Icone

`ui/icons.py` contiene i path SVG 24×24 delle icone, in stile Lucide (licenza ISC).
- `icon(nome, colore)` crea la `QIcon` con il colore indicato e la tiene in cache.
- `toggle_icon()` è per i pulsanti checkable: l'icona diventa bianca quando il pulsante è attivo.
- `color_swatch(codice)` crea il quadratino colore usato nella tendina dei colori.

Per aggiungere un'icona basta aggiungere il suo path a `_PATHS`; il test `test_icons_render` la verifica in automatico.

## Unità e font

- Il painter è scalato in modo che **1 unità = 1 mm**: `scale(dpi / 25.4)`.
- `set_font(p, size_mm)` converte un'altezza in mm nella dimensione del font in punti: `pt = mm × 72 / dpi del dispositivo`. In questo modo il testo ha la stessa dimensione su qualsiasi dispositivo.
