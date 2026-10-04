---
id: TASK-70
title: Abbellimento delle mappe building (multi-piano)
status: To Do
assignee: []
created_date: '2026-10-04 17:30'
labels: []
milestone: m-10
dependencies:
  - TASK-69
references:
  - src/ddforge/generators/building.py
  - src/ddforge/compose.py
documentation:
  - docs/SPEC-decorate.md
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Estende `ddforge decorate` (core in TASK-69) alle mappe `building`: taverne, ville, magazzini su piu piani. Zone per piano (`p0.r3`...) con i ruoli di `room.kind` (sala_comune, cucina, camera, magazzino...), il vano `scale` e l'`esterno` fra edificio e bordo canvas. Vedi docs/SPEC-decorate.md §5 e §6.5.

Particolarita: ogni piano e un livello a se; il vano scale non riceve ingombri; i muri portanti condivisi fra piu stanze cambiano texture solo se tutte le zone che li toccano concordano (§7.2); i tetti non si toccano; l'esterno riceve terreno e natura solo nei temi naturale/abbandonato.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Dry-run e applicazione funzionano su taverna, villa e magazzino, anche con pianta a L
- [ ] #2 Ogni piano e decorato separatamente e le zone sono identificate con id per piano
- [ ] #3 Il vano scale non riceve oggetti di classe ingombro (test)
- [ ] #4 Un muro condiviso cambia texture solo se tutte le zone che lo toccano concordano (test)
- [ ] #5 I tetti del file prodotto sono identici all'ingresso (test)
- [ ] #6 Test di invarianza e di proprieta di TASK-69 estesi alle mappe building
<!-- AC:END -->
