# Componenti e colori

## Estremità supportate

Definite in [`wiresheet/components.py`](../wiresheet/components.py).

| `EndKind` | Componente | Codici stampati |
|---|---|---|
| `JST_XH` | Connettore JST XH, 2–7 posizioni | `JST:XHP-n`, `SXH-001T-P0.6` |
| `GM1312`, `GM1712`, `GM2112` | Connettore circolare GM (Hengzhan, tipo Weipu) a pannello, fissaggio posteriore | `GM-2112/S-4P`, `PANEL, REAR MOUNT` |
| `TERMINAL_BLOCK` | Morsettiera a innesto verde passo 5,08 (tipo Phoenix MSTB), 2–8 posizioni | `TB 5.08-4P`, `PLUGGABLE, SCREW` |
| `FERRULE` | Puntalino (uno per filo) | `FERRULE` |
| `FORK` | Forcella M3 isolata (una per filo) | `FORK` |
| `FASTON_F` | Faston femmina 6,3 isolato (uno per filo) | `FASTON F 6.3` |
| `FLAT_CUT` | Taglio netto, filo libero | `FLAT CUT` |

I disegni di riferimento di ogni componente sono in [`drawings/`](../drawings/), generati dagli script `gen_*.py`; i simboli in `symbols.py` ne riprendono la geometria.

### Connettori circolari GM a pannello

Serie 13, 17 e 21, montaggio posteriore con dado ("Rear mount" nel catalogo Hengzhan). La variante è **genere + disposizione dei contatti**:
`S` = femmina (socket), `P` = maschio (pin). Esempi: `S4`, `P7`, `S5A`.

| Serie | Disposizioni |
|---|---|
| GM1312 | 2, 3, 4, 5, 6, 7, 9 |
| GM1712 | 2, 3, 4, 5, 7, 9 |
| GM2112 | 2, 3, 4, 5A, 5B, 5C, 7, 9, 12 |

Codice stampato nel formato del fornitore: `GM-2112/S-4P`, `GM-2112/S-5P-A`.

`GM_LAYOUTS` elenca le disposizioni disponibili; il numero di pin di ogni variante è il numero di contatti della disposizione. Lo schema dei pin (vista frontale / lato saldatura) **non** viene disegnato nel PDF: le coordinate trascritte dal catalogo non erano affidabili e lo schema risultava fuorviante. I pin si leggono dalla WIRE LIST e dai numeri accanto al simbolo.

Per aggiungere un componente servono quattro passi:
1. un valore in `EndKind` (e in `POSITION_RANGES` se è un connettore a n posizioni);
2. i codici in `end_codes()`;
3. un simbolo in `symbols.py`;
4. per i connettori il ramo in `draw_connector()`, per i terminali per filo la voce in `TERMINALS`.

## Colori dei fili (IEC 60757)

Definiti in [`wiresheet/colors.py`](../wiresheet/colors.py).

| Sigla | Colore |
|---|---|
| BK | Nero |
| BN | Marrone |
| RD | Rosso |
| OR | Arancione |
| YE | Giallo |
| GN | Verde |
| BU | Blu |
| VT | Viola |
| GY | Grigio |
| WH | Bianco |
| PK | Rosa |
| YE/GN | Giallo/verde (terra) |
