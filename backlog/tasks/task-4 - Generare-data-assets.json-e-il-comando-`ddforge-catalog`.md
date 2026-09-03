---
id: TASK-4
title: Generare data/assets.json e il comando `ddforge catalog`
status: To Do
assignee: []
created_date: '2026-09-03 11:25'
labels: []
milestone: m-0
dependencies:
  - TASK-2
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Produrre il catalogo asset del progetto leggendo i template reali, con la struttura definita in SPEC.md §6.7: elenco packs (name, id, author, version) preso da header.asset_manifest, piu le mappe logiche walls/floors/portals/roofs/paths/objects verso i path texture res://. Regola non negoziabile: ogni path res://packs/<ID>/... deve avere <ID> presente in header.asset_manifest del template, altrimenti Dungeondraft segnala missing assets al caricamento. Il comando `ddforge catalog --from <template>` deve poter rigenerare il file quando Jay installa nuovi pack.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 data/assets.json esiste e contiene solo pack ID realmente presenti in header.asset_manifest dei template
- [ ] #2 Le chiavi logiche previste in SPEC.md §6.7 sono popolate: walls, floors, portals, roofs, paths, objects (torch, table_round, chair, bed, crate, barrel, bookshelf, altar, sarcophagus, column, brazier, chest)
- [ ] #3 `ddforge catalog --from templates/rich_reference.dungeondraft_map` rigenera data/assets.json in modo deterministico
- [ ] #4 Ogni texture nel catalogo e verificata come esistente nel template o negli asset di default (uses_default_assets)
- [ ] #5 Un test verifica che nessuna voce del catalogo referenzi un pack ID assente dal manifest
<!-- AC:END -->
