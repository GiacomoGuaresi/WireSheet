# Regole di disegno

Implementate in [`wiresheet/render/cable_drawer.py`](../wiresheet/render/cable_drawer.py) e [`symbols.py`](../wiresheet/render/symbols.py). Tutte le misure sono in mm.

## Blocco di un cavo (dall'alto verso il basso)

1. **Nome** del cavo, in grassetto, in alto a sinistra.
2. **Etichetta del cavo** (vedi sotto). Non c'è una quota: le lunghezze sono nella WIRE LIST.
3. **Fili e estremità**:
   - P1 a sinistra, P2 a destra;
   - il tratto disegnato è fisso (`SPAN` = 80 mm) e **non è in scala**;
   - i fili sono distanziati di `ROW` = 3 mm.
4. **Codici dei componenti** sotto ciascuna estremità (es. `JST:XHP-3` / `SXH-001T-P0.6`, `FERRULE`).
5. **Tabella WIRE LIST** larga quanto il cavo, subito sotto i codici: `FROM | COLOR | LENGTH | SECTION | BRANCH | TO`, una riga per filo che si legge da sola, es. `GM-1712/S-7P (pin 1) | RD (Red) | 800mm | 0.5mm² (20AWG) | A. Cooling fan | JST:XHP-2 (pin 1)`. FROM/TO usano il codice stampato sotto il connettore (`FLAT CUT`, `FERRULE`… per le estremità per filo, senza pin). SECTION compare solo se qualche filo ha la sezione, BRANCH solo nei cavi a più rami. Le colonne sono proporzionate al contenuto; se le righe non ci stanno il font si riduce (da 2,2 fino a 1,4 mm).

## Righe dei fili

| Situazione | Riga del filo |
|---|---|
| Estremità a connettore | P1 (sinistra): riga = `posizioni - pin`, il pin 1 è in basso. P2 (destra): il connettore è ruotato di 180° (non specchiato), riga = `pin - 1`, il pin 1 è in alto |
| Estremità per filo, con un connettore dall'altro lato | stessa riga del connettore opposto, così il filo resta dritto |
| Nessun connettore | riga = indice del filo nella lista |

Se le righe ai due lati sono diverse (pin permutati), il filo **si incrocia** con un tratto diagonale (`CROSS` = 12 mm) vicino a P2, come nelle tavole originali.

Sui connettori GM i contatti a saldare sono più fitti delle righe: negli ultimi `GM_FAN` = 6 mm il filo converge sul suo contatto. Se un connettore è più alto delle righe (GM con pochi pin), il blocco del cavo riceve spazio sopra e sotto.

## Etichette

Ogni cavo ha un'etichetta vicino a P1 con il nome del cavo; nei cavi a più rami ogni ramo ha in più la sua etichetta vicino all'estremità, con il titolo del ramo (`A. Cooling fan` o `Branch A`). L'etichetta di un ramo si può nascondere togliendo la spunta **Etichetta** nella card (`Branch.label`); quella del cavo c'è sempre.

- Sul disegno l'etichetta è una **fascetta** bianca larga 2,5 mm che avvolge i fili, a 12 mm dalla faccia dell'estremità (`SLEEVE_INSET`), con scritto `LABEL` in verticale (1,2 mm); è alta quanto i fili e almeno quanto la scritta.
- Una linea tratteggiata con la freccia verso la fascetta la collega al **cartellino** con il testo in grassetto.
- Il cartellino del cavo sta nella fascia sopra i fili (`LABEL_H` = 9 mm) e si sviluppa verso destra; quello di un ramo sta nella riga sopra il ramo e si sviluppa verso sinistra.
- La fascetta copre i fili che passano in quel punto (anche dove si incrociano).

## Fili

- Ogni filo è una linea colorata di 0,55 mm con un contorno di 0,9 mm dello stesso colore più scuro (`WIRE_OUTLINE`): il bianco ha il bordo grigio, il nero nero, il blu blu scuro. Così anche il bianco e il giallo sono leggibili.
- I colori bicolore (es. `YE/GN`) hanno una seconda linea tratteggiata.

## Simboli

| Estremità | Simbolo | Testo esterno |
|---|---|---|
| JST XH | Housing XHP visto dal lato aggancio: finestre dei contatti verso l'esterno, collarino sul lato fili. Scalato sul passo delle righe (2,5 → 3 mm) | `numero colore` per ogni pin (`1 RD`); i pin senza filo sono `2 nc`, con *nc* in corsivo |
| Morsettiera 5,08 | Innesto verso l'esterno, corpo con viti e fori di sblocco sul lato fili. Scalata sul passo delle righe (5,08 → 3 mm) | come JST XH |
| GM a pannello | Vista laterale: filetto, flangia, dado, isolante e contatti a saldare, scala fissa 0,55. Nessuno schema pin (tolto: fuorviante) | come JST XH |
| Puntalino | Tubetto metallico + collare isolante, alto 2,5 mm | colore del filo |
| Forcella | Linguetta con fessura + isolante, alta 2,5 mm | colore del filo |
| Faston F | Bordi arrotolati, collo + isolante, alto 2,5 mm | colore del filo |
| Taglio netto | Il conduttore esposto: rettangolo lungo 4 mm e alto 0,6 mm, più sottile del filo isolato (0,9 mm) | colore del filo |

I simboli riprendono i disegni di [`drawings/`](../drawings/), ridotti per stare nel passo delle righe.

## Cavi a più rami

- P1 a sinistra, centrato in altezza; i rami sono impilati a destra, ognuno con il suo connettore e i suoi codici sotto.
- I rami sono ordinati dall'alto seguendo le righe dei loro fili su P1 (pin 1 in basso), così i gruppi di fili non si incrociano.
- Ogni ramo ha la sua etichetta `A. nome` (es. `C. Extruder fan`), oppure `Branch A` se il ramo non ha nome; le lunghezze sono solo nella WIRE LIST. La lettera è la posizione del ramo nell'elenco (come nella card e nella WIRE LIST), anche se l'ordine di disegno è un altro.
- I fili partono dritti da P1 e si spostano verso il ramo nel tratto tra il 30% e il 60% della lunghezza disegnata (`SPLIT`).
- Nei rami con terminali per filo (taglio netto, puntalini…) i fili mantengono l'ordine che hanno su P1.
- WIRE LIST con la colonna `BRANCH` (`A. Cooling fan` o `Branch A`).

## Foglio

Implementato in [`render/sheet_layout.py`](../wiresheet/render/sheet_layout.py).

- **Formato:** A3 verticale (297 × 420 mm). Il codice supporta anche A4 verticale (`PAGE_SIZES`).
- **Cornice:** a 10 mm dal bordo, linea da 0,6 mm.
- **Colonne:** una per foglio (`COLUMNS`). Ogni cavo è disegnato in mm (largo 124 mm) e poi ingrandito per riempire la larghezza con 10 mm per lato (`PAD`): su A3 il fattore è circa 2,1, su A4 circa 1,4. Gli stessi 10 mm separano i cavi dal bordo in alto e dal cartiglio in basso. Un cavo più alto del foglio viene ingrandito meno, quanto basta per starci.
- **Cartiglio** in basso a destra, largo metà cornice (`TB_WIDTH`), su tre righe alte 9 mm. Ogni casella ha la didascalia piccola (1,8 mm) in alto a sinistra e il valore in grassetto (3,5 mm, ridotto se non ci sta):
  - riga 1: `TITLE`;
  - riga 2: `COMPANY` (50%) | `PROJECT` (50%);
  - riga 3: `DRAWN BY` (35%) | `DATE` (25%) | `REV` (15%) | `PAGE` (25%), con `PAGE` scritto `n/totale`.
- **Riempimento** (`layout_pages()`):
  - i cavi scendono dall'alto, con 8 mm tra un cavo e l'altro;
  - quando un cavo non entra si passa a un nuovo foglio;
  - l'ordine dei cavi è quello della lista del progetto.
- Il cartiglio è ripetuto su ogni foglio.
