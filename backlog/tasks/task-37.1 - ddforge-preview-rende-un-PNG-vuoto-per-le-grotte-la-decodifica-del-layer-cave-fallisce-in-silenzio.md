---
id: TASK-37.1
title: >-
  ddforge preview rende un PNG vuoto per le grotte: la decodifica del layer cave
  fallisce in silenzio
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-24 09:29'
updated_date: '2026-09-24 12:54'
labels: []
milestone: m-6
dependencies: []
references:
  - src/ddforge/preview.py
  - src/ddforge/cave_bitmap.py
  - src/ddforge/generators/cave.py
  - tests/test_preview.py
  - skill/SKILL.md
  - skill/references/examples.md
documentation:
  - docs/format.md
  - docs/SPEC.md
parent_task_id: TASK-37
priority: medium
type: bug
ordinal: 67000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
`ddforge preview` su una mappa prodotta da `ddforge generate cave` scrive un PNG completamente nero, senza nessun messaggio di errore e con codice di uscita 0.

Il file `.dungeondraft_map` NON e' difettoso: `ddforge validate` sulla stessa grotta risponde "Nessun problema trovato", ed e' la mappa che Jay ha gia' approvato al gate umano di M5. E' l'anteprima a mentire, ed e' il caso peggiore possibile: un PNG nero sembra una generazione fallita, quindi il difetto spinge chi lo guarda a buttare via una mappa buona o a rigenerarla inutilmente.

**Perche' succede** (osservato, non ipotizzato): `preview._draw_cave_bitmap` viene chiamato regolarmente, ma `cave_bitmap.decode_cave_bitmap` solleva `IndexError` sul blob della grotta; il `try/except (ValueError, IndexError): return` in `preview.py` lo assorbe e lascia l'immagine vuota. L'except silenzioso e' il motivo per cui il difetto e' invisibile: qualunque regressione futura nella decodifica si manifesterebbe allo stesso modo, cioe' per niente.

**Riproduzione** (osservata il 2026-09-24, dalla root del repo): generando una grotta con `ddforge generate cave --template templates/blank_80x80.dungeondraft_map --out g.dungeondraft_map --width 78 --height 78 --seed 1337`, il successivo `ddforge preview g.dungeondraft_map --out g.png` esce con codice 0 e scrive un PNG tutto nero, mentre `ddforge validate g.dungeondraft_map` risponde "Nessun problema trovato." Chiamando direttamente la decodifica sul documento scritto, `decode_cave_bitmap(level['cave']['bitmap'], 80, 80)` solleva `IndexError: list index out of range` (blob di 44831 caratteri, `world` 80x80).

**E' una regressione, non una funzione mai esistita.** Le implementation notes di TASK-37 (il task padre) riportano la verifica visiva del preview di `generated/cave_m5.dungeondraft_map` con esito positivo, "bitmap nativo leggibile, forma organica corretta". Fra quel momento e oggi qualcosa ha disallineato scrittura e lettura del bitmap: capire cosa fa parte del lavoro.

**Contesto d'uso**: la skill `dungeondraft-map-generator` (TASK-38) propone `ddforge preview` come autocontrollo prima di consegnare una mappa, e documenta questo difetto come limite noto delle grotte proprio perche' non fosse scambiato per una mappa vuota. Quando il baco e' chiuso quella nota va tolta, altrimenti la skill continua a sconsigliare uno strumento che funziona.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `ddforge preview` su una mappa prodotta da `ddforge generate cave` produce un PNG in cui la forma della grotta e' visibile e riconoscibile, non un'immagine vuota
- [x] #2 La decodifica del layer cave non fallisce piu' sulle grotte prodotte dal generatore, verificato su almeno due dimensioni di mappa diverse (non solo 80x80)
- [x] #3 Il preview non degrada mai piu' in silenzio: se la decodifica del layer cave fallisce, il comando lo segnala con un messaggio chiaro invece di scrivere un PNG vuoto uscendo con codice 0
- [x] #4 Esiste un test automatico di round-trip (genera una grotta -> decodifica/preview) che fallisce se l'anteprima delle grotte torna vuota
- [x] #5 Il preview resta corretto per gli altri algoritmi (dungeon, building, city): nessuna regressione nei test esistenti di tests/test_preview.py
- [x] #6 Tolto da skill/SKILL.md e skill/references/examples.md l'avviso che il preview delle grotte non e' affidabile, una volta che lo e'
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Root cause confermata riproducendo il bug: `ddforge generate cave` scrive `cave.bitmap` dimensionato su blueprint.width/height (da --width/--height, default 40x40), ma non tocca mai world.width/height nel documento finale, che restano quelli del template (es. 80x80). Per gli altri algoritmi questo e' voluto (si puo' generare in una sotto-regione di un template piu' grande, vedi test_preview.py riga 92-95), ma il layer cave nativo copre SEMPRE l'intera mappa per formato (docs/format.md §14: "dipende SOLO dalle dimensioni della mappa"): un mismatch produce un JSON valido che pero' non decodifica piu' (IndexError), e ddforge validate non lo rileva perche' _check_blob_lengths non controlla mai cave.bitmap/entrance_bitmap (solo tiles.cells/terrain.splat).
2. cli.py _cmd_generate: ramo dedicato per is_cave che usa sempre world.width/world.height del template caricato (mai un default 40x40, che per cave non ha senso), e rifiuta con un errore chiaro (stderr, return 1, nessun file scritto) un --width/--height esplicito che non corrisponda alle dimensioni del template.
3. cave_bitmap.decode_cave_bitmap: solleva ValueError con lunghezza attesa/osservata invece di lasciar propagare un IndexError nudo quando il blob e' troppo corto per width/height richiesti.
4. preview.py _draw_cave_bitmap: rimuove il try/except silenzioso, lascia propagare il ValueError fino a _cmd_preview (che gia' lo stampa come "Errore: ..." e ritorna 1) invece di scrivere un PNG vuoto con codice 0.
5. Test: round-trip generate cave -> preview su almeno due dimensioni mappa diverse (blank_80x80 e blank_160x160), test che --width/--height incoerenti con il template falliscono chiaramente in generate, test che un cave.bitmap corrotto fa fallire preview con messaggio chiaro invece di PNG vuoto/exit 0. Verifica nessuna regressione sui test esistenti di test_preview.py/test_cli_generate.py.
6. Rimuove da skill/SKILL.md e skill/references/examples.md l'avviso sul preview delle grotte inaffidabile.
7. Eseguo la suite completa, aggiorno note di implementazione, verifico gli acceptance criteria uno per uno prima di chiudere.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Causa radice confermata riproducendo il bug: ddforge generate cave scriveva cave.bitmap dimensionato su blueprint.width/height (da --width/--height, default 40x40), ma world.width/height nel documento restavano quelli del template (es. 80x80, mai toccati da generate). Per dungeon/building/city questo e' voluto (si genera dentro una sotto-regione di un template piu' grande, vedi commento gia' presente in test_preview.py:92-95), ma il layer cave nativo copre SEMPRE l'intera mappa per formato (docs/format.md §14: la lunghezza dipende solo da world.width/height, mai dal contenuto). Con dimensioni diverse il JSON restava valido e ddforge validate non lo segnalava (_check_blob_lengths in validate.py controlla solo tiles.cells/terrain.splat, mai cave.bitmap/entrance_bitmap — gap non toccato in questo task, riportato all'utente come possibile follow-up), ma preview.py falliva la decodifica con IndexError, assorbito in silenzio da un except (ValueError, IndexError): return che lasciava un PNG vuoto con exit 0.

Fix implementato:
- cli.py: nuovo ramo is_cave in _cmd_generate. Nessun default 40x40 per 'cave' (non ha senso: il layer copre sempre l'intera mappa): usa sempre world.width/height del template caricato. Un --width/--height esplicito diverso da quelli del template e' ora un errore chiaro (stderr, exit 1, nessun file scritto), non piu' un file rotto silenzioso.
- cave_bitmap.decode_cave_bitmap: solleva ValueError con lunghezza attesa/osservata invece di lasciar propagare un IndexError nudo quando il blob e' troppo corto.
- preview.py _draw_cave_bitmap: rimosso il try/except silenzioso; il ValueError ora propaga fino a _cmd_preview, che gia' lo stampa come "Errore: ..." e ritorna 1 (nessuna modifica necessaria li').
- skill/SKILL.md e skill/references/examples.md: rimossa la nota "bug noto, PNG nero per le grotte"; l'esempio di generate cave in examples.md non passa piu' --width/--height (avrebbe fallito con il nuovo controllo, dato che usava 78x78 contro un template 80x80).

Verifica: 111 test mirati (test_preview.py, test_cli_generate.py, test_cave_bitmap_format.py, test_generators_cave.py, test_cave_gate.py, test_validate.py) verdi, poi suite completa 779 passed/1 skipped (skip preesistente non correlato). Nuovi test: round-trip generate->preview su blank_80x80 e blank_160x160 (AC2/AC4), rifiuto chiaro di --width/--height incoerenti in generate cave, preview su cave.bitmap corrotto (blob troncato a mano) che ora fallisce con exit 1 e messaggio "cave.bitmap" invece di scrivere un PNG vuoto (AC3). Verificato anche manualmente end-to-end: generate cave + preview su entrambi i template producono PNG con sia _BACKGROUND che _FLOOR nei colori (non piu' monocromatico).
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Causa radice: 'ddforge generate cave' scriveva cave.bitmap dimensionato sul contenuto (--width/--height, default 40x40) senza mai aggiornare/verificare world.width/height del template (che restavano es. 80x80): il layer cave nativo copre pero' sempre l'intera mappa per formato (docs/format.md §14), quindi un mismatch produceva un JSON valido ma indecodificabile, non intercettato da ddforge validate. preview.py assorbiva l'IndexError risultante in silenzio, scrivendo un PNG nero con exit 0. Fix: cli.py ora usa sempre le dimensioni del template per 'cave' (mai un default 40x40) e rifiuta con un errore chiaro un --width/--height incoerente prima di scrivere qualsiasi file; cave_bitmap.decode_cave_bitmap solleva un ValueError descrittivo invece di un IndexError nudo; preview.py non assorbe piu' l'errore, lo lascia propagare come messaggio chiaro + exit 1. Rimossa la nota 'bug noto' da skill/SKILL.md e skill/references/examples.md. Verificato con 779 test verdi (1 skip preesistente non correlato) inclusi nuovi test di round-trip generate->preview su blank_80x80 e blank_160x160, rifiuto del mismatch --width/--height, e fallimento chiaro su bitmap corrotto.
<!-- SECTION:FINAL_SUMMARY:END -->
