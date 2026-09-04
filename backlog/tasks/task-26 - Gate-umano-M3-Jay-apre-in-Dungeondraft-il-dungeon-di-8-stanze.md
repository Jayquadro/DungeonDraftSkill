---
id: TASK-26
title: 'Gate umano M3: Jay apre in Dungeondraft il dungeon di 8 stanze'
status: In Progress
assignee:
  - '@jayquadro'
created_date: '2026-09-03 11:32'
updated_date: '2026-09-04 07:17'
labels: []
milestone: m-3
dependencies:
  - TASK-25
documentation:
  - docs/SPEC.md
priority: high
type: task
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Secondo e ultimo passaggio manuale obbligatorio (SPEC.md §5). Genera un dungeon di 8 stanze validato, poi fermati e chiedi esplicitamente a Jay di aprirlo in Dungeondraft indicando cosa controllare. Le correzioni di orientamento e allineamento emerse qui vanno codificate, non solo documentate.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 A Jay è chiesto esplicitamente di verificare: tutte le stanze sono raggiungibili, le porte sono orientate bene, i pavimenti non sbordano
- [ ] #2 Jay conferma che la mappa è utilizzabile al tavolo senza ritocchi manuali di struttura
- [ ] #3 Ogni difetto segnalato è riprodotto in un test prima di essere corretto
- [ ] #4 Le regole di orientamento e allineamento definitive sono codificate e annotate in docs/format.md
<!-- AC:END -->

## Comments

<!-- COMMENTS:BEGIN -->
author: @claude
created: 2026-09-04 07:17
---
File pronto: generated/dungeon_m3.dungeondraft_map (dungeon di 8 stanze, seed 1337, arredo medium, luci attive; rigenerabile con 'ddforge generate dungeon --template templates/blank_80x80.dungeondraft_map --out generated/dungeon_m3.dungeondraft_map --width 80 --height 80 --rooms 8 --seed 1337 --furnish medium --lights'). Passa la validazione con 2 soli avvisi non bloccanti (DDF102 su una piega di corridoio, limite noto e documentato del validatore, non un difetto della mappa). Include gia la correzione di direction/rotation trovata nel gate di TASK-12. In attesa che Jay lo apra e verifichi: tutte le stanze raggiungibili, porte orientate bene, pavimenti che non sbordano.
---
<!-- COMMENTS:END -->
