---
id: TASK-17
title: 'assets.py — catalogo, Palette e required_packs'
status: To Do
assignee: []
created_date: '2026-09-03 11:31'
labels: []
milestone: m-3
dependencies:
  - TASK-4
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Modulo che traduce l'intento semantico in texture concrete (SPEC.md §6.7): load_catalog legge data/assets.json, palette_for(style, catalog) restituisce una Palette coerente (wall, floor, door, accents) per style in {dungeon, crypt, sewer, cave, tavern, manor, warehouse, city}, required_packs(doc) estrae gli ID pack referenziati dalle texture usate. Regola: assets.py non deve MAI restituire un path il cui pack non è nel template, altrimenti Dungeondraft segnala missing assets al caricamento.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 load_catalog legge data/assets.json e fallisce con messaggio esplicito se il file manca o è malformato
- [ ] #2 palette_for restituisce una Palette valida per tutti e otto gli stili previsti
- [ ] #3 required_packs(doc) estrae correttamente gli ID da tutti i path res://packs/<ID>/... del documento
- [ ] #4 Un test verifica che ogni Palette restituita usi solo texture i cui pack sono nel manifest del template
- [ ] #5 palette_for su uno stile sconosciuto solleva un errore esplicito invece di restituire una palette a caso
<!-- AC:END -->
