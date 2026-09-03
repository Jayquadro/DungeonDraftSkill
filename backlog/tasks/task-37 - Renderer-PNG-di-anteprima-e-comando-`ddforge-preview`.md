---
id: TASK-37
title: Renderer PNG di anteprima e comando `ddforge preview`
status: To Do
assignee: []
created_date: '2026-09-03 11:35'
labels: []
milestone: m-6
dependencies:
  - TASK-26
documentation:
  - docs/SPEC.md
priority: medium
type: feature
ordinal: 37000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Anteprima raster della planimetria senza dover aprire Dungeondraft (SPEC.md §1.3, §5, §8). Unico punto del progetto in cui è ammessa una dipendenza esterna, Pillow, che deve restare opzionale: il core continua a funzionare senza. Il renderer legge il .dungeondraft_map generato, non il Blueprint, così l'anteprima verifica davvero ciò che è stato scritto sul file.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 ddforge preview <file.dungeondraft_map> produce un PNG leggibile della planimetria
- [ ] #2 Il PNG mostra muri, porte, pavimenti e oggetti in modo distinguibile
- [ ] #3 Il renderer legge il file .dungeondraft_map, non il Blueprint in memoria
- [ ] #4 Pillow è una dipendenza opzionale: il core e gli altri comandi funzionano senza averla installata
- [ ] #5 Se Pillow manca, il comando preview lo dice con un messaggio chiaro invece di un traceback
- [ ] #6 Il comando è coperto da test che verificano la produzione del PNG
<!-- AC:END -->
