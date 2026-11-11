# Changelog

Tutte le modifiche rilevanti di WireSheet. Formato [Keep a Changelog](https://keepachangelog.com/it/1.1.0/), versioni [Semantic Versioning](https://semver.org/lang/it/).

La pipeline di release usa la sezione della versione del tag come note della GitHub Release.

## [Unreleased]

### Funzionalità
- Nuovo terminale **Spelato 12 mm** (`STRIPPED 12 mm`): filo libero con 12 mm di conduttore esposto.
- **Puntalini** con la misura ricavata dalla sezione del filo (DIN 46228-4) e il codice KST, es. `FERRULE 1.5mm² L8` / `KST:E1508`, sotto l'estremità e nella WIRE LIST.
- Codici KST anche per **forcelle** (`SNYDL1-3.7`…) e **faston F** (`FDNYD2-250`…), scelti dalla sezione del filo.

### Modifiche
- Morsettiera 5,08: codice del fornitore `WJ2EDGK-5.08-nP` al posto di `TB 5.08-nP`.
- **Taglio netto** ora indica il filo tagliato a filo dell'isolante, senza spelatura: sul disegno si vede solo la sezione del filo (prima era disegnato con 4 mm di conduttore esposto).

## [1.0.0] - 2026-10-21

Prima versione pubblica. Il programma si chiamava *CableGen*: i progetti `.cablegen` si aprono ancora.

### Funzionalità
- Editor a card: una card per cavo con estremità P1/P2, miniatura del componente, tabella dei fili (pin, colore, lunghezza, sezione) e validazione in tempo reale.
- Cavi a più rami: un'estremità in ingresso e più uscite, ognuna con componente ed etichetta propri.
- Componenti: JST XH 2–7 poli, connettori circolari GM a pannello (GM-1312, GM-1712, GM-2112), morsettiera a innesto 5,08 da 2 a 8 poli, puntalini, forcelle, faston femmina 6,3, taglio netto.
- Colori dei fili IEC 60757, anche bicolore; sezioni in mm² e/o AWG con conversione automatica.
- Export PDF A3 verticale con etichette, WIRE LIST, cartiglio e numero di pagina.
- Import ed export dei cavi in Excel/CSV, con template scaricabile.
- Anteprima live del cavo o del foglio; ordinamento dei cavi per nome, componente, numero di fili e lunghezza.
- File di progetto `.wiresheet` (JSON) con revisione che sale a ogni salvataggio.
- Menu Aiuto con la versione in uso e il controllo aggiornamenti (anche all'avvio, disattivabile): se esce una release più recente propone di aprirne la pagina.

### Download
- Windows 10/11 x64: `WireSheet-1.0.0-windows-x64.zip`. Scompatta la cartella e avvia `WireSheet.exe`.
- macOS Apple Silicon: `WireSheet-1.0.0-macos-arm64.zip`.
- Gli eseguibili non sono firmati: vedi le istruzioni nel [README](https://github.com/GiacomoGuaresi/WireSheet#download).

[1.0.0]: https://github.com/GiacomoGuaresi/WireSheet/releases/tag/v1.0.0
