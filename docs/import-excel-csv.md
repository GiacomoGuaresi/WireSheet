# Import / export Excel e CSV

Implementato in [`wiresheet/table_io.py`](../wiresheet/table_io.py). Non dipende da Qt; per l'Excel usa openpyxl.

## Comandi (menu File)

| Comando | Cosa fa |
|---|---|
| **Esporta template Excel/CSV…** | Crea un file con le colonne e 2 cavi di esempio da sovrascrivere |
| **Importa cavi da Excel/CSV…** (Ctrl+I) | Legge il file e chiede se **aggiungere** i cavi in fondo o **sostituire** quelli del progetto |
| **Esporta cavi in Excel/CSV…** | Esporta i cavi del progetto nello stesso formato, così si possono modificare in Excel e reimportare |

Il formato si sceglie dall'estensione: `.xlsx` per Excel, `.csv` per CSV.

## Formato

Una **riga per filo**. Le righe con lo stesso valore in *Cavo* formano un cavo, anche se non sono consecutive. L'ordine dei cavi è quello della loro prima riga.

| Colonna | Obbligatoria | Valori |
|---|---|---|
| Cavo | sì | Nome del cavo, es. `CABLE1` |
| P1 componente | sì, sulla prima riga del cavo | `JST XH`, `GM1312`, `GM1712`, `GM2112`, `Puntalini`, `Forcelle`, `Taglio netto` |
| P1 variante | se P1 è un connettore | JST XH: numero di pin, da 2 a 7. GM: genere + disposizione, es. `S4`, `P7`, `S5A` |
| Pin P1 | se P1 è un connettore | Pin a cui va il filo |
| Colore | sì | Sigla (`RD`, `BK`, `YE/GN`…) oppure nome italiano (`Rosso`, `Nero`…) |
| Lunghezza (mm) | sì | Numero maggiore di 0 |
| Pin P2 | se P2 è un connettore | Pin a cui va il filo |
| P2 componente | sì, sulla prima riga di ogni ramo | come P1 |
| P2 variante | se P2 è un connettore | come P1 |
| Ramo | no | Nome del ramo, es. `Cooling fan`. Vuoto per i cavi semplici |
| Sezione | no | Es. `0.25mm² (24AWG)`. Basta una unità: `0,25`, `0.25mm2` oppure `24AWG` (AWG da 8 a 30) |

P1 (componente e variante) si può lasciare vuoto nelle righe successive alla prima: viene ereditato dalla prima riga del cavo. Se invece è compilato, deve essere uguale a quello della prima riga.

### Cavi a più rami

Un cavo ha un solo P1 e uno o più rami in uscita. Un ramo è identificato da **Ramo + componente P2**:
- la prima riga di un ramo indica P2 (componente e variante);
- le righe con P2 vuoto continuano l'ultimo ramo con lo stesso nome;
- se P2 cambia, anche con lo stesso nome (o con il nome vuoto), inizia un nuovo ramo. Per esempio, due puntalini e un filo a taglio netto senza nome formano due rami.

```
Cavo;P1 componente;P1 variante;Pin P1;Colore;Lunghezza (mm);Pin P2;P2 componente;P2 variante;Ramo
FANS;GM1712;S7;1;RD;800;1;JST XH;2;Cooling fan
FANS;;;2;BK;800;2;;;Cooling fan
FANS;;;6;RD;1000;;Taglio netto;;Extruder fan
FANS;;;7;BK;1000;;;;Extruder fan
```

In export la colonna *Ramo* è compilata su tutte le righe, P2 sulla prima riga di ogni ramo. La colonna *Ramo* è l'ultima, così i file senza rami (9 colonne) restano validi.

Esempio (CSV):

```
Cavo;P1 componente;P1 variante;Pin P1;Colore;Lunghezza (mm);Pin P2;P2 componente;P2 variante;Ramo
CABLE1;JST XH;2;1;RD;350;1;JST XH;2;
CABLE1;;;2;BK;350;2;;;
CABLE2;JST XH;4;1;RD;200;;Puntalini;;
CABLE2;;;2;BK;200;;;;
```

### Valori accettati in import

L'import è tollerante sul modo in cui sono scritti i valori:
- **Componenti:** non conta maiuscolo/minuscolo; sono accettati anche `xh`, `jst_xh`, `puntalino`, `forcella`, `fork`, `flat cut`, `taglio`, `GM-2112`.
- **Colori:** sigla o nome italiano, senza distinzione di maiuscole (`rosso`, `giallo-verde`, `GN/YE`).
- **Varianti GM:** `s4`, `S-4P`, `p 5a` sono accettate; il genere (`S`/`P`) è obbligatorio.
- **Numeri:** `4 pin` vale 4; `12,5` vale 12.5.
- **Ramo:** l'intestazione può essere anche `Funzione` o `Funzione/segnale`.
- **Intestazioni:** si possono scrivere anche in inglese (`name`, `p1 type`, `color`, `length`…) e in qualunque ordine.
- **CSV:** il separatore può essere `;`, `,` o tabulazione; il file viene letto in UTF-8.
- **Excel:** viene letto il foglio `Cavi`, oppure il primo foglio se `Cavi` non c'è. Le righe vuote vengono ignorate.

### Errori

- Gli **errori di formato** (colonna mancante, componente o colore sconosciuto, lunghezza non numerica, pin mancante su un connettore) vengono elencati con il **numero di riga**, e in quel caso **non viene importato nulla**.
- Gli **errori di cablaggio** (pin doppi, più fili che pin) non bloccano l'import: i cavi vengono importati e marcati con ⚠ nella loro card.

## File generati

- **Excel:**
  - foglio `Cavi` con intestazione colorata e prima riga bloccata;
  - tendine per componente, variante, pin e colore, e controllo che la lunghezza sia maggiore di 0;
  - foglio `Istruzioni`.
- **CSV:** separatore `;` (quello che Excel usa con le impostazioni italiane), UTF-8 con BOM, così Excel mostra correttamente gli accenti.
