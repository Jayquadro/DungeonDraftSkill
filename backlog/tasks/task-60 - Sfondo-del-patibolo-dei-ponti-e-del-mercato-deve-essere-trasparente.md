---
id: TASK-60
title: 'Sfondo del patibolo, dei ponti e del mercato deve essere trasparente'
status: In Progress
assignee:
  - '@claude'
created_date: '2026-09-18 14:18'
labels: []
dependencies: []
documentation:
  - docs/sprite-luoghi.md
ordinal: 61000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Jay ha aperto in Dungeondraft le mappe rigenerate per TASK-54 (piazza in terra battuta, chr_dirt) e ha notato che tre elementi mostrano un rettangolo di pavimentazione con sfondo opaco invece che trasparente: il patibolo, i ponti e il mercato. Tutti e tre passano dallo stesso meccanismo: compose.draw_landmark disegna add_pattern(rect, palette.floors[landmark.ground]) per i luoghi all'aperto con un campo 'ground' (patibolo e mercato hanno ground='selciato'), e compose.draw_bridge disegna un add_pattern analogo per l'impalcato del ponte (palette.floors['ponte']). add_pattern usa di default color='ffffffff' (opaco). Il campo LandmarkKind.ground ha gia' un meccanismo documentato per NON disegnare alcun pattern (ground=None, 'lascia il terreno della mappa'): e' la leva naturale per patibolo e mercato. Per i ponti serve l'equivalente in draw_bridge (compose.py), che non ha un LandmarkKind dietro. Non tocca gli altri luoghi all'aperto con ground impostato (cimitero='verde', fiera='terra', giardino='verde'), che Jay non ha menzionato e restano invariati.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Il patibolo non disegna piu' un pattern di pavimentazione proprio: l'area mostra il terreno/pavimento sottostante (la piazza), non un rettangolo di selciato opaco
- [ ] #2 Il mercato non disegna piu' un pattern di pavimentazione proprio: l'area mostra il terreno/pavimento sottostante (la piazza), non un rettangolo di selciato opaco
- [ ] #3 L'impalcato del ponte non disegna piu' un pattern di pavimentazione: l'acqua sottostante resta visibile senza un rettangolo opaco sopra
- [ ] #4 Gli altri luoghi all'aperto con un terreno dichiarato (cimitero, fiera, giardino) restano invariati: continuano a disegnare il loro pattern di terreno come oggi
- [ ] #5 Le mappe di valutazione in generated/ per i tre preset sono rigenerate con seed fissi e superano ddforge validate
- [ ] #6 La suite di test completa passa, golden aggiornati dove il cambio li tocca
- [ ] #7 Gate umano: Jay apre le mappe rigenerate in Dungeondraft e conferma che patibolo, ponti e mercato ora hanno lo sfondo trasparente
<!-- AC:END -->
