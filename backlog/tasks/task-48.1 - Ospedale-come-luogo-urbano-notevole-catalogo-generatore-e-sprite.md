---
id: TASK-48.1
title: 'Ospedale come luogo urbano notevole: catalogo, generatore e sprite'
status: To Do
assignee: []
created_date: '2026-09-11 13:37'
labels: []
milestone: m-8
dependencies: []
documentation:
  - docs/sprite-luoghi.md
parent_task_id: TASK-48
ordinal: 49000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Fra i luoghi notevoli delle mappe cittadine manca l'ospedale. Il piu' vicino e' il lazzaretto, che e' un'altra cosa: edificio d'isolamento, lungo e basso, recintato, piazzato fuori le mura. Un ospedale cittadino sta invece dentro le mura, in mezzo al tessuto abitato, ed e' uno dei luoghi che il tavolo cerca per primi. Il prompt per generare lo sprite dedicato (nm_ospedale.png, 768x768, tetto ricolorabile) e' gia' scritto in prompt/01-ospedale.md; quello che manca e' il luogo dentro il sistema: non compare fra i tipi generabili da generators/city.py, non ha una voce in assets._CITY_LANDMARK_SPRITES e non e' elencato in docs/sprite-luoghi.md. Finche' lo sprite dipinto non esiste serve uno sprite di ripiego scelto fra i 440 object gia' in catalogo.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Il tipo di luogo `ospedale` e' generabile da generators/city.py e compare sulla mappa con l'etichetta Ospedale
- [ ] #2 assets._CITY_LANDMARK_SPRITES ha una voce `ospedale` che risolve a uno sprite presente nei pack installati, cosi' il luogo si disegna anche prima che nm_ospedale.png esista
- [ ] #3 L'ospedale e' richiedibile esplicitamente come gli altri luoghi notevoli, e quando non e' richiesto puo' uscire a sorte al piu' una volta per mappa
- [ ] #4 docs/sprite-luoghi.md elenca l'ospedale fra i luoghi chiusi, con la dimensione misurata a cui viene disegnato nei preset quartiere e citta
- [ ] #5 I golden di tests/fixtures/golden sono rigenerati e la suite passa
<!-- AC:END -->
