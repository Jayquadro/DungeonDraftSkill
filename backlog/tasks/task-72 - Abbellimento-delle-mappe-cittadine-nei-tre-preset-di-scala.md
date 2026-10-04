---
id: TASK-72
title: Abbellimento delle mappe cittadine nei tre preset di scala
status: To Do
assignee: []
created_date: '2026-10-04 17:31'
updated_date: '2026-10-04 17:43'
labels: []
milestone: m-10
dependencies:
  - TASK-70
references:
  - src/ddforge/generators/city.py
  - src/ddforge/generators/landmarks.py
  - src/ddforge/compose.py
documentation:
  - docs/SPEC-decorate.md
  - README.md
priority: medium
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Estende `ddforge decorate` (core in TASK-69, interni di edifici in TASK-70) alle mappe `city`. Vedi docs/SPEC-decorate.md §5 e §6.5.

Zone: strade (`s*`, flag `principale`), piazze (`pz*`), cortili interni ai lotti (`cort*`), fascia extramurale (`extra`), rive del fiume (`riva`, flag `a_valle`), banchina, landmark open-air (`lm.<kind>`). A `isolato` gli interni degli edifici si decorano come le mappe building. A `quartiere`/`citta` niente interni (gli edifici sono sprite): solo terreno, alberi/cespugli nei cortili e lungo il fiume, carretti e bancarelle sulle piazze, a una scala coerente con il preset (mai un albero piu grande di una casa). Per decisione di Jay NON c'e alcun tetto al numero di oggetti aggiunti ne alla dimensione del file: l'aumento si misura e si riporta, senza limitarlo.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Le zone cittadine sono derivate dal Blueprint con id stabili e alias leggibili (test)
- [ ] #2 A `isolato` gli interni degli edifici sono decorati con le stesse regole di TASK-70
- [ ] #3 Nessun oggetto aggiunto si sovrappone a un edificio, a un landmark o alla carreggiata di una strada (test su 30 seed per preset)
- [ ] #4 Il lato lungo di ogni oggetto aggiunto a `quartiere`/`citta` non supera quello medio di un edificio del preset (test)
- [ ] #5 Etichette, sprite di edifici e landmark del file prodotto sono identici all'ingresso (test)
- [ ] #6 L'aumento di dimensione del file e il numero di oggetti aggiunti sono misurati per i tre preset e i sei temi e riportati nella nota di chiusura, senza alcun tetto imposto
<!-- AC:END -->
