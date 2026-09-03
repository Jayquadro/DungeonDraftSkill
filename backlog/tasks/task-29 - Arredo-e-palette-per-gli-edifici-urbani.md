---
id: TASK-29
title: Arredo e palette per gli edifici urbani
status: To Do
assignee: []
created_date: '2026-09-03 11:34'
labels: []
milestone: m-4
dependencies:
  - TASK-28
  - TASK-23
documentation:
  - docs/SPEC.md
priority: medium
type: feature
ordinal: 29000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Estensione di furnish e delle Palette agli stili tavern, manor e warehouse (SPEC.md §6.7, §9.5). Un edificio arredato con la palette del dungeon non è utilizzabile: servono pavimenti in assi, tavoli, letti, casse e scaffali coerenti con la funzione della stanza.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 palette_for restituisce palette specifiche per tavern, manor e warehouse
- [ ] #2 L'arredo rispetta il kind della stanza: camere con letti, sala comune con tavoli e sedie, magazzino con casse e barili
- [ ] #3 Nessun oggetto ostruisce porte o scale
- [ ] #4 Le luci sono collocate in modo plausibile per un ambiente abitato
<!-- AC:END -->
