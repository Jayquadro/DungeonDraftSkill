---
id: TASK-11
title: 'Script demo M1: file con 1 stanza e 1 porta'
status: To Do
assignee: []
created_date: '2026-09-03 11:28'
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
- [ ] #1 Lo script gira da riga di comando e produce un file .dungeondraft_map senza errori
- [ ] #2 Il file contiene un pattern pavimento, quattro muri (o un muro in loop) e una porta annidata in wall['portals']
- [ ] #3 world.next_node_id e maggiore di ogni node_id presente nel file
- [ ] #4 Il template di partenza non viene modificato
- [ ] #5 pytest e verde su tutta la suite del core
<!-- AC:END -->
