# Changelog

Tutte le modifiche rilevanti di WireSheet. Formato [Keep a Changelog](https://keepachangelog.com/it/1.1.0/), versioni [Semantic Versioning](https://semver.org/lang/it/).

La pipeline di release usa la sezione della versione del tag come note della GitHub Release.

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
