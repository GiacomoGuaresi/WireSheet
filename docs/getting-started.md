# Getting started

## Requisiti

- Python 3.12 o superiore
- Windows 10/11 oppure macOS

## Installazione

Dalla cartella del progetto:

```powershell
# Windows
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

```bash
# macOS
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Avviare il programma

```powershell
.\.venv\Scripts\python.exe -m wiresheet                     # progetto nuovo
.\.venv\Scripts\python.exe -m wiresheet progetto.wiresheet   # apre un progetto
```

### La finestra

- **Menu File:** Nuovo progetto, Apri, Salva, Salva con nome, Nuovo cavo (Ctrl+T), Esci.
- **Menu Importa/Esporta:** Esporta PDF (Ctrl+E), Importa cavi da Excel/CSV (Ctrl+I), Esporta cavi in Excel/CSV, Esporta template Excel/CSV.
- **Menu Ordina:** nome A → Z o Z → A (ordine naturale, `CABLE2` prima di `CABLE10`), componente P1, numero di fili, lunghezza. L'ordinamento cambia l'ordine dei cavi nel progetto e nel PDF; a parità resta l'ordine attuale.
- **Card Cartiglio** in cima alla pila, con lo sfondo crema e non comprimibile: Titolo, Azienda, Progetto / macchina, Disegnato da, Data (con il pulsante Oggi) e Revisione. Le modifiche vanno subito nel progetto e nell'anteprima del foglio.
- **Pila di card**, una per cavo:
  - intestazione con la freccia per comprimere, nome modificabile, riepilogo (`XH-4 → Puntalini · 4 fili · 200 mm`), stato ✓ / ⚠ e le icone Duplica, Su, Giù, Elimina;
  - corpo con P1 e P2. Per ciascuno ci sono la tendina del componente e, sotto, la variante (numero di pin) con la miniatura del componente;
  - tabella dei fili: Pin P1 | Colore (con campione) | Lunghezza | Pin P2, più i pulsanti + Filo / − Filo e gli errori;
  - in fondo alla pila il pulsante **Aggiungi cavo**. I cavi nuovi o duplicati compaiono sotto la card attiva.
- **Pannello anteprima:** si apre con la linguetta verticale **ANTEPRIMA** sul bordo destro, con F2 o dal menu Vista. Mostra la card attiva, bordata di blu: diventa attiva la card sotto il mouse, oppure quella su cui clicchi o scrivi.
  - **Cavo** mostra il disegno del singolo cavo.
  - **Foglio** mostra il foglio A3 in cui finirà il cavo, con l'indicazione "Foglio n di m".
- **Menu Vista:** Anteprima, Espandi tutto, Comprimi tutto. I progetti con più di 5 cavi si aprono con le card compresse.
- **Esporta PDF** (menu Importa/Esporta o Ctrl+E) crea un PDF A3 verticale con tutti i cavi del progetto, uno sotto l'altro e ingranditi per riempire la larghezza del foglio, con il cartiglio e il numero di pagina in fondo a ogni foglio. Se ci sono modifiche non salvate, prima di esportare chiede di salvare, così il PDF riporta la revisione del file salvato. La revisione sale da sola a ogni salvataggio con modifiche ed è mostrata nel titolo della finestra.

Scorrendo la pila con la rotella, tendine e numeri non cambiano per sbaglio: per modificarli con la rotella bisogna prima cliccarci sopra.

## Generare il PDF di esempio

```powershell
.\.venv\Scripts\python.exe -m wiresheet.demo            # crea demo.pdf
.\.venv\Scripts\python.exe -m wiresheet.demo out.pdf    # percorso personalizzato
```

Il PDF (A3, progetto DEMO) contiene 10 cavi di esempio: uno per ogni tipo di estremità (diretto, pin invertiti, puntalini, forcelle, taglio netto, GM, morsettiera → faston) e due cavi a più rami.

## Test

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

I test di rendering usano la piattaforma Qt `offscreen`, quindi non serve un display.

## Creare gli eseguibili

```powershell
.\.venv\Scripts\python.exe -m pip install pyinstaller pillow
.\.venv\Scripts\pyinstaller.exe --noconfirm packaging/wiresheet.spec
```

Il risultato è in `dist/`: `WireSheet.exe` su Windows, `WireSheet.app` su macOS (PyInstaller non fa cross-compilazione). Pillow serve su macOS per convertire l'icona in `.icns`.

## Release

La pipeline [`.github/workflows/release.yml`](../.github/workflows/release.yml) parte al push di un tag `v*` (es. `git tag v1.0.0 && git push origin v1.0.0`): esegue i test, crea gli eseguibili su Windows e macOS e pubblica la GitHub Release con i due zip. La pipeline [`ci.yml`](../.github/workflows/ci.yml) esegue i test a ogni push su `main` e a ogni pull request.
