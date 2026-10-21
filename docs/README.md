# WireSheet — Documentazione

WireSheet è un piccolo programma desktop (Windows e Mac) che genera **tavole di cablaggio in PDF**.
Il formato è lo stesso delle tavole del fornitore (P/N:1, 2, 3): estremità 1 → fili → estremità 2, con quote e tabella dei fili.

Lo sviluppo procede **a piccoli step incrementali**. Ogni step deve funzionare ed essere provabile prima di passare al successivo. Le funzioni nuove si aggiungono solo quando servono.

## Indice

| Documento | Contenuto |
|---|---|
| [getting-started.md](getting-started.md) | Installazione, avvio, esecuzione dei test |
| [architecture.md](architecture.md) | Struttura del codice e responsabilità dei moduli |
| [data-model.md](data-model.md) | Modello dati (Cable, End, Wire) e regole di validazione |
| [drawing-rules.md](drawing-rules.md) | Come viene disegnato un cavo: geometria, simboli, testi |
| [components.md](components.md) | Componenti supportati e colori dei fili |
| [import-excel-csv.md](import-excel-csv.md) | Template, import ed export dei cavi in Excel/CSV |
| [roadmap.md](roadmap.md) | Step completati, step in corso e idee future |

## Perimetro attuale

- **Estremità supportate:** connettore JST XH da 2 a 7 posizioni (XHP-n + terminale SXH-001T-P0.6), connettori circolari GM a pannello (GM-1312, GM-1712, GM-2112), morsettiera a innesto 5,08 da 2 a 8 poli, puntalini, forcelle, faston femmina, taglio netto.
- **Caso gestito:** solo il caso base `[estremità 1] — [fili: pin, colore, lunghezza] — [estremità 2]`.
- **Fuori perimetro, per ora:** istruzioni di taglio/spelatura, giunzioni e diramazioni, etichette, altri connettori, scelta della lingua.

## Stack

- Python 3.12
- PySide6 (Qt 6): interfaccia, disegno vettoriale (QPainter) e PDF (QPdfWriter)
- openpyxl: lettura e scrittura dei file Excel (.xlsx)
- pytest per i test
