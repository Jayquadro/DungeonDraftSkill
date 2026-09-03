---
id: TASK-11
title: 'Script demo M1: file con 1 stanza e 1 porta'
status: Done
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:28'
updated_date: '2026-09-03 14:41'
labels: []
milestone: m-1
dependencies:
  - TASK-10
documentation:
  - docs/SPEC.md
priority: high
type: task
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Criterio di completamento di M1 (SPEC.md §5): uno script demo che, partendo dal template blank, produce un .dungeondraft_map con una stanza (pavimento + muri perimetrali chiusi) e una porta sul muro. Serve a chiudere il ciclo template -> build -> save prima che esista qualunque generatore.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Lo script gira da riga di comando e produce un file .dungeondraft_map senza errori
- [x] #2 Il file contiene un pattern pavimento, quattro muri (o un muro in loop) e una porta annidata in wall['portals']
- [x] #3 world.next_node_id e maggiore di ogni node_id presente nel file
- [x] #4 Il template di partenza non viene modificato
- [x] #5 pytest e verde su tutta la suite del core
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Creare scripts/demo_m1.py: carica templates/blank_80x80.dungeondraft_map, prepare(levels=1), disegna una stanza 10x10 quadretti (pavimento + 4 muri perimetrali separati, non un loop, per poter agganciare la porta a un muro specifico con t noto), aggiunge una porta su un muro con direction/rotation placeholder chiaramente commentati come da calibrare nel gate umano TASK-12, finalize+save su un file di output configurabile (default fuori da templates/, in una cartella generated/ ignorata da git). Eseguire lo script per produrre davvero il file. Verificare via script: nessun node_id duplicato, next_node_id maggiore di ogni id usato, hash del template sorgente invariato, pytest -q verde su tutta la suite.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Creato scripts/demo_m1.py: carica blank_80x80, prepare(levels=1), disegna una stanza 10x10 quadretti (pavimento + 4 muri perimetrali separati per poter agganciare la porta a un muro specifico), aggiunge una porta sul muro inferiore con direction=(0,1)/rotation=0.0 esplicitamente commentati come placeholder da calibrare in TASK-12. Eseguito realmente: generated/demo_m1.dungeondraft_map prodotto (1.7MB, generated/ in .gitignore, non e un artefatto da committare). Verificato manualmente e con 4 test automatici in tests/test_demo_m1.py: 1 pattern, 4 walls, 1 portal annidato (0 a livello mappa), 6 node_id tutti distinti, next_node_id (0x7) maggiore del max id usato (0x6), hash SHA-256 del template sorgente invariato prima/dopo. Suite completa: 88 test verdi.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
scripts/demo_m1.py chiude il ciclo template->build->save: genera generated/demo_m1.dungeondraft_map con 1 stanza (pavimento + 4 muri) e 1 porta annidata correttamente. Verificato con 4 test automatici (nessun node_id duplicato, next_node_id coerente, template sorgente invariato, output JSON valido) piu ispezione manuale del file reale prodotto. Suite completa: 88 test verdi. Pronto per il gate umano TASK-12.
<!-- SECTION:FINAL_SUMMARY:END -->
