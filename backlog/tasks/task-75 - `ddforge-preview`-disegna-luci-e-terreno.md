---
id: TASK-75
title: '`ddforge preview` disegna luci e terreno'
status: To Do
assignee: []
created_date: '2026-10-04 17:43'
labels: []
milestone: m-10
dependencies:
  - TASK-67
references:
  - src/ddforge/preview.py
  - src/ddforge/cli.py
documentation:
  - docs/SPEC-decorate.md
  - docs/format.md
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
L'abbellimento di M10 e fatto in buona parte di luci, luce ambientale e terreno dipinto, ma oggi `ddforge preview` disegna solo pavimenti, muri, porte, oggetti e layer cave: il confronto prima/dopo che la skill decorator mostra all'utente sarebbe quasi identico. Jay ha chiesto di estendere il preview (docs/SPEC-decorate.md §9.1).

Il terreno si ricava da `terrain.splat` con la codifica trovata dallo spike TASK-67, colorando ogni slot con il colore medio della sua texture (o una tinta fissa per slot se la texture non e leggibile). Le luci si rendono come alone radiale additivo con colore, range e intensita della luce, sopra un velo scuro proporzionale a `environment.ambient_light`. Il preview resta un extra opzionale (Pillow) e legge sempre il file su disco.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Il preview di una mappa con terreno dipinto mostra le aree di ciascuno slot nella posizione giusta (test su fixture)
- [ ] #2 Il preview mostra ogni luce come alone del suo colore, con raggio proporzionale a `range` (test sui pixel attorno a una luce nota)
- [ ] #3 Un `ambient_light` scuro scurisce le aree lontane dalle luci, uno chiaro no (test)
- [ ] #4 `--no-lighting` produce la planimetria piatta di prima del task, byte-identica (test)
- [ ] #5 Le mappe senza luci ne terreno dipinto producono un preview invariato rispetto a prima del task
- [ ] #6 README e la sezione preview della skill generator documentano le novita e i limiti (niente ombre)
<!-- AC:END -->
