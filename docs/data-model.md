# Modello dati

Definito in [`wiresheet/model.py`](../wiresheet/model.py).

## End (estremità)

| Campo | Tipo | Note |
|---|---|---|
| `kind` | `EndKind` | `JST_XH`, `GM1312`, `GM1712`, `GM2112`, `TERMINAL_BLOCK`, `FERRULE`, `FORK`, `FASTON_F`, `FLAT_CUT` |
| `positions` | `int` | Numero di pin del connettore. Usato solo per i connettori |
| `variant` | `str` | Solo connettori GM: genere + disposizione (`S4`, `P5A`…). Vuoto negli altri casi |

`end_variants(kind)` elenca tutte le combinazioni valide; la tendina "variante" della UI e la validazione usano questo elenco.

`is_connector` è vero per `JST_XH`, `TERMINAL_BLOCK` e per i GM. Puntalini, forcelle, faston e taglio netto sono estremità **per filo**: ogni filo riceve il proprio terminale (o nessuno, nel caso del taglio netto).

## Wire (filo)

| Campo | Tipo | Note |
|---|---|---|
| `color` | `str` | Sigla colore, vedi [components.md](components.md) |
| `length_mm` | `float` | Lunghezza del singolo filo |
| `p1_pin` | `int \| None` | Pin su P1. Obbligatorio solo se P1 è un connettore |
| `p2_pin` | `int \| None` | Pin su P2. Obbligatorio solo se P2 è un connettore |
| `section_mm2` | `float \| None` | Sezione in mm² (facoltativa) |
| `awg` | `int \| None` | Sezione in AWG, 8–30 (facoltativa) |

Basta una delle due sezioni: l'altra si ricava dalla tabella di equivalenza commerciale in [`gauges.py`](../wiresheet/gauges.py) (0,25 ↔ 24AWG, 0,5 ↔ 20AWG, 0,75 ↔ 18AWG, 1 ↔ 17AWG, 1,5 ↔ 16AWG, 2,5 ↔ 14AWG…). Se sono indicate entrambe, restano come sono. Card, Excel/CSV e WIRE LIST hanno una sola colonna *Sezione* scritta `0.25mm² (24AWG)`; la WIRE LIST stampa sempre entrambe le unità; la colonna SECTION compare solo se almeno un filo ha la sezione.

## Branch (ramo in uscita)

| Campo | Tipo | Note |
|---|---|---|
| `end` | `End` | Estremità P2 del ramo |
| `wires` | `list[Wire]` | Fili del ramo; `p2_pin` si riferisce a `end` |
| `name` | `str` | Funzione del ramo, es. `Cooling fan`. Distingue i rami anche se hanno lo stesso connettore |
| `label` | `bool` | `True` (default): l'etichetta del ramo è disegnata. Si toglie con la casella **Etichetta** del ramo nella card. Non passa da Excel/CSV: i rami importati hanno sempre l'etichetta |

## Cable (cavo)

Un cavo ha **un solo connettore in ingresso (P1)** e **uno o più rami in uscita**.

| Campo | Tipo | Note |
|---|---|---|
| `name` | `str` | Es. `CABLE24` |
| `p1` | `End` | Ingresso, a sinistra nel disegno |
| `branches` | `list[Branch]` | Almeno uno. Un cavo semplice ha un ramo senza nome |

`Cable(nome, p1, p2, fili)` crea un cavo semplice; `Cable(nome, p1, branches=[...])` un cavo a più rami.
Proprietà di comodo: `p2` (estremità del primo ramo), `wires` (tutti i fili, ramo per ramo; è una lista nuova, per aggiungere fili usare `branches[i].wires`), `is_branched`.

`length_mm` restituisce la lunghezza del filo più lungo. Il disegno non ha quote: le lunghezze dei fili sono nella WIRE LIST.

## Project (progetto)

| Campo | Tipo | Note |
|---|---|---|
| `title` | `str` | Cartiglio: TITLE; è anche il nome proposto per i file |
| `company` | `str` | Cartiglio: COMPANY |
| `machine` | `str` | Cartiglio: PROJECT (progetto / macchina) |
| `revision` | `int` | Cartiglio: REV. Parte da 0 e sale di 1 a ogni salvataggio con modifiche (il primo salvataggio dà 1); Ctrl+S ripetuto senza modifiche non la cambia. Si può cambiare a mano dalla finestra Cartiglio: in quel caso al salvataggio resta il numero scelto. Nei file vecchi un valore non numerico diventa 0 |
| `date` | `str` | Cartiglio: DATE, testo libero (i progetti nuovi partono con la data di oggi) |
| `drawn_by` | `str` | Cartiglio: DRAWN BY |
| `cables` | `list[Cable]` | Ordine = ordine nel PDF |

Tutti i campi del cartiglio sono facoltativi; una casella vuota resta vuota nel PDF.

`next_cable_name()` restituisce `CABLEn`, dove n è il numero più alto già usato + 1. I nomi che non seguono lo schema `CABLEn` vengono ignorati.

## File di progetto (`.wiresheet`)

È un JSON UTF-8, scritto da [`project_io.py`](../wiresheet/project_io.py):

```json
{
  "format": "wiresheet",
  "version": 2,
  "title": "Cablaggio stampante",
  "company": "ACME Srl",
  "machine": "G1",
  "revision": 3,
  "date": "2026-10-20",
  "drawn_by": "DM",
  "cables": [
    {
      "name": "CABLE1",
      "p1": {"kind": "jst_xh", "positions": 2},
      "branches": [
        {
          "name": "",
          "label": true,
          "end": {"kind": "ferrule", "positions": 0},
          "wires": [
            {"color": "RD", "length_mm": 300, "p1_pin": 1, "p2_pin": null}
          ]
        }
      ]
    }
  ]
}
```

Per i connettori GM l'estremità ha anche `"variant"`, es. `{"kind": "gm2112", "positions": 4, "variant": "S4"}`. Il campo è facoltativo, quindi i file vecchi restano validi.

Versioni: la 1 aveva `p2` + `wires` al posto di `branches`; viene ancora letta (diventa un cavo con un solo ramo). I file si salvano sempre nella versione 2.

I progetti creati quando il programma si chiamava CableGen (estensione `.cablegen`, `"format": "cablegen"`) si aprono ancora; salvando con nome diventano `.wiresheet`.

Il programma rifiuta i file senza `"format": "wiresheet"` (o `"cablegen"`) e quelli con una `version` più recente di quella che conosce. Quando il formato cambierà, `FORMAT_VERSION` andrà incrementato e servirà una conversione dei file vecchi.

## Validazione (`Cable.validate()`)

Restituisce una lista di messaggi di errore, vuota se il cavo è valido:

- il cavo deve avere almeno un filo;
- ogni colore deve esistere nella tabella colori;
- ogni lunghezza deve essere maggiore di 0;
- per ogni estremità a connettore:
  - la variante deve esistere nel catalogo (JST XH: 2–7 posizioni; GM: vedi [components.md](components.md));
  - i fili non possono essere più delle posizioni;
  - ogni filo deve avere un pin compreso tra 1 e il numero di posizioni;
  - nessun pin può essere usato due volte.

Sulle estremità per filo i pin vengono ignorati.

Nei cavi a più rami i pin di P1 sono controllati su tutti i fili, quelli di P2 ramo per ramo; gli errori indicano il ramo (`P2 ramo 'Cooling fan': …`) e un ramo senza fili è un errore.

