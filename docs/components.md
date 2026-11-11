# Componenti e colori

## Estremità supportate

Definite in [`wiresheet/components.py`](../wiresheet/components.py).

| `EndKind` | Componente | Codici stampati |
|---|---|---|
| `JST_XH` | Connettore JST XH, 2–7 posizioni | `JST:XHP-n`, `SXH-001T-P0.6` |
| `GM1312`, `GM1712`, `GM2112` | Connettore circolare GM (Hengzhan, tipo Weipu) a pannello, fissaggio posteriore | `GM-2112/S-4P`, `PANEL, REAR MOUNT` |
| `TERMINAL_BLOCK` | Morsettiera a innesto verde passo 5,08 (tipo Phoenix MSTB), 2–8 posizioni | `WJ2EDGK-5.08-4P`, `PLUGGABLE, SCREW` |
| `FERRULE` | Puntalino isolato DIN 46228-4 (uno per filo), misura scelta dalla sezione del filo | `FERRULE 1.5mm² L8` + `KST:E1508` per ogni misura; `FERRULE` se i fili non hanno sezione |
| `FORK` | Forcella M3 isolata (una per filo) | `FORK` |
| `FASTON_F` | Faston femmina 6,3 isolato (uno per filo) | `FASTON F 6.3` |
| `FLAT_CUT` | Taglio netto: filo libero, tagliato a filo dell'isolante, non spelato | `FLAT CUT` |
| `STRIPPED_12` | Filo libero spelato 12 mm | `STRIPPED 12 mm` |

I disegni di riferimento di ogni componente sono in [`drawings/`](../drawings/), generati dagli script `gen_*.py`; i simboli in `symbols.py` ne riprendono la geometria.

### Puntalini

Il puntalino di ogni filo è la misura standard (`FERRULE_SIZES`) uguale o subito più grande della sezione del filo; se il filo ha solo l'AWG, la sezione si ricava dalla tabella di equivalenza. Il codice riporta sezione e lunghezza del tubetto, più il codice KST serie E (sezione + tubetto: `E1508` = 1,5 mm², L8).

| Sezione (mm²) | 0,25 | 0,34 | 0,5 | 0,75 | 1 | 1,5 | 2,5 | 4 | 6 | 10 | 16 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Tubetto (mm) | 8 | 8 | 8 | 8 | 8 | 8 | 8 | 9 | 12 | 12 | 12 |
| KST | – | – | E0508 | E7508 | E1008 | E1508 | E2508 | E4009 | E6012 | E10-12 | E16-12 |

Sotto l'estremità ogni misura usata ha due righe (`FERRULE 1.5mm² L8`, `KST:E1508`); nella WIRE LIST ogni filo ha la sua su una riga: `FERRULE 1.5mm² L8 (KST:E1508)`. Oltre 16 mm² il codice riporta solo la sezione; per 0,25 e 0,34 mm² il codice KST non è indicato (da verificare a catalogo).

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
