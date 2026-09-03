---
id: TASK-31
title: 'Spike: rendering delle grotte come muri poligonali o come layer cave nativo'
status: To Do
assignee: []
created_date: '2026-09-03 11:34'
labels: []
milestone: m-5
dependencies:
  - TASK-26
documentation:
  - docs/SPEC.md
priority: high
type: spike
ordinal: 31000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Decisione esplicitamente rimandata a M5 dalla spec (SPEC.md §9.3): il contorno della grotta può essere reso come muri poligonali (add_wall con molti punti), che funziona di sicuro, oppure scritto nel layer cave nativo di Dungeondraft, visivamente molto migliore ma la cui codifica di cave.bitmap non è stata risolta dall'analisi (lunghezze non lineari osservate: 50x25 -> 2614 B, 30x30 -> 1892 B, 8x8 -> 154 B). Prescrizione: provare PRIMA i muri poligonali; passare al layer nativo solo se il risultato non è soddisfacente e solo dopo aver decodificato il bitmap con esperimenti su template di dimensioni diverse. Questo task produce una decisione motivata, non codice di produzione.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 È realizzato un prototipo di grotta con muri poligonali e valutato visivamente
- [ ] #2 La decisione fra muri poligonali e layer cave nativo è presa e registrata come decision di Backlog con le motivazioni
- [ ] #3 Se si sceglie il layer nativo, la codifica di cave.bitmap è documentata in docs/format.md con gli esperimenti che la confermano
- [ ] #4 Se la decodifica non riesce, la decisione ricade sui muri poligonali senza bloccare la milestone
<!-- AC:END -->
