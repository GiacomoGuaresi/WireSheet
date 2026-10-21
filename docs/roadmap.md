# Roadmap

Sviluppo agile a piccoli step: ogni step viene mostrato e approvato prima di passare al successivo. Le idee future si sviluppano solo quando servono.

Legenda: ✅ fatto · 🔄 in corso · ⏳ da fare · 💡 idea futura

## ✅ Step 1 — Disegno di un cavo e PDF da script

- [x] Modello `Cable` / `End` / `Wire` con validazione
- [x] Catalogo: JST XH 2–7P, puntalino, forcella, taglio netto
- [x] Colori IEC, compresi i bicolore
- [x] Disegno con QPainter in mm: estremità, fili colorati, incroci, quota, codici, WIRE LIST
- [x] Export PDF (A4 orizzontale, cavi impilati)
- [x] `python -m wiresheet.demo` con 5 cavi di esempio
- [x] Test su modello, righe dei fili e export

**Decisioni prese:**
- I testi sul disegno restano in inglese finché non arriva la scelta IT/EN.
- Puntalini e forcelle restano senza codice componente per ora; potrebbe servire in futuro.

## ✅ Step 2 — Finestra minima

- [x] `python -m wiresheet` apre la finestra principale
- [x] Form: tendine per il tipo di estremità P1/P2 e per le posizioni del JST XH
- [x] Tabella fili modificabile (pin P1, colore, pin P2, lunghezza), con aggiunta e rimozione di righe
- [x] "+ Filo" assegna il primo pin libero e, se il connettore è pieno, aggiunge una posizione
- [x] Anteprima live, che usa lo stesso `draw_cable()` del PDF; zoom con −/+/Adatta e Ctrl + rotella
- [x] Errori di validazione mostrati nella finestra

## ✅ Step 3 — Più cavi e impaginazione

- [x] Lista dei cavi nel progetto: nuovo, duplica, elimina (con conferma), sposta su/giù
- [x] Nomi automatici (CABLEn = numero più alto + 1), modificabili
- [x] Lista con il riepilogo `XH-2 → Puntalini` e ⚠ sui cavi con errori
- [x] Campi di progetto P/N e Titolo
- [x] Foglio A3 orizzontale con cornice, 3 colonne separate da linee, riquadro `P/N:x` + titolo
- [x] Cavi distribuiti in colonne dall'alto in basso, nuovo foglio quando è pieno (15 cavi → 2 fogli)
- [x] Export PDF dell'intero progetto (bloccato se qualche cavo ha errori)
- [x] Test: nessuna sovrapposizione, cavi dentro l'area utile, ordine rispettato (A3 e A4)

## ✅ Step 4 — Salva / Apri progetto

- [x] File di progetto JSON (`.wiresheet`) con versione del formato
- [x] Menu File: Nuovo (Ctrl+N), Apri (Ctrl+O), Salva (Ctrl+S), Salva con nome, Esporta PDF (Ctrl+E), Esci
- [x] Asterisco nel titolo della finestra se ci sono modifiche non salvate; richiesta di salvataggio alla chiusura e prima di aprire o creare un progetto
- [x] `python -m wiresheet progetto.wiresheet` apre direttamente un progetto
- [x] Test: salvando e riaprendo il progetto si ritrovano gli stessi dati; file non validi rifiutati

## ✅ Step 5 — UI a card

- [x] Pila di card, una per cavo, al posto di lista + editor
- [x] Intestazione della card: comprimi/espandi, nome modificabile, riepilogo, stato ✓/⚠, Duplica, ↑, ↓, Elimina
- [x] Card attiva evidenziata (click, modifica o focus)
- [x] Toolbar con P/N, Titolo, + Nuovo cavo, Esporta PDF, Anteprima
- [x] Pannello anteprima laterale apribile (F2), chiuso di default; modalità **Cavo** e **Foglio** (foglio A3 in cui cade il cavo)
- [x] Menu Vista: Espandi tutto / Comprimi tutto; progetti con più di 5 cavi aperti compressi
- [x] Rotella: scorre la pagina senza cambiare tendine o numeri; tabella fili ad altezza fissa
- [x] Stile: card bianche arrotondate, pulsante primario per l'export

## ✅ Step 6 — Rifinitura UI

- [x] Linguetta verticale "ANTEPRIMA" sul bordo destro, centrata, che apre e chiude il pannello (anche F2 o menu Vista)
- [x] Estremità su tre righe: titolo → tendina componente → [variante (n° pin)] [miniatura del componente]
- [x] Miniatura disegnata con gli stessi simboli del PDF (JST XH, puntalini, forcelle, taglio netto)
- [x] Icone in stile Lucide (SVG inline, nessuna dipendenza): azioni delle card, toolbar, menu, pannello anteprima, stato ✓/⚠
- [x] Tabella fili con le colonne Pin P1 | Colore | Lunghezza | Pin P2
- [x] Tendina colore con il campione del colore (righe per i bicolore come YE/GN)

## ✅ Step 7 — Template e import Excel/CSV

- [x] File → **Esporta template Excel/CSV**: colonne, 2 cavi di esempio, tendine in Excel, foglio "Istruzioni"
- [x] File → **Importa cavi da Excel/CSV** (Ctrl+I): sceglie se aggiungere in fondo o sostituire i cavi
- [x] File → **Esporta cavi in Excel/CSV**: stesso formato, per modificare i cavi in Excel e reimportarli
- [x] Una riga per filo; le righe con lo stesso nome di cavo formano un cavo; componenti solo sulla prima riga
- [x] Valori tolleranti: `rosso`/`RD`, `jst_xh`/`JST XH`, `4 pin`, `12,5`; intestazioni anche in inglese; CSV con `;` o `,`
- [x] Errori con numero di riga; se ci sono errori di formato non viene importato nulla
- [x] Pulsanti Importa e Template nella toolbar

## ✅ Step 8 — Connettori circolari GM a pannello

- [x] Serie GM1312, GM1712, GM2112 (fissaggio posteriore), femmina `/S` e maschio `/P`, con tutte le disposizioni del catalogo (anche 5A/5B/5C e 12 pin)
- [x] Coordinate dei pin trascritte dalle tabelle "Contact arrangement"
- [x] Disegno: corpo con flangia e filettatura + schema dei pin lato saldatura sotto il codice, pin usati in grassetto
- [x] UI: tendina variante con genere e pin (es. `S5A · 5 pin femmina`), miniatura, "+ Filo" passa alla variante più grande
- [x] Import/export Excel/CSV e file di progetto con il campo `variant`
- [x] Demo: CABLE F (GM2112/S4 → puntalini) e CABLE G (GM1712/S7 → JST XH-3)

**Decisioni prese:**
- Lo schema dei pin è visto dal lato saldatura, quello che serve a chi cabla.
- Codice stampato `GM2112/S4` (formato del catalogo), seguito da `PANEL, REAR MOUNT` — sostituito allo step 9 da `GM-2112/S-4P`.

## ✅ Step 9 — Disegni dei connettori

- [x] Disegni di riferimento in `drawings/` (SVG + script `gen_*.py`), approvati uno alla volta
- [x] JST XH ridisegnato dal datasheet XHP: collarino sul lato fili, finestre dei contatti
- [x] Nuove estremità: **morsettiera a innesto 5,08** (2–8 poli) e **Faston F 6,3**
- [x] Puntalino, forcella, faston e taglio netto con la geometria dei disegni
- [x] GM a pannello: vista laterale nuova (filetto, flangia, dado, contatti a saldare), fili che convergono sui contatti, schema pin con filetto, chiave e numeri dentro i contatti
- [x] Codici GM nel formato del fornitore: `GM-2112/S-4P`, `GM-2112/S-5P-A`
- [x] Demo: CABLE H (morsettiera 4P → faston)

**Decisioni prese:**
- Il pin 1 è in basso su tutti i connettori. *Cambiato dopo lo step 10:* P2 a destra è ruotato di 180° rispetto a P1 (non specchiato), quindi a sinistra il pin 1 è in basso e a destra in alto.
- Lo schema pin dei GM resta visto dal lato saldatura. *Cambiato dopo lo step 10:* lo schema pin dei GM è stato tolto dal PDF perché fuorviante (coordinate non affidabili).

## 🔄 Step 10 — Cavi a più rami (1 ingresso, più uscite)

Esempi dall'elenco cavi: `FANS, MAT SENSOR` (GM-1712/S-7P → XH-2, morsettiera 3P, fili liberi), `TH EXT` (GM-1712/S-9P → 4× XH-2).

- [x] **10a** Modello `Branch` (estremità + fili + nome) e `Cable.branches`; validazione per ramo
- [x] **10a** Disegno ad albero: P1 a sinistra, rami impilati a destra con etichetta `A · nome · lunghezza`, WIRE LIST con colonna BR
- [x] **10a** Demo: `FANS, MAT SENSOR` e `TH EXT`
- [x] **10b** Import/export Excel/CSV con la colonna "Ramo" (ramo = nome + componente P2)
- [x] **10b** File di progetto versione 2 con i rami (legge ancora la versione 1)
- [x] WIRE LIST autoesplicativa: `FROM (pin) | COLOR (nome) | LENGTH | SECTION | BRANCH | TO (pin)`, larga quanto il cavo; rami con la lettera come nella card
- [x] **10c** Sezione del filo in mm² e/o AWG (quella mancante si ricava dalla tabella di equivalenza): una sola colonna *Sezione* in card, Excel/CSV e WIRE LIST, scritta `0.25mm² (24AWG)`
- [x] Caso minimo: `FANS, MAT SENSOR.csv` / `.wiresheet` / `.pdf` (GM-1712/S-7P → XH-2, XH-3, taglio netto, 0,5 mm²)
- [x] Foglio a 2 colonne con i cavi ingranditi per riempire la colonna (testi circa +56% su A3)
- [x] **10d** Conversione dell'elenco cavi del fornitore nel formato WireSheet (file non pubblicati; 41 cavi, 115 fili, 5 fogli A3). GM sempre su P1, rami per funzione + componente o per pin ripetuti, `-` = taglio netto, `-L` ignorato
- [x] **10e** Rami nelle card: a destra l'elenco dei rami (nome, componente, miniatura, elimina) con "+ Ramo"; tabella fili unica con la colonna **Ramo** (visibile solo con più rami); Pin P2 segue l'estremità del ramo; "+ Filo" aggiunge nel ramo dell'ultimo filo; eliminando un ramo i suoi fili passano al primo
- [x] Tolto lo schema pin dei GM dal PDF (fuorviante): la WIRE LIST parte subito sotto i codici
- [x] Sezioni scritte `mm²`; tabella AWG ↔ mm² da Multi/Cable (1 mm² = 17AWG, aggiunto 0,38 mm² = 21AWG); etichette pin `1 RD` e `2 nc` (nc in corsivo) per i pin senza filo
- [x] Fogli A3 verticali con una colonna (cavi ingranditi circa 2,2×); etichette sul disegno (fascetta con scritto LABEL in verticale + linea tratteggiata con freccia + cartellino): una per cavo vicino a P1 e una per ogni ramo; tolte la quota dei cavi semplici e la lunghezza nell'etichetta dei rami
- [x] Cartiglio in fondo a ogni foglio al posto del riquadro P/N: azienda, titolo, progetto/macchina, disegnato da, data, revisione, pagina `n/totale`; finestra **Cartiglio** dalla toolbar
- [x] Cartiglio largo metà foglio, in basso a destra, su 3 righe
- [x] Revisione numerica: +1 a ogni salvataggio con modifiche, modificabile a mano; l'export chiede di salvare prima
- [x] UI: cartiglio come card fissa in cima alla pila (sfondo crema, non comprimibile); tolta la toolbar; menu **Cavi** con Nuovo cavo, Importa, Template, Esporta cavi; Esporta PDF solo nel menu File
- [x] Contorno dei fili dello stesso colore più scuro (non più nero)
- [x] Taglio netto disegnato come conduttore esposto lungo 4 mm
- [x] Casella **Etichetta** per ogni ramo nella card: nasconde l'etichetta del ramo sul disegno
- [x] Menu **Ordina**: nome (A → Z, Z → A), componente P1, numero di fili, lunghezza
- [x] Menu: File | Importa/Esporta | Ordina | Vista
- [x] La card sotto il mouse diventa attiva e l'anteprima la mostra
- [x] Icona dell'app (`resources/icon.svg` + `icon.ico`), anche nella barra delle applicazioni di Windows
- [x] 10 mm di margine tra la cornice (e il cartiglio) e cavi e tabelle

**Decisioni prese:**
- L'unico connettore va sempre su P1 (a sinistra); nei file del fornitore, dove è su "Terminale 2", i lati vanno scambiati.
- I rami si distinguono per nome (la funzione); il nome è facoltativo; i rami si identificano con una lettera nell'ordine dell'elenco: `A. Cooling fan`, oppure `Branch A` senza nome.
- P1 può essere qualsiasi estremità, anche "tutti puntalini" o "tutti faston". Terminali diversi sullo stesso lato (es. AC IN: 2 puntalini + 1 taglio netto) sono rami diversi, anche senza nome. La lunghezza è sempre per filo.
- Disegno ad albero, non un blocco per ramo.
- Card: tabella fili unica con la colonna Ramo (non un blocco per ramo). Nella card e nel PDF i rami hanno la stessa lettera (ordine dell'elenco); nel PDF l'ordine di disegno può essere diverso.
- L'elenco del fornitore non avrà un importatore dedicato: si converte una volta nel formato WireSheet.
- Nei file del fornitore `-` come terminale vuol dire taglio netto; il suffisso `-L` dei GM si ignora.
- Nessuna quota di lunghezza sul disegno (né cavi semplici né rami): le lunghezze sono nella WIRE LIST.
- Campo P/N tolto: nei file vecchi viene ignorato. Il nome proposto per i file è il titolo del progetto.
- Le etichette mostrano il nome del cavo (vicino a P1) e il titolo del ramo (vicino al suo connettore); un cavo semplice ha solo l'etichetta vicino a P1.

## ✅ Pubblicazione

- [x] Nome definitivo **WireSheet** (prima CableGen); i progetti `.cablegen` si aprono ancora
- [x] Repository GitHub pubblico con licenza MIT
- [x] CI: test su Windows e macOS a ogni push e pull request
- [x] Release: tag `v*` → eseguibili PyInstaller (`WireSheet.exe`, `WireSheet.app`) allegati alla GitHub Release
- [x] **v1.0.0**: versione in `wiresheet/__init__.py` (finestra Informazioni, Info.plist, proprietà dell'`.exe`); la pipeline rifiuta i tag che non corrispondono
- [x] Controllo aggiornamenti dal menu Aiuto e all'avvio (disattivabile): se c'è una release più recente chiede se aprire la pagina di download
- [x] Windows distribuito come cartella zip (avvio rapido, meno falsi positivi degli antivirus); macOS solo Apple Silicon
- [x] Smoke test degli eseguibili in pipeline (`--self-test`: PDF demo + template Excel)
- [x] `CHANGELOG.md` come testo delle release; asset con la versione nel nome e `SHA256SUMS.txt`
- [x] README anche in inglese; demo e test con un'azienda di fantasia

## ⏳ Prossimo passo

- [ ] Feedback sullo stile del disegno (proporzioni, spessori, posizione del nome)
- [ ] Decidere la prossima funzione dalla lista qui sotto

## 💡 Idee future (quando serviranno)

- Firma e notarizzazione degli eseguibili (Apple Developer ID, certificato di code signing per Windows)
- Doppio clic sui file `.wiresheet` (Finder: `QFileOpenEvent` + `CFBundleDocumentTypes`; associazione dei file su Windows)
- Eseguibili per Mac Intel e Linux
- Lingua dei testi IT/EN selezionabile all'export
- Libreria componenti modificabile (codici, terminali di default)
- Altri connettori: altre serie JST
- Altri terminali: occhielli, faston maschio
- Quota di posizione delle etichette; testo dell'etichetta modificabile
- Tipo del filo (es. UL1007)
- Giunzioni (splice) e cavi multipolari con guaina
- Scelta del formato del foglio dall'interfaccia (il codice supporta già A3 e A4)
