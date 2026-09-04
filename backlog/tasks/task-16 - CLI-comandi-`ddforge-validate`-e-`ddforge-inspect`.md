---
id: TASK-16
title: 'CLI: comandi `ddforge validate` e `ddforge inspect`'
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:28'
updated_date: '2026-09-04 06:11'
labels: []
milestone: m-2
dependencies:
  - TASK-13
documentation:
  - docs/SPEC.md
priority: medium
type: feature
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Interfaccia a riga di comando per il validatore e per l'ispezione (SPEC.md §8): `ddforge validate <file>` stampa gli Issue e `ddforge inspect <file>` fa il dump della struttura e delle statistiche di una mappa. inspect e lo strumento di lavoro per capire i template reali e le mappe generate senza aprire Dungeondraft.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `ddforge validate <file>` stampa gli Issue in forma leggibile ed esce con codice 1 se ci sono errori, 0 se ci sono solo warning
- [x] #2 `ddforge inspect <file>` stampa dimensioni mappa, format, creation_build, numero di livelli, conteggio elementi per tipo e pack referenziati
- [x] #3 Entrambi i comandi gestiscono file inesistenti o JSON non valido con un messaggio chiaro invece di un traceback
- [x] #4 I comandi sono coperti da test
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Implementare _cmd_validate e _cmd_inspect in cli.py. validate: carica JSON con gestione esplicita di file mancante/JSON invalido, chiama validate(doc), stampa ogni Issue come 'SEVERITY CODE path: message', esce 1 se ci sono error, 0 se solo warning o nessun problema. inspect: dimensioni (world.width x world.height), format, creation_build, numero di livelli, conteggio elementi per tipo per livello (riusando la logica gia scritta in TASK-2 per il censimento), elenco pack da header.asset_manifest. Test con subprocess (come gia fatto per catalog in TASK-4) su file reali e su file mancante/corrotto.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implementati _cmd_validate/_cmd_inspect con un _load_document condiviso che gestisce esplicitamente file mancante e JSON non valido (messaggio chiaro su stderr, nessun traceback). validate stampa ogni Issue come '[ERRORE|AVVISO] CODICE path: messaggio' ed esce 1 solo se ci sono error (i warning da soli danno exit 0). inspect stampa dimensioni/format/build/livelli/pack e, per livello, il conteggio di ogni lista disegnabile piu i portali annidati nei muri e roofs.roofs. Verificato manualmente contro rich_reference.dungeondraft_map (42 pack, conteggi corretti) e su file mancante. 8 test via subprocess in tests/test_cli_validate_inspect.py; osservato un fallimento transitorio (PermissionError WinError 5 sullo spawn del subprocess, non riproducibile al retry) — quirk noto di Windows su creazioni rapide di processi, gia visto in TASK-4, non un difetto del codice. Suite completa: 157 test verdi.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementati ddforge validate e ddforge inspect. validate stampa gli Issue leggibili, exit 1 solo su error. inspect mostra dimensioni/format/build/pack/conteggi per livello. Entrambi gestiscono file mancante/JSON invalido senza traceback. 8 test via subprocess, suite completa 157 verdi. M2 completa.
<!-- SECTION:FINAL_SUMMARY:END -->
