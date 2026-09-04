---
id: TASK-35
title: 'generators/city.py — rete stradale, isolati, lotti e piazze'
status: To Do
assignee: []
created_date: '2026-09-03 11:35'
updated_date: '2026-09-04 07:23'
labels: []
milestone: m-8
dependencies:
  - TASK-34
  - TASK-28
documentation:
  - docs/SPEC.md
priority: high
type: feature
ordinal: 35000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Generatore di quartieri e città (SPEC.md §9.4): partizione ricorsiva del canvas in isolati con strade larghe 2-4 quadretti e una via principale più larga; suddivisione degli isolati in lotti con fronte strada garantito; un edificio per lotto riusando building.py a un solo piano, con arretramento casuale dal fronte; tetti su tutti gli edifici, perché in una mappa cittadina si vede dall'alto; 1-2 isolati lasciati vuoti come piazze con pavimentazione diversa e pozzo o fontana al centro. Le strade vanno realizzate con add_path e texture di acciottolato, non come pattern.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Ogni lotto ha fronte strada e nessun edificio è inaccessibile
- [ ] #2 Le strade sono realizzate con add_path e texture di acciottolato, non con pattern
- [ ] #3 La via principale è più larga delle strade secondarie
- [ ] #4 Tutti gli edifici hanno un tetto
- [ ] #5 Sono presenti 1-2 piazze con pavimentazione diversa e un elemento centrale
- [ ] #6 Il documento generato passa validate() senza errori
<!-- AC:END -->
